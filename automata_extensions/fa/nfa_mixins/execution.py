"""Mixin de trace d'exécution pas à pas sur un automate fini non déterministe."""

from __future__ import annotations

from collections import deque
from typing import Any, Deque, FrozenSet, Iterable, List, Set, Tuple

from automata.base.exceptions import RejectionException


class NFAExecutionMixin:
    """
    Fournit la trace des ensembles d'états actifs lors de la lecture d'un mot sur un ``ExtendedNFA``.
    """

    def _epsilon_closure_states(self, states: Iterable[Any]) -> FrozenSet[Any]:
        """
        Calcule la fermeture epsilon d'un ensemble d'états.

        Parameters
        ----------
        states : Iterable[Any]
            États de départ.

        Returns
        -------
        FrozenSet[Any]
            Ensemble des états atteignables par zéro ou plusieurs transitions ``""``.
        """
        closure: Set[Any] = set(states)
        queue: Deque[Any] = deque(closure)
        transitions = self.transitions  # type: ignore[attr-defined]

        while queue:
            current = queue.popleft()
            eps_targets = transitions.get(current, {}).get("", set())
            for target in eps_targets:
                if target not in closure:
                    closure.add(target)
                    queue.append(target)

        return frozenset(closure)

    def execution_trace(
        self,
        word: str,
    ) -> List[Tuple[FrozenSet[Any], str, FrozenSet[Any]]]:
        """
        Calcule la suite des ensembles d'états actifs ``(S_i, a_i, S_{i+1})``
        lors de la lecture du mot ``word`` sur l'automate non déterministe.

        Parameters
        ----------
        word : str
            Mot d'entrée à simuler.

        Returns
        -------
        List[Tuple[FrozenSet[Any], str, FrozenSet[Any]]]
            Liste des triplets ``(états_actifs_avant, symbole, états_actifs_après)``
            après fermeture epsilon à chaque étape.

        Raises
        ------
        RejectionException
            Si un symbole n'appartient pas à ``self.input_symbols``.

        Complexity
        ----------
        O(|word| · (|Q| + |E|))

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        alphabet = self.input_symbols  # type: ignore[attr-defined]
        transitions = self.transitions  # type: ignore[attr-defined]
        current_set = self._epsilon_closure_states([self.initial_state])  # type: ignore[attr-defined]
        trace: List[Tuple[FrozenSet[Any], str, FrozenSet[Any]]] = []

        for symbol in word:
            if symbol not in alphabet:
                raise RejectionException(
                    f"Le symbole {symbol!r} n'appartient pas à l'alphabet {alphabet!r}."
                )
            direct_next: Set[Any] = set()
            for state in current_set:
                direct_next.update(transitions.get(state, {}).get(symbol, set()))
            next_set = self._epsilon_closure_states(direct_next)
            trace.append((current_set, symbol, next_set))
            current_set = next_set

        return trace