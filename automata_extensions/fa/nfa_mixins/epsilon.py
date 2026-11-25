from __future__ import annotations
from collections import deque
from typing import Any, FrozenSet, Iterable


class EpsilonMixin:
    """Mixin fournissant le calcul des fermetures epsilon sur un NFA."""

    def has_epsilon_transitions(self) -> bool:
        """
        Teste si le NFA possède au moins une transition epsilon (clé '').

        Complexity
        ----------
        O(|Q|)
        """
        for trans in self.transitions.values():
            if "" in trans and trans[""]:
                return True
        return False

    def epsilon_closure(self, state: Any) -> FrozenSet[Any]:
        """
        Calcule la fermeture epsilon d'un état donné (parcours BFS).

        Complexity
        ----------
        O(|Q| + |E_eps|)
        """
        if state not in self.states:
            raise ValueError(f"L'état {state!r} n'appartient pas à l'automate.")

        visited = {state}
        queue = deque([state])

        while queue:
            current = queue.popleft()
            eps_targets = self.transitions.get(current, {}).get("", set())
            for target in eps_targets:
                if target not in visited:
                    visited.add(target)
                    queue.append(target)

        return frozenset(visited)

    def epsilon_closure_of_set(self, states: Iterable[Any]) -> FrozenSet[Any]:
        """
        Calcule l'union des fermetures epsilon d'un ensemble d'états.

        Complexity
        ----------
        O(|S| * (|Q| + |E_eps|))
        """
        closure = set()
        for state in states:
            closure.update(self.epsilon_closure(state))
        return frozenset(closure)