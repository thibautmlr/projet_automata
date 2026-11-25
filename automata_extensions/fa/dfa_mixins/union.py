"""Mixin d'union par produit synchronisé sur les automates finis déterministes."""

from __future__ import annotations

from typing import Any

from automata.fa.dfa import DFA


class UnionMixin:
    """
    Fournit l'union de deux langages réguliers directement sous forme d'``ExtendedDFA``
    par produit cartésien synchronisé.
    """

    def union(self, other: DFA) -> Any:
        """
        Construit l'automate déterministe reconnaissant l'union ``L(self) ∪ L(other)``.

        Parameters
        ----------
        other : DFA
            Second automate fini déterministe sur le même alphabet.

        Returns
        -------
        ExtendedDFA
            Automate produit acceptant les mots reconnus par au moins l'un des deux DFA.

        Complexity
        ----------
        O(|Q1| · |Q2| · |Σ|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        other_ext = self._validate_compatible_dfa(other)  # type: ignore[attr-defined]
        dfa1 = self.complete()  # type: ignore[attr-defined]
        dfa2 = other_ext.complete()  # type: ignore[attr-defined]
        f1 = set(dfa1.final_states)
        f2 = set(dfa2.final_states)
        return dfa1.product(dfa2, is_final=lambda s1, s2: (s1 in f1) or (s2 in f2))