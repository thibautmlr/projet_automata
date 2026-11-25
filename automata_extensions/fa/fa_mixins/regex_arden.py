from __future__ import annotations
from typing import Any, List, Optional, Sequence
from .regex import regex_concat, regex_star, regex_union


class ArdenMixin:
    """Résolution du système d'équations d'états par le lemme d'Arden."""

    def to_regex_arden(self, elimination_order: Optional[Sequence[Any]] = None) -> str:
        """
        Convertit l'automate en expression régulière en résolvant le système d'équations
        X_i = (Union_j A_{i,j} X_j) U B_i via le lemme d'Arden (X = A*B).

        Complexity
        ----------
        O(|Q|^3)
        """
        if not self.final_states:
            return "∅"

        fa = self
        if hasattr(self, "has_epsilon_transitions") and self.has_epsilon_transitions():
            fa = self.remove_epsilon_transitions()

        if elimination_order is not None:
            others = [q for q in elimination_order if q != fa.initial_state and q in fa.states]
            missing = sorted(
                (q for q in fa.states if q != fa.initial_state and q not in set(others)),
                key=str,
            )
            states: List[Any] = [fa.initial_state] + others + missing
        else:
            states = [fa.initial_state] + sorted(
                (q for q in fa.states if q != fa.initial_state), key=str
            )

        idx_map = {q: i for i, q in enumerate(states)}
        n = len(states)

        coeffs: List[List[str]] = [["∅"] * n for _ in range(n)]
        const: List[str] = ["()" if q in fa.final_states else "∅" for q in states]

        for u, trans in fa.transitions.items():
            i = idx_map[u]
            for sym, target in trans.items():
                label = "()" if sym == "" else sym
                if isinstance(target, (set, frozenset)):
                    for v in target:
                        j = idx_map[v]
                        coeffs[i][j] = regex_union(coeffs[i][j], label)
                elif target is not None:
                    j = idx_map[target]
                    coeffs[i][j] = regex_union(coeffs[i][j], label)

        for k in range(n - 1, -1, -1):
            a_kk_star = regex_star(coeffs[k][k])
            coeffs[k][k] = "∅"

            for j in range(k):
                if coeffs[k][j] != "∅":
                    coeffs[k][j] = regex_concat(a_kk_star, coeffs[k][j])
            if const[k] != "∅":
                const[k] = regex_concat(a_kk_star, const[k])

            for i in range(k):
                a_ik = coeffs[i][k]
                if a_ik == "∅":
                    continue
                coeffs[i][k] = "∅"
                for j in range(k):
                    if coeffs[k][j] != "∅":
                        coeffs[i][j] = regex_union(
                            coeffs[i][j], regex_concat(a_ik, coeffs[k][j])
                        )
                if const[k] != "∅":
                    const[i] = regex_union(
                        const[i], regex_concat(a_ik, const[k])
                    )

        return const[0]