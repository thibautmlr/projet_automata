"""Mixin de décision des relations ensemblistes entre langages réguliers (inclusion, égalité, disjonction)."""

from __future__ import annotations

from collections import deque
from typing import Any, Deque, Optional, Set, Tuple

from automata.fa.dfa import DFA


class InclusionMixin:
    """
    Fournit les algorithmes de décision d'inclusion, d'égalité, de disjonction
    et de recherche de contre-exemple entre deux DFA.
    """

    def is_included_in(self, other: DFA) -> bool:
        """
        Décide l'inclusion de langages ``L(self) ⊆ L(other)``.

        Utilise la caractérisation algébrique : ``L1 ⊆ L2 ⟺ L1 \\ L2 = ∅``.

        Parameters
        ----------
        other : DFA
            Automate supposé contenir ``L(self)``.

        Returns
        -------
        bool
            ``True`` si ``L(self) ⊆ L(other)``, ``False`` sinon.

        Complexity
        ----------
        O(|Q1| · |Q2| · |Σ|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        return bool(self.difference(other).is_empty())  # type: ignore[attr-defined]

    def is_equivalent(self, other: DFA) -> bool:
        """
        Décide l'égalité des langages reconnus ``L(self) = L(other)``.

        Vérifie la double inclusion ``L(self) ⊆ L(other)`` et ``L(other) ⊆ L(self)``.

        Parameters
        ----------
        other : DFA
            Second automate à comparer.

        Returns
        -------
        bool
            ``True`` si ``L(self) == L(other)``, ``False`` sinon.

        Complexity
        ----------
        O(|Q1| · |Q2| · |Σ|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        return bool(self.symmetric_difference(other).is_empty())  # type: ignore[attr-defined]

    def is_disjoint(self, other: DFA) -> bool:
        """
        Décide si les deux langages sont disjoints (``L(self) ∩ L(other) = ∅``).

        Parameters
        ----------
        other : DFA
            Second automate à comparer.

        Returns
        -------
        bool
            ``True`` si aucun mot n'est accepté simultanément par les deux DFA.

        Complexity
        ----------
        O(|Q1| · |Q2| · |Σ|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        return bool(self.intersection(other).is_empty())  # type: ignore[attr-defined]

    def distinguishing_word(self, other: DFA) -> Optional[str]:
        """
        Trouve un mot contre-exemple de longueur minimale distinguant ``L(self)`` et ``L(other)``.

        Effectue un parcours en largeur (BFS) sur le produit synchronisé afin de
        trouver le plus court mot appartenant à ``L(self) △ L(other)``.

        Parameters
        ----------
        other : DFA
            Second automate à comparer.

        Returns
        -------
        Optional[str]
            Un mot ``w`` tel que ``(w ∈ L(self)) != (w ∈ L(other))``, ou ``None``
            si les deux automates reconnaissent exactement le même langage.

        Complexity
        ----------
        O(|Q1| · |Q2| · |Σ|)

        References
        ----------
        Projet automata_extensions, Section 2.5 (Génération de contre-exemples).
        """
        sym_diff = self.symmetric_difference(other)  # type: ignore[attr-defined]
        alphabet = self._sorted_states(sym_diff.input_symbols)  # type: ignore[attr-defined]
        init_state = sym_diff.initial_state
        finals = set(sym_diff.final_states)

        if init_state in finals:
            return ""

        visited: Set[Any] = {init_state}
        queue: Deque[Tuple[Any, str]] = deque([(init_state, "")])

        while queue:
            current, prefix = queue.popleft()
            for symbol in alphabet:
                nxt = sym_diff.transitions[current][symbol]
                word = prefix + str(symbol)
                if nxt in finals:
                    return word
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, word))

        return None