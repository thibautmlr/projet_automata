from __future__ import annotations
from typing import Any, Dict, Set, Tuple


class LanguageOperationsMixin:
    """Opérations rationnelles directes (union, concaténation, étoile de Kleene) renvoyant un ExtendedNFA."""

    def _to_tagged_nfa(self, tag: str):
        states = {(tag, q) for q in self.states}
        initial = (tag, self.initial_state)
        finals = {(tag, q) for q in self.final_states}
        transitions: Dict[Tuple[str, Any], Dict[str, Set[Tuple[str, Any]]]] = {
            s: {} for s in states
        }

        for q, trans in self.transitions.items():
            src = (tag, q)
            for sym, target in trans.items():
                if isinstance(target, (set, frozenset)):
                    if target:
                        transitions[src][sym] = {(tag, t) for t in target}
                elif target is not None:
                    transitions[src][sym] = {(tag, target)}

        return states, set(self.input_symbols), transitions, initial, finals

    def union(self, other):
        """Construit un ExtendedNFA reconnaissant L(self) U L(other) via un nouvel état initial."""
        from ..nfa import ExtendedNFA

        s1, sym1, t1, i1, f1 = self._to_tagged_nfa("L")
        s2, sym2, t2, i2, f2 = other._to_tagged_nfa("R")

        q_init = ("U", "start")
        states = s1 | s2 | {q_init}
        transitions: Dict[Any, Dict[str, Set[Any]]] = {q: {} for q in states}
        transitions.update(t1)
        transitions.update(t2)
        transitions[q_init][""] = {i1, i2}

        return ExtendedNFA(
            states=states,
            input_symbols=sym1 | sym2,
            transitions=transitions,
            initial_state=q_init,
            final_states=f1 | f2,
        )

    def concatenation(self, other):
        """Construit un ExtendedNFA reconnaissant L(self) . L(other) par transitions epsilon."""
        from ..nfa import ExtendedNFA

        s1, sym1, t1, i1, f1 = self._to_tagged_nfa("L")
        s2, sym2, t2, i2, f2 = other._to_tagged_nfa("R")

        states = s1 | s2
        transitions: Dict[Any, Dict[str, Set[Any]]] = {q: {} for q in states}
        transitions.update(t1)
        transitions.update(t2)

        for f in f1:
            transitions[f].setdefault("", set()).add(i2)

        return ExtendedNFA(
            states=states,
            input_symbols=sym1 | sym2,
            transitions=transitions,
            initial_state=i1,
            final_states=f2,
        )

    def kleene_star(self):
        """Construit un ExtendedNFA reconnaissant L(self)*."""
        from ..nfa import ExtendedNFA

        s, sym, t, i, f = self._to_tagged_nfa("K")
        q_start = ("K", "start")
        q_accept = ("K", "accept")

        states = s | {q_start, q_accept}
        transitions: Dict[Any, Dict[str, Set[Any]]] = {q: {} for q in states}
        transitions.update(t)

        transitions[q_start][""] = {i, q_accept}
        for fin in f:
            transitions[fin].setdefault("", set()).update({i, q_accept})

        return ExtendedNFA(
            states=states,
            input_symbols=sym,
            transitions=transitions,
            initial_state=q_start,
            final_states={q_accept},
        )