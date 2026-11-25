"""Classe ``ExtendedDFA`` étendant ``automata.fa.dfa.DFA`` par héritage multiple."""

from __future__ import annotations

from automata.fa.dfa import DFA

from automata_extensions.fa.dfa_mixins.complement import ComplementMixin
from automata_extensions.fa.dfa_mixins.completeness import CompletenessMixin
from automata_extensions.fa.dfa_mixins.difference import DifferenceMixin
from automata_extensions.fa.dfa_mixins.execution import ExecutionMixin
from automata_extensions.fa.dfa_mixins.inclusion import InclusionMixin
from automata_extensions.fa.dfa_mixins.isomorphism import IsomorphismMixin
from automata_extensions.fa.dfa_mixins.minimization import MinimizationMixin
from automata_extensions.fa.dfa_mixins.prefix import PrefixMixin
from automata_extensions.fa.dfa_mixins.product import ProductMixin
from automata_extensions.fa.dfa_mixins.union import UnionMixin
from automata_extensions.fa.fa import ExtendedFA


class ExtendedDFA(
    CompletenessMixin,
    ComplementMixin,
    ProductMixin,
    DifferenceMixin,
    UnionMixin,
    InclusionMixin,
    IsomorphismMixin,
    MinimizationMixin,
    ExecutionMixin,
    PrefixMixin,
    ExtendedFA,
    DFA,
):
    """Automate fini déterministe étendu."""

    pass