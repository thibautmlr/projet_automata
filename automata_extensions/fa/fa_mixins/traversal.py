"""Mixin de parcours de graphe (DFS itératif/récursif et BFS) sur les automates finis."""

from __future__ import annotations

from collections import deque
from typing import Any, Deque, Dict, List, Optional, Set


class TraversalMixin:
    """
    Fournit les algorithmes classiques de parcours en profondeur (DFS) et en largeur (BFS).

    Les méthodes utilisent une pile explicite (DFS itératif), la pile d'appels (DFS récursif)
    ou une file FIFO (BFS), avec un ordonnancement déterministe des voisins.
    """

    def dfs_iterative(self, start: Optional[Any] = None) -> List[Any]:
        """
        Effectue un parcours en profondeur (DFS) itératif à l'aide d'une pile.

        Parameters
        ----------
        start : Optional[Any], default=None
            État de départ du parcours. Si ``None``, utilise ``self.initial_state``.

        Returns
        -------
        List[Any]
            Liste des états visités dans l'ordre de découverte.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Cormen, Leiserson, Rivest & Stein, Introduction to Algorithms (DFS).
        """
        origin = self.initial_state if start is None else start  # type: ignore[attr-defined]
        self._validate_state_exists(origin)  # type: ignore[attr-defined]

        adj: Dict[Any, Set[Any]] = self._adjacency_list()  # type: ignore[attr-defined]
        visited: Set[Any] = set()
        order: List[Any] = []
        stack: List[Any] = [origin]

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            order.append(current)

            # Empile en ordre inverse pour dépiler dans l'ordre lexicographique croissant
            neighbors = self._sorted_states(adj[current])  # type: ignore[attr-defined]
            for neighbor in reversed(neighbors):
                if neighbor not in visited:
                    stack.append(neighbor)

        return order

    def dfs_recursive(self, start: Optional[Any] = None) -> List[Any]:
        """
        Effectue un parcours en profondeur (DFS) récursif.

        Parameters
        ----------
        start : Optional[Any], default=None
            État de départ du parcours. Si ``None``, utilise ``self.initial_state``.

        Returns
        -------
        List[Any]
            Liste des états visités dans l'ordre de découverte.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Cormen, Leiserson, Rivest & Stein, Introduction to Algorithms (DFS).
        """
        origin = self.initial_state if start is None else start  # type: ignore[attr-defined]
        self._validate_state_exists(origin)  # type: ignore[attr-defined]

        adj: Dict[Any, Set[Any]] = self._adjacency_list()  # type: ignore[attr-defined]
        visited: Set[Any] = set()
        order: List[Any] = []

        def _visit(node: Any) -> None:
            visited.add(node)
            order.append(node)
            for neighbor in self._sorted_states(adj[node]):  # type: ignore[attr-defined]
                if neighbor not in visited:
                    _visit(neighbor)

        _visit(origin)
        return order

    def dfs(self, start: Optional[Any] = None, recursive: bool = False) -> List[Any]:
        """
        Effectue un parcours en profondeur (DFS) depuis un état donné (itératif par défaut).

        Parameters
        ----------
        start : Optional[Any], default=None
            État de départ du parcours. Si ``None``, utilise ``self.initial_state``.
        recursive : bool, default=False
            Si ``True``, utilise la version récursive ; sinon utilise la version itérative.

        Returns
        -------
        List[Any]
            Liste des états visités dans l'ordre de découverte.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        if recursive:
            return self.dfs_recursive(start=start)
        return self.dfs_iterative(start=start)

    def bfs(self, start: Optional[Any] = None) -> List[Any]:
        """
        Effectue un parcours en largeur (BFS) par niveaux à l'aide d'une file.

        Parameters
        ----------
        start : Optional[Any], default=None
            État de départ du parcours. Si ``None``, utilise ``self.initial_state``.

        Returns
        -------
        List[Any]
            Liste des états visités par distance croissante depuis ``start``.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Cormen, Leiserson, Rivest & Stein, Introduction to Algorithms (BFS).
        """
        origin = self.initial_state if start is None else start  # type: ignore[attr-defined]
        self._validate_state_exists(origin)  # type: ignore[attr-defined]

        adj: Dict[Any, Set[Any]] = self._adjacency_list()  # type: ignore[attr-defined]
        visited: Set[Any] = {origin}
        order: List[Any] = []
        queue: Deque[Any] = deque([origin])

        while queue:
            current = queue.popleft()
            order.append(current)

            for neighbor in self._sorted_states(adj[current]):  # type: ignore[attr-defined]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return order