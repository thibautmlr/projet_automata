from __future__ import annotations
from collections import deque
from collections.abc import Mapping
from typing import Any, Dict, FrozenSet, Iterable, List, Optional, Set, Tuple, Union


class MinimizationExtraMixin:
    """Compléments sur la minimisation : minify(), quotient_by() et counterexample()."""

    def minify(self, rename: bool = True):
        """
        Minimise le DFA et renomme ses états en '0', '1', ..., 'n-1'
        par parcours en largeur depuis l'état initial (si `rename=True`).

        Complexity
        ----------
        O(|Sigma| * |Q|^2)
        """
        from ..dfa import ExtendedDFA

        minimal = self.minimize()
        if not rename:
            return minimal

        symbols = sorted(minimal.input_symbols)
        visited: List[Any] = [minimal.initial_state]
        seen: Set[Any] = {minimal.initial_state}
        queue = deque([minimal.initial_state])

        while queue:
            curr = queue.popleft()
            for sym in symbols:
                nxt = minimal.transitions.get(curr, {}).get(sym)
                if nxt is not None and nxt not in seen:
                    seen.add(nxt)
                    visited.append(nxt)
                    queue.append(nxt)

        for q in sorted(minimal.states, key=str):
            if q not in seen:
                seen.add(q)
                visited.append(q)

        name_map = {q: str(i) for i, q in enumerate(visited)}
        new_states = set(name_map.values())
        new_finals = {name_map[q] for q in minimal.final_states}
        new_transitions: Dict[str, Dict[str, str]] = {
            name_map[u]: {
                sym: name_map[v]
                for sym, v in trans.items()
                if v is not None
            }
            for u, trans in minimal.transitions.items()
        }

        return ExtendedDFA(
            states=new_states,
            input_symbols=set(minimal.input_symbols),
            transitions=new_transitions,
            initial_state=name_map[minimal.initial_state],
            final_states=new_finals,
            allow_partial=minimal.allow_partial,
        )

    def quotient_by(
        self,
        partition: Union[Mapping[Any, Any], Iterable[Iterable[Any]]],
    ):
        """
        Construit l'automate quotient ExtendedDFA associé à une partition congruente :
        - soit un dictionnaire `{état: représentant}`,
        - soit un itérable de classes d'équivalence (chaque classe devient un `frozenset`).

        Complexity
        ----------
        O(|Q| * |Sigma|)
        """
        from ..dfa import ExtendedDFA

        state_to_class: Dict[Any, Any] = {}
        class_members: Dict[Any, Set[Any]] = {}

        if isinstance(partition, Mapping):
            if set(partition.keys()) != set(self.states):
                raise ValueError("Les clés du dictionnaire doivent être exactement self.states.")
            for q, rep in partition.items():
                state_to_class[q] = rep
                class_members.setdefault(rep, set()).add(q)
        else:
            blocks: List[FrozenSet[Any]] = [frozenset(part) for part in partition]
            if any(len(b) == 0 for b in blocks):
                raise ValueError("Une partition ne peut pas contenir de classe vide.")
            for block in blocks:
                for q in block:
                    if q in state_to_class:
                        raise ValueError(f"État {q!r} présent dans plusieurs classes.")
                    state_to_class[q] = block
                class_members[block] = set(block)
            if set(state_to_class.keys()) != set(self.states):
                raise ValueError("La réunion des classes doit être égale à self.states.")

        new_finals: Set[Any] = set()
        new_transitions: Dict[Any, Dict[str, Any]] = {}

        for cls_id, members in class_members.items():
            final_flags = {q in self.final_states for q in members}
            if len(final_flags) > 1:
                raise ValueError(
                    f"La classe {members} mélange des états finaux et non finaux."
                )
            if True in final_flags:
                new_finals.add(cls_id)

            new_transitions[cls_id] = {}
            for sym in self.input_symbols:
                target_classes: Set[Optional[Any]] = set()
                for q in members:
                    dst = self.transitions.get(q, {}).get(sym)
                    target_classes.add(state_to_class[dst] if dst is not None else None)
                if len(target_classes) > 1:
                    raise ValueError(
                        f"La partition n'est pas congruente sur {members} pour le symbole {sym!r}."
                    )
                sole_target = next(iter(target_classes))
                if sole_target is not None:
                    new_transitions[cls_id][sym] = sole_target

        return ExtendedDFA(
            states=set(class_members.keys()),
            input_symbols=set(self.input_symbols),
            transitions=new_transitions,
            initial_state=state_to_class[self.initial_state],
            final_states=new_finals,
            allow_partial=self.allow_partial,
        )

    def counterexample(self, other) -> Optional[str]:
        """
        Retourne le plus court mot (dans l'ordre lexicographique) appartenant à la différence
        symétrique L(self) Δ L(other), ou None si L(self) == L(other).

        Complexity
        ----------
        O(|Q_1| * |Q_2| * |Sigma|)
        """
        if self.input_symbols != other.input_symbols:
            raise ValueError(
                f"Alphabets incompatibles : {self.input_symbols} != {other.input_symbols}."
            )

        d1 = self.complete()
        d2 = other.complete()
        symbols = sorted(d1.input_symbols)

        start = (d1.initial_state, d2.initial_state)
        queue: deque[Tuple[Tuple[Any, Any], str]] = deque([(start, "")])
        visited: Set[Tuple[Any, Any]] = {start}

        while queue:
            (q1, q2), word = queue.popleft()
            if (q1 in d1.final_states) != (q2 in d2.final_states):
                return word
            for sym in symbols:
                nxt = (d1.transitions[q1][sym], d2.transitions[q2][sym])
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, f"{word}{sym}"))

        return None