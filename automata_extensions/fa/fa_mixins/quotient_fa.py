from __future__ import annotations
from typing import Any, Dict, Set


class QuotientMixin:
    """Quotients gauche et droit d'un langage reconnu par un automate fini par un mot u."""

    def _as_nfa(self):
        from ..nfa import ExtendedNFA

        if isinstance(self, ExtendedNFA):
            return self.copy()

        transitions: Dict[Any, Dict[str, Set[Any]]] = {q: {} for q in self.states}
        for q, trans in self.transitions.items():
            for sym, dst in trans.items():
                if dst is not None:
                    transitions[q][sym] = {dst}

        return ExtendedNFA(
            states=set(self.states),
            input_symbols=set(self.input_symbols),
            transitions=transitions,
            initial_state=self.initial_state,
            final_states=set(self.final_states),
        )

    def _reachable_from(self, nfa, start_states: Set[Any], word: str) -> Set[Any]:
        """Calcule l'ensemble des états atteignables dans `nfa` depuis `start_states` en lisant `word`."""
        current = set(nfa.epsilon_closure_of_set(start_states))
        for sym in word:
            if sym not in nfa.input_symbols:
                raise ValueError(f"Symbole {sym!r} hors de l'alphabet {nfa.input_symbols}.")
            nxt: Set[Any] = set()
            for q in current:
                for t in nfa.transitions.get(q, {}).get(sym, set()):
                    nxt.update(nfa.epsilon_closure(t))
            current = nxt
        return current

    def left_quotient_word(self, word: str):
        """
        Quotient à gauche u^{-1}L = { w | u.w in L }.
        Retourne un ExtendedNFA.
        """
        from ..nfa import ExtendedNFA

        nfa = self._as_nfa()
        reached = self._reachable_from(nfa, {nfa.initial_state}, word)

        q_start = ("LQ", "start")
        while q_start in nfa.states:
            q_start = ("LQ", q_start)

        new_states = set(nfa.states) | {q_start}
        new_transitions: Dict[Any, Dict[str, Set[Any]]] = {q: {} for q in new_states}
        for q, trans in nfa.transitions.items():
            for sym, dsts in trans.items():
                if dsts:
                    new_transitions[q][sym] = set(dsts)

        if reached:
            new_transitions[q_start][""] = set(reached)

        return ExtendedNFA(
            states=new_states,
            input_symbols=set(nfa.input_symbols),
            transitions=new_transitions,
            initial_state=q_start,
            final_states=set(nfa.final_states),
        )

    def right_quotient_word(self, word: str):
        """
        Quotient à droite L.u^{-1} = { w | w.u in L }.
        Un état q devient final ssi lire `word` depuis q permet d'atteindre un état final.
        Retourne un ExtendedNFA.
        """
        from ..nfa import ExtendedNFA

        nfa = self._as_nfa()
        new_finals = {
            q
            for q in nfa.states
            if not self._reachable_from(nfa, {q}, word).isdisjoint(nfa.final_states)
        }

        return ExtendedNFA(
            states=set(nfa.states),
            input_symbols=set(nfa.input_symbols),
            transitions={
                q: {sym: set(dsts) for sym, dsts in trans.items() if dsts}
                for q, trans in nfa.transitions.items()
            },
            initial_state=nfa.initial_state,
            final_states=new_finals,
        )