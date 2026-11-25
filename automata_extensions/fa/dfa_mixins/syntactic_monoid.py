from __future__ import annotations
from collections import deque
from typing import Any, Dict, List, Tuple


class SyntacticMonoidMixin:
    """Calcul du monoïde syntaxique d'un langage régulier reconnu par un ExtendedDFA."""

    def syntactic_monoid(self) -> Dict[Tuple[int, ...], str]:
        """
        Calcule le monoïde syntaxique de L(self), représenté comme un dictionnaire
        associant chaque transformation d'états du DFA minimal complet (tuple d'indices)
        à son plus court mot représentant.

        Complexity
        ----------
        O(|M| * |Sigma| * |Q_min|) où |M| <= |Q_min|^|Q_min| est l'ordre du monoïde.
        """
        minimal = self.complete().minimize()

        ordered_states: List[Any] = [minimal.initial_state] + sorted(
            (q for q in minimal.states if q != minimal.initial_state),
            key=str,
        )
        state_idx = {q: i for i, q in enumerate(ordered_states)}
        n = len(ordered_states)

        identity = tuple(range(n))
        generators: List[Tuple[str, Tuple[int, ...]]] = []
        for sym in sorted(minimal.input_symbols):
            trans = tuple(state_idx[minimal.transitions[q][sym]] for q in ordered_states)
            generators.append((sym, trans))

        monoid: Dict[Tuple[int, ...], str] = {identity: ""}
        queue = deque([identity])

        while queue:
            curr = queue.popleft()
            curr_word = monoid[curr]
            for sym, gen in generators:
                composed = tuple(gen[curr[i]] for i in range(n))
                if composed not in monoid:
                    monoid[composed] = f"{curr_word}{sym}"
                    queue.append(composed)

        return monoid