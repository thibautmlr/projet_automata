"""Classe ``ExtendedDFA`` étendant ``automata.fa.dfa.DFA`` par héritage multiple."""

from __future__ import annotations

from automata.fa.dfa import DFA

from .dfa_mixins.residual import ResidualMixin
from .dfa_mixins.complement import ComplementMixin
from .dfa_mixins.completeness import CompletenessMixin
from .dfa_mixins.difference import DifferenceMixin
from .dfa_mixins.execution import ExecutionMixin
from .dfa_mixins.inclusion import InclusionMixin
from .dfa_mixins.isomorphism import IsomorphismMixin
from .dfa_mixins.minimization import MinimizationMixin
from .dfa_mixins.prefix import PrefixMixin
from .dfa_mixins.product import ProductMixin
from .dfa_mixins.minimization_extra import MinimizationExtraMixin
from .dfa_mixins.syntactic_monoid import SyntacticMonoidMixin
from .dfa_mixins.union import UnionMixin
from .fa import ExtendedFA


class ExtendedDFA(
    CompletenessMixin,
    ComplementMixin,
    ProductMixin,
    SyntacticMonoidMixin,
    DifferenceMixin,
    UnionMixin,
    InclusionMixin,
    IsomorphismMixin,
    MinimizationExtraMixin,
    MinimizationMixin,
    ExecutionMixin,
    PrefixMixin,
    ResidualMixin,
    ExtendedFA,
    DFA,
):
    """Automate fini déterministe étendu."""

    pass