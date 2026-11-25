"""Tests unitaires de l'Étape 6 : conversions vers regex (élimination, optimum, Arden) et Brzozowski."""

import pytest
from automata_extensions.fa import ExtendedDFA, ExtendedNFA


@pytest.fixture
def dfa_fig_3_1_d() -> ExtendedDFA:
    """Automate fig 3.1d : nombre de 'a' congru à 1 modulo 3."""
    return ExtendedDFA(
        states={"1", "2", "3"},
        input_symbols={"a", "b"},
        transitions={
            "1": {"a": "2", "b": "1"},
            "2": {"a": "3", "b": "2"},
            "3": {"a": "1", "b": "3"},
        },
        initial_state="1",
        final_states={"2"},
    )


@pytest.fixture
def nfa_fig_7_2_a() -> ExtendedNFA:
    """Automate fig 7.2a reconnaissant (ba)*."""
    return ExtendedNFA(
        states={"1", "2"},
        input_symbols={"a", "b"},
        transitions={
            "1": {"b": {"2"}},
            "2": {"a": {"1"}},
        },
        initial_state="1",
        final_states={"1"},
    )


class TestRegexConversions:
    def test_to_regex_and_roundtrip(self, dfa_fig_3_1_d, nfa_fig_7_2_a):
        for fa in (dfa_fig_3_1_d, nfa_fig_7_2_a):
            dfa_ref = fa.to_dfa() if isinstance(fa, ExtendedNFA) else fa

            r_std = fa.to_regex()
            r_opt = fa.to_regex_optimum()
            r_ard = fa.to_regex_arden()

            for expr in (r_std, r_opt, r_ard):
                rebuilt = ExtendedNFA.from_regex(expr, input_symbols=fa.input_symbols).to_dfa()
                assert rebuilt.is_equivalent(dfa_ref) is True

        # L'heuristique optimale doit produire une expression au moins aussi courte que l'ordre standard
        assert len(dfa_fig_3_1_d.to_regex_optimum()) <= len(dfa_fig_3_1_d.to_regex())

    def test_empty_and_epsilon_languages(self):
        empty_dfa = ExtendedDFA(
            states={"q0"},
            input_symbols={"a"},
            transitions={"q0": {"a": "q0"}},
            initial_state="q0",
            final_states=set(),
        )
        assert empty_dfa.to_regex() == "∅"
        assert empty_dfa.to_regex_optimum() == "∅"
        assert empty_dfa.to_regex_arden() == "∅"

        eps_dfa = ExtendedDFA(
            states={"q0"},
            input_symbols={"a"},
            transitions={"q0": {}},
            initial_state="q0",
            final_states={"q0"},
            allow_partial=True,
        )
        for expr in (eps_dfa.to_regex(), eps_dfa.to_regex_optimum(), eps_dfa.to_regex_arden()):
            rebuilt = ExtendedNFA.from_regex(expr, input_symbols={"a"}).to_dfa()
            assert rebuilt.is_equivalent(eps_dfa) is True


class TestBrzozowskiMixin:
    def test_brzozowski_minimize_dfa_and_nfa(self, dfa_fig_3_1_d, nfa_fig_7_2_a):
        min_dfa = dfa_fig_3_1_d.brzozowski_minimize()
        assert min_dfa.is_minimal() is True
        assert min_dfa.is_equivalent(dfa_fig_3_1_d) is True
        assert len(min_dfa.states) == 3

        min_nfa = nfa_fig_7_2_a.to_dfa_brzozowski()
        assert min_nfa.is_minimal() is True
        assert min_nfa.is_equivalent(nfa_fig_7_2_a.to_dfa()) is True