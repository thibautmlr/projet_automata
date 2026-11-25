from __future__ import annotations
from collections import deque
from typing import Any, Callable, Dict, FrozenSet, Optional, Set


class DeterminizationMixin:
    """Mixin fournissant la déterminisation d'un NFA en ExtendedDFA (construction des sous-ensembles)."""

    def determinize(
        self,
        retain_names: bool = True,
        state_namer: Optional[Callable[[FrozenSet[Any]], Any]] = None,
    ):
        """
        Déterminise le NFA en ExtendedDFA par construction des sous-ensembles accessibles non vides.

        Parameters
        ----------
        retain_names : bool, default=True
            Si True (et state_namer est None), conserve les frozenset d'états comme noms d'états.
            Si False, renomme les états en '0', '1', '2', ...
        state_namer : Callable[[FrozenSet], Any], optional
            Fonction personnalisée pour nommer chaque sous-ensemble d'états.

        Complexity
        ----------
        O(2^|Q| * |Sigma|)
        """
        from ..dfa import ExtendedDFA

        initial_subset = self.epsilon_closure(self.initial_state)

        subsets: list[FrozenSet[Any]] = [initial_subset]
        visited: Set[FrozenSet[Any]] = {initial_subset}
        queue = deque([initial_subset])
        raw_transitions: Dict[FrozenSet[Any], Dict[str, FrozenSet[Any]]] = {}

        while queue:
            current_set = queue.popleft()
            raw_transitions[current_set] = {}

            for symbol in self.input_symbols:
                next_states: Set[Any] = set()
                for state in current_set:
                    targets = self.transitions.get(state, {}).get(symbol, set())
                    for t in targets:
                        next_states.update(self.epsilon_closure(t))

                if not next_states:
                    continue

                next_subset = frozenset(next_states)
                raw_transitions[current_set][symbol] = next_subset

                if next_subset not in visited:
                    visited.add(next_subset)
                    subsets.append(next_subset)
                    queue.append(next_subset)

        # Attribution des noms d'états du DFA
        if state_namer is not None:
            name_map = {s: state_namer(s) for s in subsets}
        elif not retain_names:
            name_map = {s: str(i) for i, s in enumerate(subsets)}
        else:
            name_map = {s: s for s in subsets}

        dfa_states = set(name_map.values())
        dfa_initial = name_map[initial_subset]
        dfa_finals = {
            name_map[s] for s in subsets if not s.isdisjoint(self.final_states)
        }
        dfa_transitions = {
            name_map[src]: {
                sym: name_map[dst] for sym, dst in trans.items()
            }
            for src, trans in raw_transitions.items()
        }

        return ExtendedDFA(
            states=dfa_states,
            input_symbols=set(self.input_symbols),
            transitions=dfa_transitions,
            initial_state=dfa_initial,
            final_states=dfa_finals,
            allow_partial=True,
        )

    def to_dfa(
        self,
        retain_names: bool = True,
        state_namer: Optional[Callable[[FrozenSet[Any]], Any]] = None,
    ):
        """Alias de determinize()."""
        return self.determinize(retain_names=retain_names, state_namer=state_namer)