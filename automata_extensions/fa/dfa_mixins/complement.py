"""Mixin de complémentation et de décision d'universalité d'un DFA."""

from __future__ import annotations

from typing import Any, Set


class ComplementMixin:
    """
    Fournit la complémentation d'un langage régulier représenté par un DFA
    ainsi que le test d'universalité (``L(A) = Σ*``).
    """

    def complement(
        self,
        minify: bool = False,
        retain_names: bool = False,
    ) -> Any:
        """
        Construit l'automate complémentaire reconnaissant ``Σ* \\ L(self)``.

        Complète d'abord l'automate (étape indispensable pour préserver le
        complément), puis inverse l'ensemble des états accepteurs ``Q \\ F``.

        Parameters
        ----------
        minify : bool, default=False
            Si ``True``, minimise le résultat via ``minimize(keep_original_names=retain_names)``.
        retain_names : bool, default=False
            Transmis à ``minimize(keep_original_names=retain_names)`` lorsque ``minify=True``.

        Returns
        -------
        ExtendedDFA
            Nouvelle instance d'``ExtendedDFA`` reconnaissant le langage complémentaire.

        Complexity
        ----------
        O(|Q| · |Σ|) sans minimisation ; O(|Q|² · |Σ|) avec ``minify=True``.

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        completed = self.complete()  # type: ignore[attr-defined]
        all_states: Set[Any] = set(completed.states)
        old_finals: Set[Any] = set(completed.final_states)
        new_finals = all_states - old_finals

        cls = type(self)
        comp_dfa = cls(
            states=all_states,
            input_symbols=set(completed.input_symbols),
            transitions={s: dict(completed.transitions[s]) for s in all_states},
            initial_state=completed.initial_state,
            final_states=new_finals,
        )

        if minify:
            return comp_dfa.minimize(keep_original_names=retain_names)
        return comp_dfa

    def is_universal(self) -> bool:
        """
        Décide si l'automate reconnaît l'ensemble de tous les mots ``Σ*``.

        Par dualité ensembliste, ``L(A) = Σ*`` si et seulement si ``L(A)^c = ∅``.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            ``True`` si ``L(self) = Σ*``, ``False`` sinon.

        Complexity
        ----------
        O(|Q| · |Σ|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        return bool(self.complement().is_empty())