"""Mixin de différence et différence symétrique de langages réguliers sur DFA."""

from __future__ import annotations

from typing import Any

from automata.fa.dfa import DFA


class DifferenceMixin:
    """
    Fournit la différence ensembliste ``L(self) \\ L(other)`` et la différence
    symétrique ``L(self) △ L(other)`` par produit synchronisé.
    """

    def difference(self, other: DFA) -> Any:
        """
        Construit l'automate reconnaissant la différence ``L(self) \\ L(other)``.

        Parameters
        ----------
        other : DFA
            Automate à soustraire, sur le même alphabet.

        Returns
        -------
        ExtendedDFA
            Automate reconnaissant les mots de ``L(self)`` n'appartenant pas à ``L(other)``.

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
        return dfa1.product(dfa2, is_final=lambda s1, s2: (s1 in f1) and (s2 not in f2))

    def symmetric_difference(self, other: DFA) -> Any:
        """
        Construit l'automate reconnaissant la différence symétrique ``L(self) △ L(other)``.

        Parameters
        ----------
        other : DFA
            Second automate sur le même alphabet.

        Returns
        -------
        ExtendedDFA
            Automate reconnaissant les mots appartenant à exactement l'un des deux langages.

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
        return dfa1.product(dfa2, is_final=lambda s1, s2: (s1 in f1) != (s2 in f2))