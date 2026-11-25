"""Tests unitaires de l'Étape 1 : socle ExtendedFA, graphe, parcours, accessibilité et émondage."""

from automata.fa.dfa import DFA as BaseDFA
import pytest

import automata_extensions  # noqa: F401
from automata_extensions.fa import ExtendedDFA, ExtendedFA, ExtendedGNFA, ExtendedNFA


class TestArchitectureAndPatches:
    """Vérifie l'héritage MRO, copy(), input_parameters et le correctif cached_method."""

    def test_mro_and_inheritance(self, dfa_mod3_a, nfa_with_epsilon, gnfa_from_mod3):
        assert isinstance(dfa_mod3_a, ExtendedFA)
        assert isinstance(dfa_mod3_a, BaseDFA)
        assert isinstance(nfa_with_epsilon, ExtendedFA)
        assert isinstance(gnfa_from_mod3, ExtendedFA)
        assert ExtendedDFA.__mro__.index(ExtendedFA) < ExtendedDFA.__mro__.index(BaseDFA)

    def test_input_parameters_and_copy(self, dfa_mod3_a):
        assert sorted(dfa_mod3_a.input_parameters.keys()) == [
            "allow_partial",
            "final_states",
            "initial_state",
            "input_symbols",
            "states",
            "transitions",
        ]
        cloned = dfa_mod3_a.copy()
        assert cloned == dfa_mod3_a
        assert cloned is not dfa_mod3_a
        assert cloned.states is not dfa_mod3_a.states

    def test_patch_cached_method_chained_temporary(self, dfa_mod3_a):
        # Ne doit pas lever RuntimeError: weakly-referenced object no longer exists
        assert (dfa_mod3_a - dfa_mod3_a).isempty() is True

        pure_d = BaseDFA(
            states={"0", "1"},
            input_symbols={"a"},
            transitions={"0": {"a": "1"}, "1": {"a": "0"}},
            initial_state="0",
            final_states={"0"},
        )
        assert (pure_d - pure_d).isempty() is True


class TestGraphMixin:
    """Tests des méthodes predecessors_graph et successors_graph."""

    def test_nominal_doc_fixture(self, dfa_mod3_a):
        assert dfa_mod3_a.predecessors_graph("1") == {"0", "1"}
        assert dfa_mod3_a.successors_graph("1") == {"1", "2"}

    def test_nfa_with_epsilon_edges(self, nfa_with_epsilon):
        # 'p' a 'a' -> {'p', 'q'} et '' -> {'r'}
        assert nfa_with_epsilon.successors_graph("p") == {"p", "q", "r"}
        assert nfa_with_epsilon.predecessors_graph("r") == {"p", "r"}
        assert nfa_with_epsilon.predecessors_graph("q") == {"p", "q"}

    def test_gnfa_edges(self, gnfa_from_mod3):
        assert "0" in gnfa_from_mod3.successors_graph(gnfa_from_mod3.initial_state)

    def test_invalid_state_raises(self, dfa_mod3_a):
        with pytest.raises(ValueError):
            dfa_mod3_a.successors_graph("inexistant")
        with pytest.raises(ValueError):
            dfa_mod3_a.predecessors_graph("inexistant")


class TestTraversalMixin:
    """Tests des parcours DFS (itératif et récursif) et BFS."""

    def test_doc_fixture_bfs_and_dfs(self, dfa_mod3_a):
        assert dfa_mod3_a.bfs() == ["0", "1", "2"]
        assert dfa_mod3_a.dfs() == ["0", "1", "2"]
        assert dfa_mod3_a.dfs(recursive=True) == ["0", "1", "2"]

    def test_bfs_vs_dfs_branching_graph(self):
        dfa = ExtendedDFA(
            states={"0", "1", "2", "3"},
            input_symbols={"a", "b"},
            transitions={
                "0": {"a": "1", "b": "2"},
                "1": {"a": "3"},
                "2": {},
                "3": {},
            },
            initial_state="0",
            final_states={"3"},
            allow_partial=True,
        )
        # BFS visite par niveaux : 0 -> [1, 2] -> [3]
        assert dfa.bfs() == ["0", "1", "2", "3"]
        # DFS plonge sur la première branche '1' -> '3' avant '2'
        assert dfa.dfs() == ["0", "1", "3", "2"]
        assert dfa.dfs(recursive=True) == ["0", "1", "3", "2"]

    def test_traversal_from_custom_start(self, dfa_with_sink_and_unreachable):
        assert set(dfa_with_sink_and_unreachable.bfs(start="unreach1")) == {
            "unreach1",
            "unreach2",
            "q2",
            "sink",
        }


class TestAccessibilityAndTrim:
    """Tests d'accessibilité, coaccessibilité, états utiles et émondage (trim)."""

    def test_nominal_doc_fixtures(self, dfa_mod3_a, nfa_with_epsilon):
        assert dfa_mod3_a.accessible_states() == {"0", "1", "2"}
        assert dfa_mod3_a.is_accessible("2") is True
        assert dfa_mod3_a.coaccessible_states() == {"0", "1", "2"}
        assert dfa_mod3_a.is_coaccessible("0") is True
        assert dfa_mod3_a.useful_states() == {"0", "1", "2"}
        assert dfa_mod3_a.is_trim() is True
        assert dfa_mod3_a.reachable_states("1") == {"0", "1", "2"}

        assert nfa_with_epsilon.accessible_states() == {"p", "q", "r"}
        assert nfa_with_epsilon.coaccessible_states() == {"p", "q", "r"}
        assert nfa_with_epsilon.is_trim() is True

    def test_cours_6_automaton(self, dfa_cours_6):
        # L'état '4' n'a aucune transition entrante dans automate_cours_6
        expected_accessible = {"1", "2", "3", "5", "6", "7", "8"}
        assert dfa_cours_6.accessible_states() == expected_accessible
        assert dfa_cours_6.coaccessible_states() == {"1", "2", "3", "4", "5", "6", "7", "8"}
        assert dfa_cours_6.is_accessible("4") is False
        assert dfa_cours_6.is_trim() is False
        assert dfa_cours_6.trim().states == expected_accessible

    def test_unreachable_and_sink_states_trim(self, dfa_with_sink_and_unreachable):
        orig_states = set(dfa_with_sink_and_unreachable.states)

        assert dfa_with_sink_and_unreachable.accessible_states() == {"q0", "q1", "q2", "sink"}
        assert dfa_with_sink_and_unreachable.is_accessible("unreach1") is False

        assert dfa_with_sink_and_unreachable.coaccessible_states() == {
            "q0",
            "q1",
            "q2",
            "unreach1",
            "unreach2",
        }
        assert dfa_with_sink_and_unreachable.is_coaccessible("sink") is False

        assert dfa_with_sink_and_unreachable.useful_states() == {"q0", "q1", "q2"}
        assert dfa_with_sink_and_unreachable.is_trim() is False

        trimmed = dfa_with_sink_and_unreachable.trim()
        assert trimmed.states == {"q0", "q1", "q2"}
        assert trimmed.is_trim() is True
        assert trimmed.accepts_input("aa") is True
        assert trimmed.accepts_input("ab") is False
        # Immutabilité : self n'a pas été modifié
        assert dfa_with_sink_and_unreachable.states == orig_states

    def test_single_state_automaton(self):
        single = ExtendedDFA(
            states={"q0"},
            input_symbols={"a"},
            transitions={"q0": {"a": "q0"}},
            initial_state="q0",
            final_states={"q0"},
        )
        assert single.accessible_states() == {"q0"}
        assert single.coaccessible_states() == {"q0"}
        assert single.useful_states() == {"q0"}
        assert single.is_trim() is True
        assert single.trim() == single

    def test_empty_language_automaton_trim(self):
        empty_lang_dfa = ExtendedDFA(
            states={"q0", "q1"},
            input_symbols={"a"},
            transitions={"q0": {"a": "q0"}, "q1": {"a": "q1"}},
            initial_state="q0",
            final_states={"q1"},
        )
        assert empty_lang_dfa.accessible_states() == {"q0"}
        assert empty_lang_dfa.coaccessible_states() == {"q1"}
        assert empty_lang_dfa.useful_states() == set()
        assert empty_lang_dfa.is_trim() is False

        trimmed = empty_lang_dfa.trim()
        assert trimmed.states == {"q0"}
        assert trimmed.final_states == set()
        assert trimmed.isempty() is True


class TestSubautomatonMixin:
    """Tests d'extraction de sous-automates induits."""

    def test_induced_subautomaton_doc_fixture(self, dfa_mod3_a):
        sub = dfa_mod3_a.induced_subautomaton({"0", "1"})
        assert isinstance(sub, ExtendedDFA)
        assert sub.states == {"0", "1"}
        assert sub.final_states == {"0"}
        assert sub.transitions == {
            "0": {"a": "1", "b": "0"},
            "1": {"b": "1"},
        }
        # 'aa' allait vers '2', donc n'est plus accepté dans le sous-automate
        assert sub.accepts_input("b") is True
        assert sub.accepts_input("aaa") is False

    def test_induced_subautomaton_custom_initial(self, dfa_with_sink_and_unreachable):
        comp = dfa_with_sink_and_unreachable.induced_subautomaton(
            {"unreach1", "unreach2", "q2"},
            initial_state="unreach1",
        )
        assert comp.initial_state == "unreach1"
        assert comp.accepts_input("b") is True
        assert comp.accepts_input("aab") is True
        assert comp.accepts_input("ab") is False

    def test_induced_subautomaton_errors(self, dfa_mod3_a):
        with pytest.raises(ValueError):
            dfa_mod3_a.induced_subautomaton(set())
        with pytest.raises(ValueError):
            dfa_mod3_a.induced_subautomaton({"0", "999"})
        with pytest.raises(ValueError):
            dfa_mod3_a.induced_subautomaton({"1", "2"})  # initial_state '0' absent