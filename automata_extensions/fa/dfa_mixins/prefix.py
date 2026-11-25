"""Mixin d'analyse de clôture par préfixe et d'extraction de sous-langage préfixe-clos."""

from __future__ import annotations

from typing import Any, Set


class PrefixMixin:
    """
    Fournit les algorithmes liés aux langages préfixes-clos sur un ``ExtendedDFA``.

    Un langage ``L`` est préfixe-clos si pour tout mot ``w ∈ L``, tous les préfixes
    de ``w`` appartiennent également à ``L``.
    """

    def is_prefix_closed(self) -> bool:
        """
        Teste si le langage reconnu par l'automate est préfixe-clos.

        Un langage régulier reconnu par un DFA est préfixe-clos si et seulement si
        tous les états utiles (accessibles et coaccessibles) de l'automate sont
        accepteurs. Si le langage est vide, la propriété est vraie par vacuité.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            ``True`` si ``L(self)`` est préfixe-clos, ``False`` sinon.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Cassandras & Lafortune, Introduction to Discrete Event Systems (Prefix-Closure).
        """
        useful: Set[Any] = self.useful_states()  # type: ignore[attr-defined]
        finals: Set[Any] = set(self.final_states)  # type: ignore[attr-defined]
        return useful.issubset(finals)

    def prefix_closed_sublanguage(self) -> Any:
        """
        Construit un nouvel ``ExtendedDFA`` reconnaissant le plus grand sous-langage
        préfixe-clos inclus dans ``L(self)``.

        Un mot ``w`` appartient au plus grand sous-langage préfixe-clos de ``L(self)``
        si et seulement si son exécution depuis l'état initial ne traverse que des
        états accepteurs. L'automate s'obtient donc en restreignant le DFA aux seuls
        états accepteurs accessibles depuis ``initial_state`` (ou en retournant un
        automate vide si ``initial_state`` n'est pas final).

        Parameters
        ----------
        None

        Returns
        -------
        ExtendedDFA
            Nouvelle instance d'``ExtendedDFA`` reconnaissant le plus grand sous-langage
            préfixe-clos de ``L(self)``, sans modifier ``self``.

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Cassandras & Lafortune, Introduction to Discrete Event Systems (Supremal Prefix-Closed Sublanguage).
        """
        initial = self.initial_state  # type: ignore[attr-defined]
        finals: Set[Any] = set(self.final_states)  # type: ignore[attr-defined]

        if initial not in finals:
            return self._build_restricted_automaton(  # type: ignore[attr-defined]
                kept_states={initial},
                initial_state=initial,
                final_states=set(),
            )

        sub = self.induced_subautomaton(finals, initial_state=initial)  # type: ignore[attr-defined]
        return sub.trim()