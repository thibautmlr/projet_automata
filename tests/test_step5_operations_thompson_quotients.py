"""Tests unitaires de l'Étape 5 : opérations rationnelles, Thompson, quotients et résiduels."""

import pytest
from automata_extensions.fa import ExtendedDFA, ExtendedNFA


@pytest.fixture
def dfa_mod3_a() -> ExtendedDFA:
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


class TestLanguageOperationsMixin:
    def test_union_concatenation_kleene_star(self):
        n1 = ExtendedNFA.from_regex("a", input_symbols={"a", "b"})
        n2 = ExtendedNFA.from_regex("b", input_symbols={"a", "b"})

        u = n1.union(n2)
        assert u.accepts("a") is True
        assert u.accepts("b") is True
        assert u.accepts("ab") is False

        c = n1.concatenation(n2)
        assert c.accepts("ab") is True
        assert c.accepts("a") is False

        k = c.kleene_star()
        assert k.accepts("") is True
        assert k.accepts("ab") is True
        assert k.accepts("ababab") is True
        assert k.accepts("aba") is False


class TestThompsonMixin:
    def test_from_regex_standard_and_specials(self):
        nfa = ExtendedNFA.from_regex("(a|b)*abb", input_symbols={"a", "b"})
        assert isinstance(nfa, ExtendedNFA)
        assert nfa.accepts("abb") is True
        assert nfa.accepts("aabb") is True
        assert nfa.accepts("ab") is False

        plus_nfa = ExtendedNFA.from_regex("a+b?", input_symbols={"a", "b"})
        assert plus_nfa.accepts("") is False
        assert plus_nfa.accepts("a") is True
        assert plus_nfa.accepts("aaab") is True

        eps_nfa = ExtendedNFA.from_regex("()", input_symbols={"a"})
        assert eps_nfa.accepts("") is True
        assert eps_nfa.accepts("a") is False

        empty_nfa = ExtendedNFA.from_regex("∅", input_symbols={"a"})
        assert empty_nfa.is_empty() is True


class TestQuotientAndResidualMixin:
    def test_left_and_right_quotient_word(self, dfa_mod3_a):
        lq = dfa_mod3_a.left_quotient_word("a")
        assert lq.accepts("aa") is True
        assert lq.accepts("baab") is True
        assert lq.accepts("") is False

        rq = dfa_mod3_a.right_quotient_word("a")
        assert rq.accepts("aa") is True
        assert rq.accepts("abab") is True
        assert rq.accepts("ababa") is False
        assert rq.accepts("") is False

    def test_residual_automaton(self, dfa_mod3_a):
        res = dfa_mod3_a.residual_automaton()
        assert sorted(res.states) == ["q0", "q1", "q2"]
        assert res.is_equivalent(dfa_mod3_a) is True