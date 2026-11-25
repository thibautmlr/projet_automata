"""Mixin de calcul de l'automate du langage miroir (renversement)."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Dict, Set

from automata.fa.dfa import DFA
from automata.fa.nfa import NFA


class ReverseMixin:
    """
    Fournit l'opération de renversement (langage miroir) sur tout automate fini.

    Si ``L`` est le langage reconnu par ``self``, ``self.reverse()`` construit un
    ``ExtendedNFA`` reconnaissant ``L^R = { w^R | w ∈ L }``.
    """

    def reverse(self) -> Any:
        """
        Construit un ``ExtendedNFA`` reconnaissant le langage miroir de ``self``.

        Toutes les transitions sont inversées (``p --a--> q`` devient ``q --a--> p``,
        y compris les transitions epsilon ``""``), l'ancien état initial devient
        l'unique état accepteur, et les anciens états accepteurs deviennent les états
        initiaux (via un nouvel état initial relié par transitions epsilon s'il y a
        strictement plus d'un état accepteur).

        Parameters
        ----------
        None

        Returns
        -------
        ExtendedNFA
            Nouvel automate fini non déterministe reconnaissant ``L(self)^R``,
            sans modifier ``self``.

        Raises
        ------
        TypeError
            Si le type d'automate n'est pas pris en charge (ex. ``GNFA``).

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages,
        and Computation (Reversal of Regular Languages).
        """
        from automata_extensions.fa.nfa import ExtendedNFA

        if not isinstance(self, (DFA, NFA)):
            raise TypeError(
                f"Le renversement vers ExtendedNFA n'est pas supporté pour {type(self)!r}."
            )

        states: Set[Any] = set(self.states)  # type: ignore[attr-defined]
        input_symbols: Set[Any] = set(self.input_symbols)  # type: ignore[attr-defined]
        initial = self.initial_state  # type: ignore[attr-defined]
        finals: Set[Any] = set(self._get_final_states())  # type: ignore[attr-defined]

        rev_transitions: Dict[Any, Dict[Any, Set[Any]]] = {s: {} for s in states}

        for src, mapping in self.transitions.items():  # type: ignore[attr-defined]
            for sym, targets in mapping.items():
                if isinstance(self, DFA):
                    target_set = {targets}
                elif isinstance(targets, Iterable) and not isinstance(targets, (str, bytes)):
                    target_set = set(targets)
                else:
                    target_set = {targets}

                for dst in target_set:
                    rev_transitions[dst].setdefault(sym, set()).add(src)

        if len(finals) == 0:
            return ExtendedNFA(
                states=states,
                input_symbols=input_symbols,
                transitions=rev_transitions,
                initial_state=initial,
                final_states=set(),
            )

        if len(finals) == 1:
            new_initial = next(iter(finals))
            return ExtendedNFA(
                states=states,
                input_symbols=input_symbols,
                transitions=rev_transitions,
                initial_state=new_initial,
                final_states={initial},
            )

        new_initial = "q_rev_init"
        counter = 0
        while new_initial in states:
            new_initial = f"__rev_init_{counter}__"
            counter += 1

        new_states = set(states) | {new_initial}
        rev_transitions[new_initial] = {"": set(finals)}

        return ExtendedNFA(
            states=new_states,
            input_symbols=input_symbols,
            transitions=rev_transitions,
            initial_state=new_initial,
            final_states={initial},
        )