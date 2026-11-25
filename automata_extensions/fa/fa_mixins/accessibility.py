"""Mixin d'accessibilité, coaccessibilité, états utiles et émondage (trim)."""

from __future__ import annotations

from collections import deque
from typing import Any, Deque, Dict, Set


class AccessibilityMixin:
    """
    Fournit les algorithmes d'analyse d'accessibilité et d'émondage d'un automate fini.

    Toutes les méthodes préservent l'immutabilité de ``self`` : ``trim()`` retourne
    une nouvelle instance restreinte aux états utiles.
    """

    def reachable_states(self, state: Any) -> Set[Any]:
        """
        Calcule l'ensemble des états atteignables depuis un état donné.

        Parameters
        ----------
        state : Any
            État de départ.

        Returns
        -------
        Set[Any]
            Ensemble des états accessibles à partir de ``state`` (incluant ``state``).

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        return set(self.bfs(start=state))  # type: ignore[attr-defined]

    def accessible_states(self) -> Set[Any]:
        """
        Calcule l'ensemble des états accessibles depuis l'état initial ``q0``.

        Un état ``q`` est accessible s'il existe un chemin de ``q0`` vers ``q``.

        Parameters
        ----------
        None

        Returns
        -------
        Set[Any]
            Ensemble des états atteignables depuis ``self.initial_state``.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        return self.reachable_states(self.initial_state)  # type: ignore[attr-defined]

    def is_accessible(self, state: Any) -> bool:
        """
        Teste si un état donné est accessible depuis l'état initial.

        Parameters
        ----------
        state : Any
            État à tester.

        Returns
        -------
        bool
            ``True`` si ``state`` est accessible depuis ``self.initial_state``, ``False`` sinon.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        self._validate_state_exists(state)  # type: ignore[attr-defined]
        return state in self.accessible_states()

    def coaccessible_states(self) -> Set[Any]:
        """
        Calcule l'ensemble des états coaccessibles (pouvant atteindre un état final).

        Effectue un parcours en largeur sur le graphe transposé (arcs inversés)
        à partir de l'ensemble des états accepteurs ``self.final_states``.

        Parameters
        ----------
        None

        Returns
        -------
        Set[Any]
            Ensemble des états depuis lesquels au moins un état final est atteignable.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Sakarovitch, Éléments de théorie des automates.
        """
        final_states: Set[Any] = set(self._get_final_states())  # type: ignore[attr-defined]
        if not final_states:
            return set()

        rev_adj: Dict[Any, Set[Any]] = self._reverse_adjacency_list()  # type: ignore[attr-defined]
        coaccessible: Set[Any] = set(final_states)
        queue: Deque[Any] = deque(final_states)

        while queue:
            current = queue.popleft()
            for pred in rev_adj[current]:
                if pred not in coaccessible:
                    coaccessible.add(pred)
                    queue.append(pred)

        return coaccessible

    def is_coaccessible(self, state: Any) -> bool:
        """
        Teste si un état donné est coaccessible.

        Parameters
        ----------
        state : Any
            État à tester.

        Returns
        -------
        bool
            ``True`` si un état accepteur est atteignable depuis ``state``, ``False`` sinon.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Sakarovitch, Éléments de théorie des automates.
        """
        self._validate_state_exists(state)  # type: ignore[attr-defined]
        return state in self.coaccessible_states()

    def useful_states(self) -> Set[Any]:
        """
        Calcule l'ensemble des états utiles (à la fois accessibles et coaccessibles).

        Parameters
        ----------
        None

        Returns
        -------
        Set[Any]
            Intersection ``accessible_states() ∩ coaccessible_states()``.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Sakarovitch, Éléments de théorie des automates.
        """
        return self.accessible_states() & self.coaccessible_states()

    def is_trim(self) -> bool:
        """
        Teste si l'automate est émondé (tous ses états sont utiles).

        Parameters
        ----------
        None

        Returns
        -------
        bool
            ``True`` si ``useful_states() == set(self.states)``, ``False`` sinon.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Sakarovitch, Éléments de théorie des automates.
        """
        return self.useful_states() == set(self.states)  # type: ignore[attr-defined]

    def trim(self) -> Any:
        """
        Construit un nouvel automate émondé en supprimant tous les états non utiles.

        Si le langage reconnu est vide (aucun état utile, donc l'état initial n'est
        pas coaccessible), retourne un automate minimal contenant uniquement l'état
        initial non accepteur et sans transitions, afin de respecter les invariants
        d'automata-lib.

        Parameters
        ----------
        None

        Returns
        -------
        ExtendedFA
            Nouvelle instance d'automate (du même type que ``self``) restreinte aux
            états utiles, sans modifier ``self``.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        useful = self.useful_states()
        if not useful:
            return self._build_restricted_automaton(  # type: ignore[attr-defined]
                kept_states={self.initial_state},  # type: ignore[attr-defined]
                initial_state=self.initial_state,  # type: ignore[attr-defined]
                final_states=set(),
            )

        return self.induced_subautomaton(useful)  # type: ignore[attr-defined]