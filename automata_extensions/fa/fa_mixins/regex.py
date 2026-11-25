from __future__ import annotations
from typing import Any, Dict, List, Optional, Sequence, Set


def _is_atomic_regex(expr: str) -> bool:
    """Retourne True si `expr` n'a pas besoin de parenthèses supplémentaires sous `*`."""
    if expr in {"()", "∅"}:
        return True
    if len(expr) == 1 and expr not in {"|", "*", "+", "?", "(", ")"}:
        return True
    if expr.startswith("(") and expr.endswith(")"):
        depth = 0
        for idx, ch in enumerate(expr):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0 and idx < len(expr) - 1:
                    return False
        return depth == 0
    return False


def _needs_concat_parens(expr: str) -> bool:
    """Retourne True si `expr` contient un `|` au niveau racine (hors parenthèses)."""
    depth = 0
    for ch in expr:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "|" and depth == 0:
            return True
    return False


def _split_top_union(expr: str) -> List[str]:
    """Découpe `expr` selon les `|` au niveau racine."""
    parts: List[str] = []
    depth = 0
    start = 0
    for idx, ch in enumerate(expr):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "|" and depth == 0:
            parts.append(expr[start:idx])
            start = idx + 1
    parts.append(expr[start:])
    return parts


def regex_union(r1: str, r2: str) -> str:
    """Simplifie l'union r1 | r2."""
    if r1 == "∅":
        return r2
    if r2 == "∅":
        return r1
    if r1 == r2:
        return r1

    seen: Set[str] = set()
    terms: List[str] = []
    for part in _split_top_union(r1) + _split_top_union(r2):
        if part != "∅" and part not in seen:
            seen.add(part)
            terms.append(part)

    if not terms:
        return "∅"
    return "|".join(terms)


def regex_concat(r1: str, r2: str) -> str:
    """Simplifie la concaténation r1 . r2."""
    if r1 == "∅" or r2 == "∅":
        return "∅"
    if r1 == "()":
        return r2
    if r2 == "()":
        return r1

    left = f"({r1})" if _needs_concat_parens(r1) else r1
    right = f"({r2})" if _needs_concat_parens(r2) else r2
    return f"{left}{right}"


def regex_star(r: str) -> str:
    """Simplifie l'étoile de Kleene r*."""
    if r in {"∅", "()"}:
        return "()"
    if r.endswith("*") and _is_atomic_regex(r[:-1]):
        return r
    if _is_atomic_regex(r):
        return f"{r}*"
    return f"({r})*"


class RegexMixin:
    """Conversion d'un automate fini vers une expression régulière par élimination d'états."""

    def _build_gnfa_graph(self):
        """
        Construit le graphe généralisé normalisé (q_start, q_accept, active_states, labels)
        où labels[u][v] contient l'expression régulière étiquetant l'arc u -> v.
        """
        if not self.final_states:
            return None

        q_start = ("GNFA", "start")
        q_accept = ("GNFA", "accept")
        while q_start in self.states:
            q_start = ("GNFA", q_start)
        while q_accept in self.states or q_accept == q_start:
            q_accept = ("GNFA", q_accept)

        active_states = list(self.states)
        labels: Dict[Any, Dict[Any, str]] = {
            q: {} for q in [q_start, q_accept, *active_states]
        }

        def add_label(u: Any, v: Any, expr: str) -> None:
            if expr == "∅":
                return
            if v in labels[u]:
                labels[u][v] = regex_union(labels[u][v], expr)
            else:
                labels[u][v] = expr

        add_label(q_start, self.initial_state, "()")
        for f in self.final_states:
            add_label(f, q_accept, "()")

        for u, trans in self.transitions.items():
            for sym, target in trans.items():
                expr = "()" if sym == "" else sym
                if isinstance(target, (set, frozenset)):
                    for v in target:
                        add_label(u, v, expr)
                elif target is not None:
                    add_label(u, target, expr)

        return q_start, q_accept, active_states, labels

    @staticmethod
    def _eliminate_gnfa_node(
        node: Any,
        all_nodes: List[Any],
        labels: Dict[Any, Dict[Any, str]],
    ) -> None:
        """Élimine un nœud intermédiaire du GNFA en mettant à jour les arcs (p, r)."""
        loop_star = regex_star(labels[node].get(node, "∅"))

        preds = [p for p in all_nodes if p != node and node in labels[p]]
        succs = [r for r in all_nodes if r != node and r in labels[node]]

        for p in preds:
            in_expr = labels[p][node]
            for r in succs:
                out_expr = labels[node][r]
                via = regex_concat(regex_concat(in_expr, loop_star), out_expr)
                if via != "∅":
                    if r in labels[p]:
                        labels[p][r] = regex_union(labels[p][r], via)
                    else:
                        labels[p][r] = via

        for p in preds:
            del labels[p][node]
        del labels[node]

    def to_regex(self, elimination_order: Optional[Sequence[Any]] = None) -> str:
        """
        Convertit l'automate en expression régulière par élimination des états.

        Complexity
        ----------
        O(|Q|^3) opérations sur les expressions régulières.
        """
        from automata.fa.gnfa import GNFA

        if isinstance(self, GNFA) and elimination_order is None:
            return GNFA.to_regex(self)

        built = self._build_gnfa_graph()
        if built is None:
            return "∅"

        q_start, q_accept, active_states, labels = built

        if elimination_order is not None:
            order = list(elimination_order)
            if set(order) != set(active_states) or len(order) != len(active_states):
                raise ValueError("elimination_order doit contenir exactement tous les états de l'automate.")
        else:
            order = sorted(active_states, key=str)

        remaining = [q_start, *order, q_accept]
        for node in order:
            self._eliminate_gnfa_node(node, remaining, labels)
            remaining.remove(node)

        return labels[q_start].get(q_accept, "∅")