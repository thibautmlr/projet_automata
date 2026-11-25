"""Mixin d'exploration structurelle du graphe de transition d'un automate fini."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Dict, FrozenSet, Iterator, List, Set, Tuple

from automata.fa.dfa import DFA
from automata.fa.gnfa import GNFA


class GraphMixin:
    """
    Fournit les primitives d'accès au graphe sous-jacent d'un automate fini.

    Ce mixin est pur (aucun ``__init__``, aucun état interne) et ne dépend que
    des attributs ``states``, ``transitions``, ``initial_state`` et ``final_states``.
    """

    def _validate_state_exists(self, state: Any) -> None:
        """
        Vérifie qu'un état appartient bien à ``self.states``.

        Parameters
        ----------
        state : Any
            État à vérifier.

        Raises
        ------
        ValueError
            Si ``state`` n'appartient pas à ``self.states``.

        Complexity
        ----------
        O(1)
        """
        if state not in self.states:  # type: ignore[attr-defined]
            raise ValueError(f"L'état {state!r} n'appartient pas à l'automate.")

    def _iter_transitions_edges(self) -> Iterator[Tuple[Any, Any, Any]]:
        """
        Itère sur tous les arcs orientés ``(source, label, destination)`` du graphe.

        Gère uniformément les structures de transitions de ``DFA`` (destination unique,
        y compris lorsque l'état est un ``tuple`` ou un ``frozenset``), ``NFA``
        (ensemble de destinations) et ``GNFA`` (mapping ``src -> dst -> regex``).

        Returns
        -------
        Iterator[Tuple[Any, Any, Any]]
            Triplets ``(état_source, étiquette, état_destination)``.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        transitions = self.transitions  # type: ignore[attr-defined]
        is_gnfa = isinstance(self, GNFA)
        is_dfa = isinstance(self, DFA)

        for src, mapping in transitions.items():
            if is_gnfa:
                for dst, label in mapping.items():
                    if label is not None:
                        yield (src, label, dst)
            elif is_dfa:
                for symbol, dst in mapping.items():
                    if dst is not None:
                        yield (src, symbol, dst)
            else:
                for symbol, target in mapping.items():
                    if isinstance(target, Iterable) and not isinstance(target, (str, bytes)):
                        for dst in target:
                            yield (src, symbol, dst)
                    elif target is not None:
                        yield (src, symbol, target)

    def _adjacency_list(self) -> Dict[Any, Set[Any]]:
        """
        Construit la liste d'adjacence sortante du graphe de transition.

        Returns
        -------
        Dict[Any, Set[Any]]
            Dictionnaire associant à chaque état l'ensemble de ses successeurs directs.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        adj: Dict[Any, Set[Any]] = {state: set() for state in self.states}  # type: ignore[attr-defined]
        for src, _, dst in self._iter_transitions_edges():
            if src in adj:
                adj[src].add(dst)
        return adj

    def _reverse_adjacency_list(self) -> Dict[Any, Set[Any]]:
        """
        Construit la liste d'adjacence entrante (graphe transposé) de l'automate.

        Returns
        -------
        Dict[Any, Set[Any]]
            Dictionnaire associant à chaque état l'ensemble de ses prédécesseurs directs.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        rev_adj: Dict[Any, Set[Any]] = {state: set() for state in self.states}  # type: ignore[attr-defined]
        for src, _, dst in self._iter_transitions_edges():
            if dst in rev_adj:
                rev_adj[dst].add(src)
        return rev_adj

    @staticmethod
    def _sorted_states(states: Iterable[Any]) -> List[Any]:
        """
        Trie une collection d'états de manière déterministe, même pour des types hétérogènes.

        Parameters
        ----------
        states : Iterable[Any]
            Collection d'états à trier.

        Returns
        -------
        List[Any]
            Liste triée des états.

        Complexity
        ----------
        O(|S| log |S|)
        """
        items = list(states)
        try:
            return sorted(items)
        except TypeError:
            return sorted(items, key=lambda x: (type(x).__name__, str(x)))

    def successors_graph(self, state: Any) -> Set[Any]:
        """
        Retourne l'ensemble des successeurs directs d'un état dans le graphe de transition.

        Parameters
        ----------
        state : Any
            État source.

        Returns
        -------
        Set[Any]
            Ensemble des états atteignables en une transition depuis ``state``.

        Raises
        ------
        ValueError
            Si ``state`` n'appartient pas à ``self.states``.

        Complexity
        ----------
        O(|Σ| + deg⁺(state))

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        self._validate_state_exists(state)
        transitions = self.transitions  # type: ignore[attr-defined]
        mapping = transitions.get(state, {})
        result: Set[Any] = set()

        if isinstance(self, GNFA):
            for dst, label in mapping.items():
                if label is not None:
                    result.add(dst)
        elif isinstance(self, DFA):
            for _, dst in mapping.items():
                if dst is not None:
                    result.add(dst)
        else:
            for _, target in mapping.items():
                if isinstance(target, Iterable) and not isinstance(target, (str, bytes)):
                    result.update(target)
                elif target is not None:
                    result.add(target)

        return result

    def predecessors_graph(self, state: Any) -> Set[Any]:
        """
        Retourne l'ensemble des prédécesseurs directs d'un état dans le graphe de transition.

        Parameters
        ----------
        state : Any
            État cible.

        Returns
        ------
        Set[Any]
            Ensemble des états ayant une transition directe vers ``state``.

        Raises
        ------
        ValueError
            Si ``state`` n'appartient pas à ``self.states``.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        self._validate_state_exists(state)
        result: Set[Any] = set()
        for src, _, dst in self._iter_transitions_edges():
            if dst == state:
                result.add(src)
        return result

    def frozen_states(self) -> FrozenSet[Any]:
        """
        Retourne l'ensemble immuable des états de l'automate.

        Returns
        -------
        FrozenSet[Any]
            Ensemble figé ``frozenset(self.states)``.

        Complexity
        ----------
        O(|Q|)
        """
        return frozenset(self.states)  # type: ignore[attr-defined]