"""Classe de base commune ``ExtendedFA`` pour les automates finis étendus."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Dict, FrozenSet, Set

from automata.fa.dfa import DFA
from automata.fa.fa import FA
from automata.fa.gnfa import GNFA
from automata.fa.nfa import NFA

from .fa_mixins.language_operations import LanguageOperationsMixin
from .fa_mixins.quotient_fa import QuotientMixin
from automata_extensions.fa.fa_mixins.accessibility import AccessibilityMixin
from automata_extensions.fa.fa_mixins.cycle import CycleMixin
from automata_extensions.fa.fa_mixins.determinism import DeterminismMixin
from automata_extensions.fa.fa_mixins.graph import GraphMixin
from automata_extensions.fa.fa_mixins.reverse import ReverseMixin
from automata_extensions.fa.fa_mixins.scc import SCCMixin
from automata_extensions.fa.fa_mixins.subautomaton import SubautomatonMixin
from automata_extensions.fa.fa_mixins.traversal import TraversalMixin
from automata_extensions.fa.fa_mixins.word import WordMixin


class ExtendedFA(
    GraphMixin,
    TraversalMixin,
    AccessibilityMixin,
    SubautomatonMixin,
    SCCMixin,
    CycleMixin,
    WordMixin,
    DeterminismMixin,
    ReverseMixin,
    LanguageOperationsMixin,
    QuotientMixin,
    FA,
):
    """
    Classe mère commune aux automates finis étendus (``ExtendedDFA``, ``ExtendedNFA``,
    ``ExtendedGNFA``).

    Regroupe tous les algorithmes génériques indépendants du déterminisme et des
    transitions epsilon, corrige ``input_parameters`` sur l'ensemble du MRO et
    fournit une méthode ``copy()`` immuable et sûre.
    """

    @property
    def input_parameters(self) -> Dict[str, Any]:
        """
        Collecte les paramètres publics reconstructibles sur l'ensemble du MRO.

        Corrige le comportement d'automata-lib 9.2.0 qui n'inspecte qu'un seul niveau
        de ``__slots__``, rendant ``copy()`` et le pickling fonctionnels sur les
        sous-classes étendues.

        Returns
        -------
        Dict[str, Any]
            Dictionnaire des attributs publics de construction de l'automate.

        Complexity
        ----------
        O(|MRO|)
        """
        params: Dict[str, Any] = {}
        ignored = {"__dict__", "__weakref__", "_cache"}
        for cls in self.__class__.__mro__:
            slots = getattr(cls, "__slots__", ())
            if isinstance(slots, str):
                slots = (slots,)
            for slot in slots:
                if slot in ignored or slot.startswith("_"):
                    continue
                if hasattr(self, slot):
                    params[slot] = getattr(self, slot)
        return params

    def copy(self) -> "ExtendedFA":
        """
        Retourne une copie indépendante de l'automate sans partager de cache interne.

        Reconstruit l'automate via ses paramètres publics afin d'éviter la corruption
        des ``frozendict`` d'automata-lib par ``copy.deepcopy``.

        Parameters
        ----------
        None

        Returns
        -------
        ExtendedFA
            Nouvelle instance identique mais distincte en mémoire (``d2 == d`` et ``d2 is not d``).

        Complexity
        ----------
        O(|Q| + |E|)

        References
        ----------
        Documentation automata_extensions, Section 10.
        """
        params = self.input_parameters
        if "states" in params:
            params["states"] = set(params["states"])
        if "input_symbols" in params:
            params["input_symbols"] = set(params["input_symbols"])
        if "final_states" in params:
            params["final_states"] = set(params["final_states"])
        if "transitions" in params:
            orig_t = params["transitions"]
            if isinstance(self, NFA):
                params["transitions"] = {
                    src: {
                        sym: set(targets)
                        if isinstance(targets, Iterable) and not isinstance(targets, (str, bytes))
                        else {targets}
                        for sym, targets in mapping.items()
                    }
                    for src, mapping in orig_t.items()
                }
            else:
                params["transitions"] = {
                    src: dict(mapping) for src, mapping in orig_t.items()
                }

        return type(self)(**params)

    def _get_final_states(self) -> FrozenSet[Any]:
        """
        Retourne l'ensemble des états accepteurs de manière uniforme (y compris pour ``GNFA``).

        Returns
        -------
        FrozenSet[Any]
            Ensemble des états finaux.
        """
        if hasattr(self, "final_states"):
            return frozenset(self.final_states)
        if hasattr(self, "final_state"):
            return frozenset({self.final_state})
        return frozenset()

    def _build_restricted_automaton(
        self,
        kept_states: Set[Any],
        initial_state: Any,
        final_states: Set[Any],
    ) -> "ExtendedFA":
        """
        Construit un nouvel automate du même type restreint à ``kept_states``.

        Parameters
        ----------
        kept_states : Set[Any]
            États conservés.
        initial_state : Any
            État initial du nouvel automate.
        final_states : Set[Any]
            États accepteurs du nouvel automate.

        Returns
        -------
        ExtendedFA
            Nouvelle instance de ``type(self)``.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        cls = type(self)
        orig_transitions = self.transitions

        if isinstance(self, GNFA):
            if len(final_states) != 1:
                raise ValueError(
                    "Un GNFA restreint doit posséder exactement un état final unique."
                )
            single_final = next(iter(final_states))
            new_gnfa_transitions: Dict[Any, Dict[Any, Any]] = {s: {} for s in kept_states}
            for src in kept_states:
                for dst, label in orig_transitions.get(src, {}).items():
                    if dst in kept_states:
                        new_gnfa_transitions[src][dst] = label
            return cls(  # type: ignore[call-arg]
                states=set(kept_states),
                input_symbols=set(self.input_symbols),
                transitions=new_gnfa_transitions,
                initial_state=initial_state,
                final_state=single_final,
            )

        if isinstance(self, DFA):
            new_dfa_transitions: Dict[Any, Dict[Any, Any]] = {s: {} for s in kept_states}
            for src in kept_states:
                for sym, dst in orig_transitions.get(src, {}).items():
                    if dst in kept_states:
                        new_dfa_transitions[src][sym] = dst
            return cls(  # type: ignore[call-arg]
                states=set(kept_states),
                input_symbols=set(self.input_symbols),
                transitions=new_dfa_transitions,
                initial_state=initial_state,
                final_states=set(final_states),
                allow_partial=True,
            )

        if isinstance(self, NFA):
            new_nfa_transitions: Dict[Any, Dict[Any, Set[Any]]] = {s: {} for s in kept_states}
            for src in kept_states:
                for sym, targets in orig_transitions.get(src, {}).items():
                    if isinstance(targets, Iterable) and not isinstance(targets, (str, bytes)):
                        filtered = set(targets) & kept_states
                    else:
                        filtered = {targets} & kept_states
                    if filtered:
                        new_nfa_transitions[src][sym] = filtered
            return cls(  # type: ignore[call-arg]
                states=set(kept_states),
                input_symbols=set(self.input_symbols),
                transitions=new_nfa_transitions,
                initial_state=initial_state,
                final_states=set(final_states),
            )

        raise TypeError(f"Type d'automate non supporté : {cls!r}")