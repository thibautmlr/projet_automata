"""Mixin de reconnaissance de mots sur un automate fini."""

from __future__ import annotations

from automata.fa.gnfa import GNFA
from automata.fa.nfa import NFA


class WordMixin:
    """
    Fournit l'interface pédagogique de reconnaissance de mots sur tout automate fini.
    """

    def accepts(self, word: str) -> bool:
        """
        Teste si un mot ``word`` appartient au langage reconnu par l'automate.

        Alias pédagogique de ``accepts_input(word)`` d'automata-lib, commun à
        ``ExtendedDFA``, ``ExtendedNFA`` et ``ExtendedGNFA``. Pour un ``GNFA``
        (dont ``accepts_input`` lève ``NotImplementedError`` dans automata-lib 9.2.0),
        la reconnaissance passe par l'expression régulière équivalente ``to_regex()``.

        Parameters
        ----------
        word : str
            Mot d'entrée sur ``self.input_symbols`` (``""`` pour le mot vide ε).

        Returns
        -------
        bool
            ``True`` si ``word ∈ L(self)``, ``False`` sinon.

        Complexity
        ----------
        O(|word|) pour un DFA ; O(|Q|² · |word|) pour un NFA.

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        if isinstance(self, GNFA):
            regex_str = self.to_regex()
            nfa = NFA.from_regex(regex_str, input_symbols=self.input_symbols)
            return bool(nfa.accepts_input(word))

        return bool(self.accepts_input(word))  # type: ignore[attr-defined]