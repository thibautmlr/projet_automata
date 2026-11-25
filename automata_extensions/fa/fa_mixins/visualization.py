from __future__ import annotations
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union


def _format_state_label(state: Any) -> str:
    """Formate lisiblement un nom d'état (chaîne, frozenset, tuple, etc.)."""
    if isinstance(state, frozenset):
        if not state:
            return "∅"
        items = ", ".join(sorted((_format_state_label(s) for s in state), key=str))
        return f"{{{items}}}"
    if isinstance(state, tuple):
        return "(" + ", ".join(_format_state_label(s) for s in state) + ")"
    return str(state)


def _escape_dot(text: str) -> str:
    """Échappe les guillemets et antislashs pour le format Graphviz DOT."""
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _escape_tex(text: str) -> str:
    """Échappe les caractères spéciaux LaTeX tout en préservant les symboles mathématiques."""
    replacements = {
        "{": r"\{",
        "}": r"\}",
        "_": r"\_",
        "&": r"\&",
        "%": r"\%",
        "#": r"\#",
        "ε": r"$\varepsilon$",
        "∅": r"$\emptyset$",
        "⊥": r"$\bot$",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


class VisualizationMixin:
    """Export de l'automate en formats DOT, TikZ, LaTeX autonome, SVG, PNG et PDF."""

    def _grouped_edges(self) -> List[Tuple[Any, Any, List[str]]]:
        """Regroupe les symboles de transitions partageant la même paire (source, cible)."""
        from automata.fa.nfa import NFA

        is_nfa = isinstance(self, NFA)
        edge_symbols: Dict[Tuple[Any, Any], Set[str]] = {}

        for u, trans in self.transitions.items():
            for sym, target in trans.items():
                label = "ε" if sym == "" else str(sym)
                if is_nfa:
                    for v in target:
                        edge_symbols.setdefault((u, v), set()).add(label)
                elif target is not None:
                    edge_symbols.setdefault((u, target), set()).add(label)

        ordered_edges: List[Tuple[Any, Any, List[str]]] = []
        for (u, v) in sorted(edge_symbols.keys(), key=lambda pair: (str(pair[0]), str(pair[1]))):
            syms = sorted(edge_symbols[(u, v)], key=lambda s: (s == "ε", s))
            ordered_edges.append((u, v, syms))
        return ordered_edges

    def to_dot(
        self,
        rankdir: str = "LR",
        highlight_states: Optional[Iterable[Any]] = None,
        highlight_edges: Optional[Iterable[Tuple[Any, Any]]] = None,
    ) -> str:
        """
        Génère la représentation Graphviz DOT de l'automate.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        hi_states = set(highlight_states) if highlight_states is not None else set()
        hi_edges = set(highlight_edges) if highlight_edges is not None else set()

        ordered_states = [self.initial_state] + sorted(
            (q for q in self.states if q != self.initial_state),
            key=str,
        )
        node_ids = {q: f"s{i}" for i, q in enumerate(ordered_states)}

        lines: List[str] = [
            "digraph Automaton {",
            f'    rankdir="{_escape_dot(rankdir)}";',
            '    node [fontname="Helvetica", fontsize=11];',
            '    edge [fontname="Helvetica", fontsize=10];',
            '    __start__ [shape=point, width=0.15];',
        ]

        for q in ordered_states:
            nid = node_ids[q]
            shape = "doublecircle" if q in self.final_states else "circle"
            label = _escape_dot(_format_state_label(q))
            attrs = [f'label="{label}"', f"shape={shape}"]
            if q in hi_states:
                attrs.append('style=filled')
                attrs.append('fillcolor="#ffe082"')
            lines.append(f"    {nid} [{', '.join(attrs)}];")

        lines.append(f"    __start__ -> {node_ids[self.initial_state]};")

        for u, v, syms in self._grouped_edges():
            edge_label = _escape_dot(",".join(syms))
            attrs = [f'label="{edge_label}"']
            if (u, v) in hi_edges:
                attrs.append('color="#d32f2f"')
                attrs.append("penwidth=2.0")
            lines.append(f"    {node_ids[u]} -> {node_ids[v]} [{', '.join(attrs)}];")

        lines.append("}")
        return "\n".join(lines)

    def dot(self, **kwargs) -> str:
        """Alias de to_dot()."""
        return self.to_dot(**kwargs)

    def to_tikz(self, radius: float = 2.8) -> str:
        """
        Génère le code LaTeX TikZ représentant l'automate
        (nécessite \\usetikzlibrary{automata, positioning, arrows.meta}).

        Complexity
        ----------
        O(|Q| + |E|)
        """
        ordered_states = [self.initial_state] + sorted(
            (q for q in self.states if q != self.initial_state),
            key=str,
        )
        n = len(ordered_states)
        node_ids = {q: f"q{i}" for i, q in enumerate(ordered_states)}

        lines: List[str] = [
            r"\begin{tikzpicture}[->, >=Stealth, shorten >=1pt, auto, thick]",
        ]

        for i, q in enumerate(ordered_states):
            nid = node_ids[q]
            opts = ["state"]
            if q == self.initial_state:
                opts.append("initial")
            if q in self.final_states:
                opts.append("accepting")

            if n == 1:
                x, y = 0.0, 0.0
            else:
                angle = math.pi - (2.0 * math.pi * i / n)
                x = round(radius * math.cos(angle), 2)
                y = round(radius * math.sin(angle), 2)

            label = _escape_tex(_format_state_label(q))
            lines.append(
                f"    \\node[{', '.join(opts)}] ({nid}) at ({x}, {y}) {{{label}}};"
            )

        edges = self._grouped_edges()
        edge_pairs = {(u, v) for u, v, _ in edges}

        if edges:
            lines.append(r"    \path")
            for idx, (u, v, syms) in enumerate(edges):
                uid, vid = node_ids[u], node_ids[v]
                lbl = _escape_tex(",".join(syms))
                if u == v:
                    edge_opt = "loop above"
                elif (v, u) in edge_pairs:
                    edge_opt = "bend left=18"
                else:
                    edge_opt = ""
                opt_str = f"[{edge_opt}]" if edge_opt else ""
                end_char = ";" if idx == len(edges) - 1 else ""
                lines.append(
                    f"        ({uid}) edge{opt_str} node {{{lbl}}} ({vid}){end_char}"
                )

        lines.append(r"\end{tikzpicture}")
        return "\n".join(lines)

    def tikz(self, radius: float = 2.8) -> str:
        """Alias de to_tikz()."""
        return self.to_tikz(radius=radius)

    def to_latex(self, radius: float = 2.8) -> str:
        """Génère un document LaTeX autonome compilable contenant la figure TikZ."""
        return "\n".join([
            r"\documentclass[tikz,border=4pt]{standalone}",
            r"\usepackage{tikz}",
            r"\usetikzlibrary{automata, positioning, arrows.meta}",
            r"\begin{document}",
            self.to_tikz(radius=radius),
            r"\end{document}",
        ])

    def latex(self, radius: float = 2.8) -> str:
        """Alias de to_latex()."""
        return self.to_latex(radius=radius)

    def latex_tikz(self, radius: float = 2.8) -> str:
        """Alias de to_tikz()."""
        return self.to_tikz(radius=radius)

    @staticmethod
    def _find_graphviz_bin(prog: str = "dot") -> str:
        """Localise le binaire Graphviz (PATH système ou environnement Python/Conda actif)."""
        found = shutil.which(prog)
        if found:
            return found

        env_root = Path(sys.executable).parent
        exe_name = f"{prog}.exe" if sys.platform.startswith("win") else prog
        candidates = [
            env_root / "Library" / "bin" / exe_name,
            env_root / "bin" / exe_name,
            Path(r"C:\Program Files\Graphviz\bin") / exe_name,
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)

        raise FileNotFoundError(
            f"Binaire Graphviz '{prog}' introuvable. Installez Graphviz et ajoutez-le au PATH."
        )

    def _render_graphviz(
        self,
        fmt: str,
        filename: Optional[Union[str, os.PathLike]] = None,
        prog: str = "dot",
    ) -> bytes:
        """Rend l'automate via le binaire Graphviz en sous-processus."""
        graphviz_bin = self._find_graphviz_bin(prog)
        dot_source = self.to_dot().encode("utf-8")

        result = subprocess.run(
            [graphviz_bin, f"-T{fmt}"],
            input=dot_source,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            err = result.stderr.decode("utf-8", errors="replace")
            raise RuntimeError(f"Échec du rendu Graphviz ({fmt}) :\n{err}")

        if filename is not None:
            Path(filename).write_bytes(result.stdout)

        return result.stdout

    def to_svg(self, filename: Optional[Union[str, os.PathLike]] = None) -> str:
        """Exporte l'automate au format SVG (retourne le code XML SVG et écrit le fichier si précisé)."""
        raw = self._render_graphviz("svg", filename=filename)
        return raw.decode("utf-8")

    def svg(self, filename: Optional[Union[str, os.PathLike]] = None) -> str:
        """Alias de to_svg()."""
        return self.to_svg(filename=filename)

    def to_png(self, filename: Optional[Union[str, os.PathLike]] = None) -> bytes:
        """Exporte l'automate au format PNG (retourne les octets PNG et écrit le fichier si précisé)."""
        return self._render_graphviz("png", filename=filename)

    def png(self, filename: Optional[Union[str, os.PathLike]] = None) -> bytes:
        """Alias de to_png()."""
        return self.to_png(filename=filename)

    def to_pdf(self, filename: Optional[Union[str, os.PathLike]] = None) -> bytes:
        """Exporte l'automate au format PDF (retourne les octets PDF et écrit le fichier si précisé)."""
        return self._render_graphviz("pdf", filename=filename)

    def pdf(self, filename: Optional[Union[str, os.PathLike]] = None) -> bytes:
        """Alias de to_pdf()."""
        return self.to_pdf(filename=filename)

    def display(self):
        """Affiche le diagramme SVG dans un notebook Jupyter, ou retourne le DOT en console."""
        try:
            from IPython.display import SVG, display as ipy_display
            svg_code = self.to_svg()
            ipy_display(SVG(svg_code))
            return svg_code
        except Exception:
            dot_code = self.to_dot()
            print(dot_code)
            return dot_code