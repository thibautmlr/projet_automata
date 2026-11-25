"""Tests de validation globale : imports publics, correctifs MRO/cached_method et pipeline complet."""

from pathlib import Path
from automata.fa.dfa import DFA
import automata_extensions
from automata_extensions.fa import ExtendedDFA, ExtendedGNFA, ExtendedNFA
from automata_extensions.grammar import DerivationStep, Grammar


def test_public_exports_and_cached_method_patch():
    assert hasattr(automata_extensions, "ExtendedDFA")
    assert hasattr(automata_extensions, "ExtendedNFA")
    assert hasattr(automata_extensions, "ExtendedGNFA")

    # Vérifie que le patch sur @cached_method permet les appels chaînés sur objets temporaires
    pure_dfa = DFA(
        states={"0", "1"},
        input_symbols={"a"},
        transitions={"0": {"a": "1"}, "1": {"a": "0"}},
        initial_state="0",
        final_states={"0"},
    )
    assert (pure_dfa - pure_dfa).isempty() is True


def test_end_to_end_pipeline():
    # Regex -> Thompson NFA -> DFA -> Minify -> Grammar -> NFA -> Regex -> Equivalence
    nfa = ExtendedNFA.from_regex("(a|b)*abb", input_symbols={"a", "b"})
    dfa = nfa.to_dfa().minify()
    gram = dfa.to_grammar()

    assert isinstance(gram, Grammar)
    deriv = gram.derive("aabb")
    assert deriv is not None and all(isinstance(step, DerivationStep) for step in deriv)

    rebuilt = ExtendedNFA.from_grammar(gram).to_dfa()
    assert rebuilt.is_equivalent(dfa) is True

    regex_back = dfa.to_regex_optimum()
    dfa_from_back = ExtendedNFA.from_regex(regex_back, input_symbols={"a", "b"}).to_dfa()
    assert dfa_from_back.is_equivalent(dfa) is True


def test_project_deliverables_exist():
    root = Path(__file__).resolve().parent.parent
    assert (root / "pyproject.toml").is_file()
    assert (root / "README.md").is_file()