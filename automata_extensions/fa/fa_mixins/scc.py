"""Mixin de calcul des composantes fortement connexes (algorithme de Tarjan)."""

from __future__ import annotations

from typing import Any, Dict, FrozenSet, List, Set


class SCCMixin:
    """
    Fournit le calcul des composantes fortement connexes du graphe de transition.

    Utilise l'algorithme linéaire de Tarjan en un seul parcours en profondeur.
    """

    def strongly_connected_components(self) -> List[FrozenSet[Any]]:
        """
        Calcule les composantes fortement connexes (CFC) du graphe de transition.

        Deux états ``u`` et ``v`` appartiennent à la même CFC si et seulement s'il
        existe un chemin de ``u`` vers ``v`` et un chemin de ``v`` vers ``u``.

        Parameters
        ----------
        None

        Returns
        -------
        List[FrozenSet[Any]]
            Liste des composantes fortement connexes sous forme d'ensembles immuables.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Tarjan, Depth-First Search and Linear Graph Algorithms (1972).
        """
        adj: Dict[Any, Set[Any]] = self._adjacency_list()  # type: ignore[attr-defined]
        ordered_states: List[Any] = self._sorted_states(self.states)  # type: ignore[attr-defined]

        index_counter = 0
        indices: Dict[Any, int] = {}
        lowlink: Dict[Any, int] = {}
        stack: List[Any] = []
        on_stack: Set[Any] = set()
        components: List[FrozenSet[Any]] = []

        def _strongconnect(node: Any) -> None:
            nonlocal index_counter
            indices[node] = index_counter
            lowlink[node] = index_counter
            index_counter += 1
            stack.append(node)
            on_stack.add(node)

            for neighbor in self._sorted_states(adj[node]):  # type: ignore[attr-defined]
                if neighbor not in indices:
                    _strongconnect(neighbor)
                    lowlink[node] = min(lowlink[node], lowlink[neighbor])
                elif neighbor in on_stack:
                    lowlink[node] = min(lowlink[node], indices[neighbor])

            if lowlink[node] == indices[node]:
                scc_members: Set[Any] = set()
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    scc_members.add(w)
                    if w == node:
                        break
                components.append(frozenset(scc_members))

        for state in ordered_states:
            if state not in indices:
                _strongconnect(state)

        return components

    def is_strongly_connected(self) -> bool:
        """
        Teste si le graphe de transition de l'automate est fortement connexe.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            ``True`` si tous les états appartiennent à une unique CFC, ``False`` sinon.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Tarjan, Depth-First Search and Linear Graph Algorithms (1972).
        """
        return len(self.strongly_connected_components()) == 1