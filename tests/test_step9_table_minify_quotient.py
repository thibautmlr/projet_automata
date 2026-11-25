"""Tests unitaires de l'Étape 9 : minify(), pair_table_str(), quotient_by() et counterexample()."""

import pytest
from automata_extensions.fa import ExtendedDFA, ExtendedNFA


@pytest.fixture
def dfa_fig_6_1_a() -> ExtendedDFA:
    """Automate fig 6.1a du cours (états 3 et 4 équivalents, 3 classes au total)."""
    return ExtendedDFA(
        states={"1", "2", "3", "4"},
        input_symbols={"a", "b"},
        transitions={
            "1": {"a": "2", "b": "3"},
            "2": {"a": "4", "b": "2"},
            "3": {"a": "4", "b": "3"},
            "4": {"a": "3", "b": "4"},
        },
        initial_state="1",
        final_states={"3", "4"},
    )


class TestMinimizationExtraMixin:
    def test_minify_renames_states_and_preserves_language(self):
        dfa = ExtendedNFA.from_regex("(a|b)*abaa(a|b)*", input_symbols={"a", "b"}).to_dfa()
        mini = dfa.minify()
        assert mini.states == {"0", "1", "2", "3", "4"}
        assert mini.initial_state == "0"
        assert mini.is_minimal() is True
        assert mini.is_equivalent(dfa) is True

    def test_pair_table_str_and_print(self, dfa_fig_6_1_a, capsys):
        expected_rounds = "  1 2 3\n2 1\n3 0 0\n4 0 0 ."
        expected_marks = "  1 2 3\n2 X\n3 X X\n4 X X ."

        assert dfa_fig_6_1_a.pair_table_str(show_round=True) == expected_rounds
        assert dfa_fig_6_1_a.pair_table_str(show_round=False) == expected_marks

        dfa_fig_6_1_a.print_pair_table(show_round=True)
        captured = capsys.readouterr()
        assert captured.out.strip() == expected_rounds.strip()

    def test_quotient_by_equivalence_classes_and_mapping(self, dfa_fig_6_1_a):
        classes = dfa_fig_6_1_a.equivalence_classes()
        quot = dfa_fig_6_1_a.quotient_by(classes)
        assert len(quot.states) == 3
        assert quot.is_equivalent(dfa_fig_6_1_a) is True

        # Format dictionnaire {état: représentant}
        quot_map = dfa_fig_6_1_a.quotient_by({"1": "1", "2": "2", "3": "3", "4": "3"})
        assert sorted(quot_map.states) == ["1", "2", "3"]
        assert quot_map.is_equivalent(dfa_fig_6_1_a) is True

        # Partition non congruente -> ValueError
        with pytest.raises(ValueError):
            dfa_fig_6_1_a.quotient_by([{"1", "3"}, {"2", "4"}])

    def test_counterexample(self, dfa_fig_6_1_a):
        assert dfa_fig_6_1_a.counterexample(dfa_fig_6_1_a.minify()) is None

        other = ExtendedDFA(
            states={"q0"},
            input_symbols={"a", "b"},
            transitions={"q0": {"a": "q0", "b": "q0"}},
            initial_state="q0",
            final_states=set(),
        )
        ce = dfa_fig_6_1_a.counterexample(other)
        assert ce == "b"