"""Mixin de test d'isomorphisme structurel entre deux automates finis déterministes."""

from __future__ import annotations

from collections import deque
from typing import Any, Deque, Dict, List, Optional, Set, Tuple

from automata.fa.dfa import DFA


class IsomorphismMixin:
    """
    Fournit le test d'isomorphisme (bijection entre états préservant l'état initial,
    les états finaux et toutes les transitions étiquetées) entre deux DFA.
    """

    def isomorphism_to(self, other: DFA) -> Optional[Dict[Any, Any]]:
        """
        Recherche une bijection ``φ : Q1 → Q2`` définissant un isomorphisme d'automates
        entre ``self`` et ``other``.

        Deux DFA ``A1`` et ``A2`` sur le même alphabet ``Σ`` sont isomorphes s'il
        existe une bijection ``φ : Q1 → Q2`` telle que :
        1. ``φ(q0_1) = q0_2`` ;
        2. ``∀q ∈ Q1, q ∈ F1 ⟺ φ(q) ∈ F2`` ;
        3. ``∀q ∈ Q1, ∀a ∈ Σ, δ1(q, a) est définie ⟺ δ2(φ(q), a) est définie``
           et ``φ(δ1(q, a)) = δ2(φ(q), a)``.

        Parameters
        ----------
        other : DFA
            Second automate fini déterministe.

        Returns
        -------
        Optional[Dict[Any, Any]]
            Dictionnaire ``{état_self: état_other}`` réalisant l'isomorphisme, ou ``None``
            si les deux automates ne sont pas isomorphes.

        Complexity
        ----------
        O(|Q| · |Σ|) pour des automates accessibles ; backtracking sur composantes
        inaccessibles éventuelles.

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        if not isinstance(other, DFA):
            raise TypeError(f"Un DFA était attendu, reçu : {type(other)!r}")

        if set(self.input_symbols) != set(other.input_symbols):  # type: ignore[attr-defined]
            return None

        states1: Set[Any] = set(self.states)  # type: ignore[attr-defined]
        states2: Set[Any] = set(other.states)
        if len(states1) != len(states2):
            return None

        finals1: Set[Any] = set(self.final_states)  # type: ignore[attr-defined]
        finals2: Set[Any] = set(other.final_states)
        if len(finals1) != len(finals2):
            return None

        alphabet = self._sorted_states(self.input_symbols)  # type: ignore[attr-defined]
        t1 = self.transitions  # type: ignore[attr-defined]
        t2 = other.transitions

        def _propagate(
            seed_u: Any,
            seed_v: Any,
            fwd: Dict[Any, Any],
            bwd: Dict[Any, Any],
        ) -> bool:
            if (seed_u in finals1) != (seed_v in finals2):
                return False
            if seed_u in fwd:
                return fwd[seed_u] == seed_v
            if seed_v in bwd:
                return bwd[seed_v] == seed_u

            fwd[seed_u] = seed_v
            bwd[seed_v] = seed_u
            queue: Deque[Tuple[Any, Any]] = deque([(seed_u, seed_v)])

            while queue:
                u, v = queue.popleft()
                row_u = t1.get(u, {})
                row_v = t2.get(v, {})
                for sym in alphabet:
                    has_u = sym in row_u and row_u[sym] is not None
                    has_v = sym in row_v and row_v[sym] is not None
                    if has_u != has_v:
                        return False
                    if not has_u:
                        continue
                    nu = row_u[sym]
                    nv = row_v[sym]
                    if (nu in finals1) != (nv in finals2):
                        return False
                    if nu in fwd:
                        if fwd[nu] != nv:
                            return False
                    elif nv in bwd:
                        return False
                    else:
                        fwd[nu] = nv
                        bwd[nv] = nu
                        queue.append((nu, nv))
            return True

        fwd_map: Dict[Any, Any] = {}
        bwd_map: Dict[Any, Any] = {}
        if not _propagate(self.initial_state, other.initial_state, fwd_map, bwd_map):  # type: ignore[attr-defined]
            return None

        if len(fwd_map) == len(states1):
            return fwd_map

        # Gestion d'éventuelles composantes inaccessibles via backtracking déterministe
        remaining_u: List[Any] = self._sorted_states(states1 - set(fwd_map.keys()))  # type: ignore[attr-defined]
        remaining_v: List[Any] = self._sorted_states(states2 - set(bwd_map.keys()))  # type: ignore[attr-defined]

        def _backtrack(cur_fwd: Dict[Any, Any], cur_bwd: Dict[Any, Any]) -> Optional[Dict[Any, Any]]:
            if len(cur_fwd) == len(states1):
                return cur_fwd
            next_u = next(u for u in remaining_u if u not in cur_fwd)
            for cand_v in remaining_v:
                if cand_v in cur_bwd:
                    continue
                trial_fwd = dict(cur_fwd)
                trial_bwd = dict(cur_bwd)
                if _propagate(next_u, cand_v, trial_fwd, trial_bwd):
                    res = _backtrack(trial_fwd, trial_bwd)
                    if res is not None:
                        return res
            return None

        return _backtrack(fwd_map, bwd_map)

    def is_isomorphic_to(self, other: DFA) -> bool:
        """
        Teste s'il existe un isomorphisme d'automates entre ``self`` et ``other``.

        Parameters
        ----------
        other : DFA
            Second automate fini déterministe.

        Returns
        -------
        bool
            ``True`` si ``self`` et ``other`` sont isomorphes, ``False`` sinon.

        Complexity
        ----------
        O(|Q| · |Σ|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        return self.isomorphism_to(other) is not None