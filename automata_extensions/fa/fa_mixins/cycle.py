"""Mixin de détection de cycles et de décision des langages vide et fini/infini."""

from __future__ import annotations

from typing import Any, Dict, List, Set


class CycleMixin:
    """
    Fournit la détection de cycles dans le graphe de transition et la décision
    des problèmes classiques du langage vide et du langage fini/infini.
    """

    def _has_cycle_in_subgraph(
        self,
        allowed_states: Set[Any],
        start_states: List[Any],
    ) -> bool:
        """
        Détecte l'existence d'un cycle dans le sous-graphe induit par ``allowed_states``.

        Utilise un parcours en profondeur tricolore (0 = non visité, 1 = en cours
        d'exploration sur la pile courante, 2 = exploration terminée). La présence
        d'un arc vers un sommet gris (y compris une boucle ``u -> u``) caractérise
        un cycle.

        Parameters
        ----------
        allowed_states : Set[Any]
            Ensemble des sommets autorisés.
        start_states : List[Any]
            Sommets depuis lesquels lancer l'exploration.

        Returns
        -------
        bool
            ``True`` si un cycle est détecté, ``False`` sinon.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        adj: Dict[Any, Set[Any]] = self._adjacency_list()  # type: ignore[attr-defined]
        color: Dict[Any, int] = {s: 0 for s in allowed_states}

        def _dfs_cycle(node: Any) -> bool:
            color[node] = 1
            for neighbor in self._sorted_states(adj[node] & allowed_states):  # type: ignore[attr-defined]
                if color[neighbor] == 1:
                    return True
                if color[neighbor] == 0 and _dfs_cycle(neighbor):
                    return True
            color[node] = 2
            return False

        for state in start_states:
            if state in allowed_states and color[state] == 0:
                if _dfs_cycle(state):
                    return True
        return False

    def has_cycle_from(self, state: Any) -> bool:
        """
        Teste s'il existe un cycle atteignable à partir d'un état donné.

        Parameters
        ----------
        state : Any
            État de départ de la recherche de cycle.

        Returns
        -------
        bool
            ``True`` s'il existe un cycle dans le sous-graphe accessible depuis ``state``,
            ``False`` sinon.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Cormen, Leiserson, Rivest & Stein, Introduction to Algorithms (Détection de cycles).
        """
        self._validate_state_exists(state)  # type: ignore[attr-defined]
        reachable: Set[Any] = self.reachable_states(state)  # type: ignore[attr-defined]
        return self._has_cycle_in_subgraph(allowed_states=reachable, start_states=[state])

    def has_cycle(self) -> bool:
        """
        Teste s'il existe au moins un cycle dans le graphe de transition de l'automate.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            ``True`` si le graphe de transition contient un cycle, ``False`` sinon.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Cormen, Leiserson, Rivest & Stein, Introduction to Algorithms (Détection de cycles).
        """
        all_states: Set[Any] = set(self.states)  # type: ignore[attr-defined]
        ordered: List[Any] = self._sorted_states(all_states)  # type: ignore[attr-defined]
        return self._has_cycle_in_subgraph(allowed_states=all_states, start_states=ordered)

    def is_empty(self) -> bool:
        """
        Décide si le langage reconnu par l'automate est vide (``L(A) = ∅``).

        Un automate reconnaît le langage vide si et seulement si aucun état accepteur
        n'est accessible depuis l'état initial.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            ``True`` si ``L(A) = ∅``, ``False`` sinon.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        accessible: Set[Any] = self.accessible_states()  # type: ignore[attr-defined]
        finals: Set[Any] = set(self._get_final_states())  # type: ignore[attr-defined]
        return len(accessible & finals) == 0

    def is_finite(self) -> bool:
        """
        Décide si le langage reconnu par l'automate est fini (``|L(A)| < ∞``).

        Le langage reconnu est infini si et seulement s'il existe, dans le sous-automate
        émondé (restreint aux états utiles), un cycle contenant au moins une transition
        consommant un symbole non vide (``label != ""``). La vérification via les CFC
        de l'automate émondé écarte ainsi correctement les cycles purement composés de
        transitions epsilon.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            ``True`` si ``L(A)`` est fini, ``False`` si ``L(A)`` est infini.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        useful: Set[Any] = self.useful_states()  # type: ignore[attr-defined]
        if not useful:
            return True

        trimmed = self.induced_subautomaton(useful)  # type: ignore[attr-defined]
        sccs = trimmed.strongly_connected_components()
        state_to_scc: Dict[Any, int] = {}
        for idx, comp in enumerate(sccs):
            for st in comp:
                state_to_scc[st] = idx

        # Un cycle contenant un arc non-epsilon existe ssi un arc (u, a, v) avec a != ""
        # relie deux états de la même composante fortement connexe du graphe utile.
        for src, label, dst in trimmed._iter_transitions_edges():  # type: ignore[attr-defined]
            if label != "" and state_to_scc[src] == state_to_scc[dst]:
                return False

        return True

    def is_infinite(self) -> bool:
        """
        Décide si le langage reconnu par l'automate est infini (``|L(A)| = ∞``).

        Parameters
        ----------
        None

        Returns
        -------
        bool
            ``True`` si ``L(A)`` est infini, ``False`` sinon.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        return not self.is_finite()