"""Mixin d'extraction de sous-automate induit par un sous-ensemble d'états."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Optional, Set


class SubautomatonMixin:
    """
    Fournit l'extraction d'un sous-automate induit par une restriction d'états.

    Toutes les transitions internes au sous-ensemble d'états conservé sont préservées ;
    celles sortant du sous-ensemble sont supprimées.
    """

    def induced_subautomaton(
        self,
        states: Iterable[Any],
        initial_state: Optional[Any] = None,
    ) -> Any:
        """
        Extrait le sous-automate induit par un sous-ensemble d'états ``S ⊆ Q``.

        Parameters
        ----------
        states : Iterable[Any]
            Sous-ensemble d'états à conserver (doit être non vide et inclus dans ``self.states``).
        initial_state : Optional[Any], default=None
            État initial du sous-automate. Si ``None``, utilise ``self.initial_state``
            (qui doit alors appartenir à ``states``).

        Returns
        -------
        ExtendedFA
            Nouvelle instance du même type que ``self`` restreinte aux états fournis.

        Raises
        ------
        ValueError
            Si ``states`` est vide, contient un état inconnu, ou si l'état initial
            n'appartient pas à ``states``.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Sakarovitch, Éléments de théorie des automates.
        """
        kept_states: Set[Any] = set(states)
        if not kept_states:
            raise ValueError("Le sous-ensemble d'états d'un sous-automate doit être non vide.")

        unknown = kept_states - set(self.states)  # type: ignore[attr-defined]
        if unknown:
            raise ValueError(f"États inconnus dans l'automate : {unknown!r}")

        new_initial = self.initial_state if initial_state is None else initial_state  # type: ignore[attr-defined]
        if new_initial not in kept_states:
            raise ValueError(
                f"L'état initial {new_initial!r} doit appartenir aux états conservés {kept_states!r}."
            )

        orig_finals: Set[Any] = set(self._get_final_states())  # type: ignore[attr-defined]
        new_finals = orig_finals & kept_states

        return self._build_restricted_automaton(  # type: ignore[attr-defined]
            kept_states=kept_states,
            initial_state=new_initial,
            final_states=new_finals,
        )