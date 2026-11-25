from __future__ import annotations
from typing import Any, Dict, Set


class GrammarMixin:
    """Conversion bidirectionnelle entre automates finis et grammaires régulières."""

    def to_grammar(self):
        """
        Convertit l'automate fini en une grammaire régulière linéaire droite équivalente.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        from ...grammar.grammar import Grammar

        # Attribution de noms de variables majuscules (un caractère) pour chaque état
        ordered_states = [self.initial_state] + sorted(
            (q for q in self.states if q != self.initial_state),
            key=str,
        )

        # Réserve 'S' pour l'état initial et évite toute collision avec input_symbols
        alphabet_letters = [
            ch for ch in "SABCDEFGHIJKLMNOPQRSTUVWXYZ" if ch not in self.input_symbols
        ]
        if len(ordered_states) > len(alphabet_letters):
            raise ValueError(
                "Trop d'états pour attribuer des symboles non-terminaux d'un caractère."
            )

        var_map: Dict[Any, str] = {
            st: alphabet_letters[i] for i, st in enumerate(ordered_states)
        }
        variables = set(var_map.values())
        terminals = set(self.input_symbols)
        start_symbol = var_map[self.initial_state]
        productions: Dict[str, Set[str]] = {v: set() for v in variables}

        for u, trans in self.transitions.items():
            lhs = var_map[u]
            for sym, target in trans.items():
                if isinstance(target, (set, frozenset)):
                    for v in target:
                        productions[lhs].add(f"{sym}{var_map[v]}")
                elif target is not None:
                    productions[lhs].add(f"{sym}{var_map[target]}")

        for f in self.final_states:
            productions[var_map[f]].add("")

        return Grammar(
            variables=variables,
            terminals=terminals,
            productions=productions,
            start_symbol=start_symbol,
        )

    @classmethod
    def from_grammar(cls, grammar):
        """
        Construit un automate fini (ExtendedNFA ou ExtendedDFA selon `cls`)
        à partir d'une grammaire régulière linéaire droite.
        """
        from ..dfa import ExtendedDFA

        nfa = grammar.to_nfa()
        if issubclass(cls, ExtendedDFA):
            return nfa.to_dfa()
        return nfa