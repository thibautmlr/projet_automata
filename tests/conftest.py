"""Fixtures d'automates issues de la documentation et des exercices de TD."""

import pytest

from automata_extensions.fa.dfa import ExtendedDFA
from automata_extensions.fa.gnfa import ExtendedGNFA
from automata_extensions.fa.nfa import ExtendedNFA


@pytest.fixture
def dfa_mod3_a() -> ExtendedDFA:
    """
    Fixture ``d`` de la documentation : mots sur {a, b} dont le nombre de 'a' est multiple de 3.
    """
    return ExtendedDFA(
        states={"0", "1", "2"},
        input_symbols={"a", "b"},
        transitions={
            "0": {"a": "1", "b": "0"},
            "1": {"a": "2", "b": "1"},
            "2": {"a": "0", "b": "2"},
        },
        initial_state="0",
        final_states={"0"},
    )


@pytest.fixture
def nfa_with_epsilon() -> ExtendedNFA:
    """
    Fixture ``n`` de la documentation : NFA avec une epsilon-transition '' de 'p' vers 'r'.
    """
    return ExtendedNFA(
        states={"p", "q", "r"},
        input_symbols={"a", "b"},
        transitions={
            "p": {"a": {"p", "q"}, "": {"r"}},
            "q": {"b": {"q"}},
            "r": {"a": {"r"}},
        },
        initial_state="p",
        final_states={"q", "r"},
    )


@pytest.fixture
def dfa_cours_6() -> ExtendedDFA:
    """
    Automate ``automate_cours_6`` (Cours 06 / Exemples) : tous les états sont accessibles et utiles.
    """
    return ExtendedDFA(
        states={"1", "2", "3", "4", "5", "6", "7", "8"},
        input_symbols={"a", "b"},
        transitions={
            "1": {"a": "2", "b": "6"},
            "2": {"a": "7", "b": "3"},
            "3": {"a": "1", "b": "3"},
            "4": {"a": "3", "b": "7"},
            "5": {"a": "8", "b": "6"},
            "6": {"a": "3", "b": "7"},
            "7": {"a": "7", "b": "5"},
            "8": {"a": "7", "b": "3"},
        },
        initial_state="1",
        final_states={"3"},
    )


@pytest.fixture
def dfa_with_sink_and_unreachable() -> ExtendedDFA:
    """
    Automate combinant états utiles, état puits non coaccessible ('sink')
    et composante inaccessible ('unreach1' <-> 'unreach2').
    """
    return ExtendedDFA(
        states={"q0", "q1", "q2", "sink", "unreach1", "unreach2"},
        input_symbols={"a", "b"},
        transitions={
            "q0": {"a": "q1", "b": "sink"},
            "q1": {"a": "q2", "b": "sink"},
            "q2": {"a": "q2", "b": "q2"},
            "sink": {"a": "sink", "b": "sink"},
            "unreach1": {"a": "unreach2", "b": "q2"},
            "unreach2": {"a": "unreach1", "b": "sink"},
        },
        initial_state="q0",
        final_states={"q2"},
    )


@pytest.fixture
def gnfa_from_mod3(dfa_mod3_a: ExtendedDFA) -> ExtendedGNFA:
    """GNFA construit à partir de la fixture ``d``."""
    return ExtendedGNFA.from_dfa(dfa_mod3_a)