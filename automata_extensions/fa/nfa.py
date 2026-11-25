from __future__ import annotations
from typing import Any, FrozenSet, List, Tuple
from automata.fa.nfa import NFA
from .fa import ExtendedFA
from .nfa_mixins.epsilon import EpsilonMixin
from .nfa_mixins.elimination import EliminationMixin
from .nfa_mixins.determinization import DeterminizationMixin
from .nfa_mixins.thompson import ThompsonMixin


class ExtendedNFA(
    EpsilonMixin,
    EliminationMixin,
    DeterminizationMixin,
    ThompsonMixin,
    ExtendedFA,
    NFA,
):
    """NFA étendu avec opérations sur les transitions epsilon et déterminisation."""

    def execution_trace(
        self, input_str: str
    ) -> List[Tuple[FrozenSet[Any], str, FrozenSet[Any]]]:
        """
        Retourne la trace complète (ensemble_courant, symbole, ensemble_suivant)
        de la lecture d'un mot.
        """
        steps = list(self.read_input_stepwise(input_str))
        return [
            (steps[i], symbol, steps[i + 1])
            for i, symbol in enumerate(input_str)
        ]