from __future__ import annotations
from collections import deque
from typing import Dict, List, Set


class ResidualMixin:
    """Construction de l'automate des résiduels (quotients à gauche u^{-1}L) d'un ExtendedDFA."""

    def residual_automaton(self):
        """
        Construit l'automate déterministe minimal des résiduels u^{-1}L,
        avec des états nommés 'q0', 'q1', ...
        """
        from ..dfa import ExtendedDFA

        minimal = self.complete().minimize()

        init_state = minimal.initial_state
        visited: List[object] = [init_state]
        seen: Set[object] = {init_state}
        queue = deque([init_state])
        raw_trans: Dict[object, Dict[str, object]] = {}

        while queue:
            curr = queue.popleft()
            raw_trans[curr] = {}
            for sym in sorted(minimal.input_symbols):
                nxt = minimal.transitions[curr][sym]
                raw_trans[curr][sym] = nxt
                if nxt not in seen:
                    seen.add(nxt)
                    visited.append(nxt)
                    queue.append(nxt)

        name_map = {st: f"q{i}" for i, st in enumerate(visited)}
        states = set(name_map.values())
        finals = {name_map[st] for st in visited if st in minimal.final_states}
        transitions = {
            name_map[src]: {sym: name_map[dst] for sym, dst in tr.items()}
            for src, tr in raw_trans.items()
        }

        return ExtendedDFA(
            states=states,
            input_symbols=set(minimal.input_symbols),
            transitions=transitions,
            initial_state=name_map[init_state],
            final_states=finals,
        )