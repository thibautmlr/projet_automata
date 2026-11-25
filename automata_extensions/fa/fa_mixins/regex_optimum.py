from __future__ import annotations
from itertools import permutations
from typing import Any, Dict, List


class RegexOptimumMixin:
    """Conversion en expression régulière avec choix d'ordre d'élimination minimisant la taille."""

    @staticmethod
    def _elimination_cost(node: Any, labels: Dict[Any, Dict[Any, str]]) -> tuple:
        in_edges = [
            expr for src, out in labels.items() if src != node for dst, expr in out.items() if dst == node
        ]
        out_edges = [
            expr for dst, expr in labels[node].items() if dst != node
        ]
        loop_len = len(labels[node].get(node, ""))
        degree_prod = len(in_edges) * len(out_edges)
        expr_weight = sum(len(e) for e in in_edges) + sum(len(e) for e in out_edges) + loop_len
        return (degree_prod, expr_weight, str(node))

    def _greedy_elimination_order(self) -> List[Any]:
        built = self._build_gnfa_graph()
        if built is None:
            return []
        q_start, q_accept, active_states, labels = built
        to_remove = list(active_states)
        remaining = [q_start, *to_remove, q_accept]
        order: List[Any] = []
        while to_remove:
            best = min(to_remove, key=lambda st: self._elimination_cost(st, labels))
            order.append(best)
            self._eliminate_gnfa_node(best, remaining, labels)
            remaining.remove(best)
            to_remove.remove(best)
        return order

    def to_regex_optimum(self) -> str:
        """
        Convertit l'automate en expression régulière en testant l'heuristique gloutonne
        (et plusieurs ordres d'élimination pour les petits automates) pour obtenir
        l'expression la plus courte.
        """
        built = self._build_gnfa_graph()
        if built is None:
            return "∅"

        _, _, active_states, _ = built
        candidates: List[str] = [
            self.to_regex(),
            self.to_regex(elimination_order=self._greedy_elimination_order()),
        ]

        if len(active_states) <= 5:
            for perm in permutations(sorted(active_states, key=str)):
                candidates.append(self.to_regex(elimination_order=perm))

        return min(candidates, key=len)

    def to_regex_arden_optimum(self) -> str:
        """
        Convertit l'automate en expression régulière via le lemme d'Arden en testant
        plusieurs ordres d'élimination des variables et en retenant l'expression la plus courte.
        """
        if not self.final_states:
            return "∅"

        non_init = sorted((q for q in self.states if q != self.initial_state), key=str)
        greedy = [q for q in self._greedy_elimination_order() if q != self.initial_state]

        candidates: List[str] = [
            self.to_regex_arden(),
            self.to_regex_arden(elimination_order=greedy),
        ]

        if len(non_init) <= 5:
            for perm in permutations(non_init):
                candidates.append(self.to_regex_arden(elimination_order=perm))

        return min(candidates, key=len)