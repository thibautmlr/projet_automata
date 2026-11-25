from __future__ import annotations
import html
import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from .visualization import _format_state_label


class AnimationMixin:
    """Simulation pas-à-pas lisible (run) et animation HTML interactive autonome (animate)."""

    def _simulation_steps(self, word: str) -> List[Dict[str, Any]]:
        """
        Calcule la séquence complète des étapes de lecture de `word` sur un DFA ou NFA.
        Chaque élément contient : step, symbol, active_states, accepted.
        """
        from ..nfa import ExtendedNFA

        is_nfa = isinstance(self, ExtendedNFA)
        steps: List[Dict[str, Any]] = []

        if is_nfa:
            current: Set[Any] = set(self.epsilon_closure(self.initial_state))
            steps.append({
                "step": 0,
                "symbol": None,
                "active_states": sorted(current, key=str),
                "accepted": not current.isdisjoint(self.final_states),
            })
            for idx, ch in enumerate(word, start=1):
                if ch not in self.input_symbols:
                    raise ValueError(f"Symbole {ch!r} hors de l'alphabet {self.input_symbols}.")
                nxt: Set[Any] = set()
                for q in current:
                    for t in self.transitions.get(q, {}).get(ch, set()):
                        nxt.update(self.epsilon_closure(t))
                current = nxt
                steps.append({
                    "step": idx,
                    "symbol": ch,
                    "active_states": sorted(current, key=str),
                    "accepted": not current.isdisjoint(self.final_states),
                })
        else:
            curr_state: Optional[Any] = self.initial_state
            steps.append({
                "step": 0,
                "symbol": None,
                "active_states": [curr_state] if curr_state is not None else [],
                "accepted": curr_state in self.final_states,
            })
            for idx, ch in enumerate(word, start=1):
                if ch not in self.input_symbols:
                    raise ValueError(f"Symbole {ch!r} hors de l'alphabet {self.input_symbols}.")
                if curr_state is not None:
                    curr_state = self.transitions.get(curr_state, {}).get(ch)
                steps.append({
                    "step": idx,
                    "symbol": ch,
                    "active_states": [curr_state] if curr_state is not None else [],
                    "accepted": curr_state in self.final_states if curr_state is not None else False,
                })

        return steps

    def run(self, word: str) -> str:
        """
        Exécute l'automate sur `word` et retourne une trace textuelle lisible :
        ex. 'q0 --a--> q1 --b--> q2 (accept)'.

        Complexity
        ----------
        O(|word| * |Q|^2) sur NFA, O(|word|) sur DFA.
        """
        from ..nfa import ExtendedNFA

        is_nfa = isinstance(self, ExtendedNFA)
        steps = self._simulation_steps(word)

        def fmt_step(states_list: List[Any]) -> str:
            if not is_nfa:
                return _format_state_label(states_list[0]) if states_list else "∅"
            if not states_list:
                return "∅"
            return "{" + ", ".join(_format_state_label(s) for s in states_list) + "}"

        parts: List[str] = [fmt_step(steps[0]["active_states"])]
        for st in steps[1:]:
            parts.append(f"--{st['symbol']}--> {fmt_step(st['active_states'])}")

        verdict = "accept" if steps[-1]["accepted"] else "reject"
        return f"{' '.join(parts)} ({verdict})"

    def animate(
        self,
        word: str,
        filename: Optional[Union[str, os.PathLike]] = None,
    ) -> str:
        """
        Génère une page HTML/SVG interactive autonome animant l'exécution de `word`
        étape par étape (contrôles Précédent, Lecture/Pause, Suivant, Réinitialiser).

        Complexity
        ----------
        O(|Q| + |E| + |word| * |Q|^2)
        """
        steps = self._simulation_steps(word)
        ordered_states = [self.initial_state] + sorted(
            (q for q in self.states if q != self.initial_state),
            key=str,
        )
        n = len(ordered_states)
        idx_map = {q: i for i, q in enumerate(ordered_states)}

        cx, cy = 260.0, 190.0
        radius = 125.0 if n > 1 else 0.0
        positions: List[Dict[str, Any]] = []
        for i, q in enumerate(ordered_states):
            angle = math.pi - (2.0 * math.pi * i / max(n, 1))
            positions.append({
                "id": i,
                "label": _format_state_label(q),
                "x": round(cx + radius * math.cos(angle), 1),
                "y": round(cy + radius * math.sin(angle), 1),
                "initial": q == self.initial_state,
                "final": q in self.final_states,
            })

        edges_data: List[Dict[str, Any]] = []
        for u, v, syms in self._grouped_edges():
            edges_data.append({
                "src": idx_map[u],
                "dst": idx_map[v],
                "label": ",".join(syms),
            })

        serialized_steps = [
            {
                "step": st["step"],
                "symbol": st["symbol"],
                "active": [idx_map[q] for q in st["active_states"] if q in idx_map],
                "accepted": st["accepted"],
            }
            for st in steps
        ]

        payload = json.dumps(
            {
                "word": word,
                "nodes": positions,
                "edges": edges_data,
                "steps": serialized_steps,
            },
            ensure_ascii=False,
        )

        safe_word = html.escape(word if word != "" else "ε")
        html_doc = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Animation Automate — mot « {safe_word} »</title>
<style>
  body {{ font-family: system-ui, -apple-system, sans-serif; margin: 20px; background: #fafafa; color: #222; }}
  .panel {{ max-width: 640px; margin: auto; background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 16px; }}
  .controls {{ display: flex; gap: 8px; align-items: center; margin-bottom: 12px; flex-wrap: wrap; }}
  button {{ padding: 6px 12px; border: 1px solid #bbb; border-radius: 4px; background: #f5f5f5; cursor: pointer; }}
  button:hover {{ background: #e8e8e8; }}
  .word-bar {{ font-family: monospace; font-size: 16px; margin: 8px 0; }}
  .char {{ padding: 2px 6px; border-radius: 4px; }}
  .char.done {{ background: #e0f2f1; color: #00695c; }}
  .char.curr {{ background: #ffe082; font-weight: bold; }}
  svg {{ width: 100%; height: 380px; border: 1px solid #eee; border-radius: 6px; background: #fff; }}
  .status {{ margin-top: 10px; font-weight: 600; }}
</style>
</head>
<body>
<div class="panel">
  <h3>Simulation pas-à-pas</h3>
  <div class="controls">
    <button onclick="resetAnim()">⏮ Début</button>
    <button onclick="prevStep()">◀ Précédent</button>
    <button id="playBtn" onclick="togglePlay()">▶ Lecture</button>
    <button onclick="nextStep()">Suivant ▶</button>
    <span id="stepInfo"></span>
  </div>
  <div class="word-bar" id="wordBar"></div>
  <svg id="canvas" viewBox="0 0 520 380"></svg>
  <div class="status" id="statusBar"></div>
</div>
<script>
const DATA = {payload};
let currentStep = 0;
let timer = null;

function render() {{
  const st = DATA.steps[currentStep];
  const activeSet = new Set(st.active);
  document.getElementById("stepInfo").textContent = `Étape ${{currentStep}} / ${{DATA.steps.length - 1}}`;

  const wordBar = document.getElementById("wordBar");
  if (DATA.word.length === 0) {{
    wordBar.innerHTML = 'Mot : <span class="char curr">ε</span>';
  }} else {{
    wordBar.innerHTML = "Mot : " + DATA.word.split("").map((c, i) => {{
      const cls = i < currentStep - 1 ? "char done" : (i === currentStep - 1 ? "char curr" : "char");
      return `<span class="${{cls}}">${{c}}</span>`;
    }}).join("");
  }}

  const svg = document.getElementById("canvas");
  let out = `<defs><marker id="arrow" markerWidth="10" markerHeight="7" refX="26" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#555"/></marker></defs>`;

  DATA.edges.forEach(e => {{
    const u = DATA.nodes[e.src], v = DATA.nodes[e.dst];
    if (e.src === e.dst) {{
      out += `<path d="M ${{u.x - 10}} ${{u.y - 18}} C ${{u.x - 30}} ${{u.y - 60}}, ${{u.x + 30}} ${{u.y - 60}}, ${{u.x + 10}} ${{u.y - 18}}" fill="none" stroke="#555" stroke-width="1.5"/>`;
      out += `<text x="${{u.x}}" y="${{u.y - 52}}" text-anchor="middle" font-size="12">${{e.label}}</text>`;
    }} else {{
      const mx = (u.x + v.x) / 2, my = (u.y + v.y) / 2 - 12;
      out += `<line x1="${{u.x}}" y1="${{u.y}}" x2="${{v.x}}" y2="${{v.y}}" stroke="#555" stroke-width="1.5" marker-end="url(#arrow)"/>`;
      out += `<text x="${{mx}}" y="${{my}}" text-anchor="middle" font-size="12" fill="#111">${{e.label}}</text>`;
    }}
  }});

  DATA.nodes.forEach(n => {{
    const isAct = activeSet.has(n.id);
    const fill = isAct ? "#ffe082" : "#ffffff";
    const stroke = isAct ? "#e65100" : "#333333";
    if (n.initial) {{
      out += `<line x1="${{n.x - 45}}" y1="${{n.y}}" x2="${{n.x - 22}}" y2="${{n.y}}" stroke="#333" stroke-width="2"/>`;
    }}
    out += `<circle cx="${{n.x}}" cy="${{n.y}}" r="21" fill="${{fill}}" stroke="${{stroke}}" stroke-width="2"/>`;
    if (n.final) {{
      out += `<circle cx="${{n.x}}" cy="${{n.y}}" r="16" fill="none" stroke="${{stroke}}" stroke-width="1.5"/>`;
    }}
    out += `<text x="${{n.x}}" y="${{n.y + 4}}" text-anchor="middle" font-size="12" font-weight="bold">${{n.label}}</text>`;
  }});

  svg.innerHTML = out;
  const activeLabels = st.active.map(id => DATA.nodes[id].label).join(", ") || "∅";
  const isEnd = currentStep === DATA.steps.length - 1;
  const verdict = isEnd ? (st.accepted ? " — ACCEPTÉ ✔" : " — REJETÉ ✘") : "";
  document.getElementById("statusBar").textContent = `États actifs : {{${{activeLabels}}}}${{verdict}}`;
}}

function nextStep() {{ if (currentStep < DATA.steps.length - 1) {{ currentStep++; render(); }} else if (timer) {{ togglePlay(); }} }}
function prevStep() {{ if (currentStep > 0) {{ currentStep--; render(); }} }}
function resetAnim() {{ currentStep = 0; render(); }}
function togglePlay() {{
  if (timer) {{ clearInterval(timer); timer = null; document.getElementById("playBtn").textContent = "▶ Lecture"; }}
  else {{ document.getElementById("playBtn").textContent = "⏸ Pause"; timer = setInterval(nextStep, 800); }}
}}
render();
</script>
</body>
</html>"""

        if filename is not None:
            Path(filename).write_text(html_doc, encoding="utf-8")

        return html_doc