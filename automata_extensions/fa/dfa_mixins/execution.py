"""Mixin de trace d'exécution pas à pas sur un automate fini déterministe."""

from __future__ import annotations

from typing import Any, List, Tuple

from automata.base.exceptions import RejectionException


class ExecutionMixin:
    """
    Fournit le calcul de la trace d'exécution détaillée d'un mot sur un ``ExtendedDFA``.
    """

    def execution_trace(self, word: str) -> List[Tuple[Any, str, Any]]:
        """
        Calcule la suite complète des transitions ``(état, symbole, état_suivant)``
        empruntées lors de la lecture du mot ``word``.

        Parameters
        ----------
        word : str
            Mot d'entrée à simuler.

        Returns
        -------
        List[Tuple[Any, str, Any]]
            Liste ordonnée des triplets ``(q_i, a_i, q_{i+1})`` traversés.
            Retourne ``[]`` pour le mot vide ``""``.

        Raises
        ------
        RejectionException
            Si un symbole n'appartient pas à ``self.input_symbols`` ou si l'automate
            est partiel et qu'aucune transition n'est définie depuis l'état courant.

        Complexity
        ----------
        O(|word|)

        References
        ----------
        Documentation automata_extensions, Section 36.
        """
        current: Any = self.initial_state  # type: ignore[attr-defined]
        alphabet = self.input_symbols  # type: ignore[attr-defined]
        transitions = self.transitions  # type: ignore[attr-defined]
        trace: List[Tuple[Any, str, Any]] = []

        for symbol in word:
            if symbol not in alphabet:
                raise RejectionException(
                    f"Le symbole {symbol!r} n'appartient pas à l'alphabet {alphabet!r}."
                )
            state_transitions = transitions.get(current, {})
            if symbol not in state_transitions or state_transitions[symbol] is None:
                raise RejectionException(
                    f"Aucune transition définie depuis l'état {current!r} pour le symbole {symbol!r}."
                )
            next_state = state_transitions[symbol]
            trace.append((current, symbol, next_state))
            current = next_state

        return trace