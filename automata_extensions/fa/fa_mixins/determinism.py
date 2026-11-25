"""Mixin de vérification du caractère déterministe d'un automate fini."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from automata.fa.dfa import DFA
from automata.fa.gnfa import GNFA


class DeterminismMixin:
    """
    Fournit le prédicat ``is_deterministic()`` sur tout automate fini.
    """

    def is_deterministic(self, require_complete: bool = False) -> bool:
        """
        Teste si la fonction de transition de l'automate est déterministe.

        Un automate est déterministe s'il ne comporte aucune transition epsilon (``""``)
        et si, pour chaque couple ``(état, symbole)``, il existe au plus une transition
        sortante (exactement une si ``require_complete=True``).

        Parameters
        ----------
        require_complete : bool, default=False
            Si ``True``, exige en plus que la fonction de transition soit totale
            (automate complet).

        Returns
        -------
        bool
            ``True`` si l'automate est déterministe, ``False`` sinon.

        Complexity
        ----------
        O(|Q| · |Σ|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        states = self.states  # type: ignore[attr-defined]
        alphabet = self.input_symbols  # type: ignore[attr-defined]
        transitions = self.transitions  # type: ignore[attr-defined]

        if isinstance(self, GNFA):
            for src in states:
                mapping = transitions.get(src, {})
                seen_symbols: set[Any] = set()
                for _, label in mapping.items():
                    if label is None:
                        continue
                    if label not in alphabet or label in seen_symbols:
                        return False
                    seen_symbols.add(label)
                if require_complete and seen_symbols != set(alphabet):
                    return False
            return True

        if isinstance(self, DFA):
            if not require_complete:
                return True
            for src in states:
                mapping = transitions.get(src, {})
                if not all(sym in mapping and mapping[sym] is not None for sym in alphabet):
                    return False
            return True

        # Cas général (NFA ou structure compatible)
        for src in states:
            mapping = transitions.get(src, {})
            if "" in mapping and len(mapping[""]) > 0:
                return False

            defined_count = 0
            for sym, targets in mapping.items():
                if sym == "":
                    continue
                if isinstance(targets, Iterable) and not isinstance(targets, (str, bytes)):
                    target_set = set(targets)
                else:
                    target_set = {targets} if targets is not None else set()

                if len(target_set) > 1:
                    return False
                if len(target_set) == 1:
                    defined_count += 1

            if require_complete and defined_count != len(alphabet):
                return False

        return True