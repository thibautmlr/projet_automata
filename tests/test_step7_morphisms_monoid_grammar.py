"""Tests unitaires de l'Étape 7 : morphismes, monoïde syntaxique et grammaires régulières."""

import pytest
from automata_extensions.fa import ExtendedDFA, ExtendedNFA
from automata_extensions.grammar import DerivationStep, Grammar


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


class TestMorphismMixin:
    def test_apply_and_inverse_morphism(self, dfa_mod3_a):
        # Morphisme h : a -> xy, b -> ""
        h = {"a": "xy", "b": ""}
        img = dfa_mod3_a.apply_morphism(h)
        assert isinstance(img, ExtendedNFA)
        assert img.accepts("") is True
        assert img.accepts("xyxyxy") is True
        assert img.accepts("xyxy") is False

        # Morphisme réciproque g : u -> aa, v -> b sur dfa_mod3_a (nombre de 'u' multiple de 3)
        g = {"u": "aa", "v": "b"}
        inv = dfa_mod3_a.inverse_morphism(g)
        assert inv.accepts("uuu") is True
        assert inv.accepts("vuvuvuv") is True
        assert inv.accepts("vuvuv") is False
        assert inv.accepts("u") is False


class TestSyntacticMonoidMixin:
    def test_syntactic_monoid_mod3(self, dfa_mod3_a):
        monoid = dfa_mod3_a.syntactic_monoid()
        assert len(monoid) == 3
        assert "" in monoid.values()
        assert "a" in monoid.values()
        assert "aa" in monoid.values()


class TestGrammarAndGrammarMixin:
    def test_fa_to_grammar_and_back(self, dfa_mod3_a):
        gram = dfa_mod3_a.to_grammar()
        assert isinstance(gram, Grammar)
        assert gram.is_regular() is True
        assert gram.accepts("") is True
        assert gram.accepts("baaba") is True
        assert gram.accepts("aa") is False

        steps = gram.derive("aaa")
        assert steps is not None
        assert all(isinstance(s, DerivationStep) for s in steps)
        assert steps[-1].current == "aaa"

        rebuilt_nfa = ExtendedNFA.from_grammar(gram)
        rebuilt_dfa = ExtendedDFA.from_grammar(gram)
        assert rebuilt_nfa.to_dfa().is_equivalent(dfa_mod3_a) is True
        assert rebuilt_dfa.is_equivalent(dfa_mod3_a) is True