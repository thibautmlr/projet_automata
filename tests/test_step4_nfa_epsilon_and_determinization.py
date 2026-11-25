"""Tests unitaires de l'Étape 4 : fermetures epsilon, élimination, déterminisation et reverse."""

import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedNFA


@pytest.fixture
def nfa_table_8_1_a() -> ExtendedNFA:
    """Fixture ``automate_table_8_1_a`` (TD8)."""
    return ExtendedNFA(
        states={"0", "1", "2", "3", "4"},
        input_symbols={"a", "b"},
        transitions={
            "0": {"": {"1", "3"}},
            "1": {"a": {"2"}},
            "2": {"": {"4"}, "b": {"1"}},
            "3": {"a": {"4"}},
            "4": {"b": {"3"}},
        },
        initial_state="0",
        final_states={"4"},
    )


@pytest.fixture
def nfa_table_8_1_b() -> ExtendedNFA:
    """Fixture ``automate_table_8_1_b`` (TD8)."""
    return ExtendedNFA(
        states={"0", "1", "2", "3", "4"},
        input_symbols={"a", "b"},
        transitions={
            "0": {"": {"1", "3"}},
            "1": {"": {"3"}, "a": {"2"}},
            "2": {"": {"1"}, "b": {"4"}},
            "3": {},
            "4": {"": {"3"}},
        },
        initial_state="0",
        final_states={"4"},
    )


@pytest.fixture
def nfa_fig_8_1_a() -> ExtendedNFA:
    """Fixture ``automate_fig_8_1_a`` (TD8)."""
    return ExtendedNFA(
        states={"0", "1", "2", "3", "4"},
        input_symbols={"a", "b"},
        transitions={
            "0": {"a": {"1"}, "": {"3"}},
            "1": {"a": {"2"}, "b": {"0"}},
            "2": {"b": {"1"}},
            "3": {"a": {"4"}},
            "4": {"b": {"3"}, "": {"2"}},
        },
        initial_state="0",
        final_states={"1", "2", "3", "4"},
    )


@pytest.fixture
def nfa_cours_7_6() -> ExtendedNFA:
    """Fixture ``automate_cours_7_6`` : '1' en avant-avant-dernière position (Cours 07)."""
    return ExtendedNFA(
        states={"0", "1", "2", "3"},
        input_symbols={"0", "1"},
        transitions={
            "0": {"0": {"0"}, "1": {"0", "1"}},
            "1": {"0": {"2"}, "1": {"2"}},
            "2": {"0": {"3"}, "1": {"3"}},
        },
        initial_state="0",
        final_states={"3"},
    )


@pytest.fixture
def dfa_mod3_a() -> ExtendedDFA:
    """DFA reconnaissant les mots sur {a, b} dont le nombre de 'a' est multiple de 3."""
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


class TestEpsilonMixin:
    """Tests de fermeture epsilon d'un état et d'un ensemble d'états."""

    def test_doc_and_td8_epsilon_closures(self, nfa_table_8_1_a, nfa_table_8_1_b):
        assert nfa_table_8_1_a.has_epsilon_transitions() is True
        assert nfa_table_8_1_a.epsilon_closure("0") == {"0", "1", "3"}
        assert nfa_table_8_1_a.epsilon_closure("2") == {"2", "4"}
        assert nfa_table_8_1_a.epsilon_closure_of_set({"1", "2"}) == {"1", "2", "4"}

        assert nfa_table_8_1_b.epsilon_closure("0") == {"0", "1", "3"}
        assert nfa_table_8_1_b.epsilon_closure("2") == {"1", "2", "3"}
        assert nfa_table_8_1_b.epsilon_closure_of_set(set()) == set()

    def test_epsilon_cycle_and_invalid_state(self):
        cyclic_eps = ExtendedNFA(
            states={"p", "q", "r"},
            input_symbols={"a"},
            transitions={
                "p": {"": {"q"}},
                "q": {"": {"p", "r"}},
                "r": {"a": {"r"}},
            },
            initial_state="p",
            final_states={"r"},
        )
        assert cyclic_eps.epsilon_closure("p") == {"p", "q", "r"}
        assert cyclic_eps.epsilon_closure_of_set({"p"}) == {"p", "q", "r"}

        with pytest.raises(ValueError):
            cyclic_eps.epsilon_closure("inexistant")
        with pytest.raises(ValueError):
            cyclic_eps.epsilon_closure_of_set({"p", "inexistant"})


class TestEliminationMixin:
    """Tests de suppression des transitions epsilon, normalisation et élimination d'états."""

    def test_remove_epsilon_transitions_and_eliminate_lambda(
        self, nfa_table_8_1_a, nfa_table_8_1_b, nfa_fig_8_1_a
    ):
        for nfa in (nfa_table_8_1_a, nfa_table_8_1_b, nfa_fig_8_1_a):
            no_eps = nfa.remove_epsilon_transitions()
            assert no_eps.has_epsilon_transitions() is False
            assert no_eps.states == nfa.states
            assert no_eps.to_dfa().is_equivalent(nfa.to_dfa()) is True
            # Surcharge de eliminate_lambda()
            assert nfa.eliminate_lambda() == no_eps

        # Immutabilité de l'automate d'origine
        assert nfa_table_8_1_a.has_epsilon_transitions() is True

    def test_epsilon_accepting_empty_word(self):
        eps_to_final = ExtendedNFA(
            states={"q0", "q1"},
            input_symbols={"a"},
            transitions={"q0": {"": {"q1"}}, "q1": {"a": {"q1"}}},
            initial_state="q0",
            final_states={"q1"},
        )
        cleaned = eps_to_final.remove_epsilon_transitions()
        assert cleaned.has_epsilon_transitions() is False
        assert cleaned.accepts("") is True
        assert cleaned.accepts("aaa") is True

    def test_normalize_and_eliminate_state(self):
        nfa = ExtendedNFA(
            states={"q1", "q2"},
            input_symbols={"a", "b"},
            transitions={
                "q1": {"a": {"q2"}},
                "q2": {"b": {"q2"}},
            },
            initial_state="q1",
            final_states={"q2"},
        )
        norm = nfa.normalize()
        assert norm.initial_state == "q_start"
        assert norm.final_states == {"q_accept"}
        assert norm.predecessors_graph("q_start") == set()
        assert norm.successors_graph("q_accept") == set()
        assert norm.to_dfa().is_equivalent(nfa.to_dfa()) is True

        # Élimination de q1 relié uniquement par ε depuis q_start
        reduced = norm.eliminate_state("q1")
        assert "q1" not in reduced.states
        assert reduced.to_dfa().is_equivalent(nfa.to_dfa()) is True

        # Impossibilité d'éliminer l'état initial ou final
        with pytest.raises(ValueError):
            norm.eliminate_state("q_start")
        with pytest.raises(ValueError):
            norm.eliminate_state("q_accept")


class TestDeterminizationMixin:
    """Tests de déterminisation (construction des sous-ensembles)."""

    def test_td8_determinization_exact_subsets(
        self, nfa_table_8_1_a, nfa_table_8_1_b, nfa_fig_8_1_a
    ):
        dfa_a = nfa_table_8_1_a.to_dfa()
        assert dfa_a == nfa_table_8_1_a.determinize()
        assert dfa_a.states == {
            frozenset({"0", "1", "3"}),
            frozenset({"2", "4"}),
            frozenset({"1", "3"}),
        }
        assert dfa_a.accepts("a") is True
        assert dfa_a.accepts("aba") is True
        assert dfa_a.accepts("ab") is False

        dfa_b = nfa_table_8_1_b.to_dfa()
        assert dfa_b.states == {
            frozenset({"0", "1", "3"}),
            frozenset({"1", "2", "3"}),
            frozenset({"3", "4"}),
        }
        assert dfa_b.accepts("ab") is True
        assert dfa_b.accepts("aaab") is True
        assert dfa_b.accepts("b") is False

        dfa_fig = nfa_fig_8_1_a.to_dfa()
        assert len(dfa_fig.states) == 5
        assert len(dfa_fig.complete().states) == 6
        assert dfa_fig.accepts("") is True
        assert dfa_fig.accepts("b") is False

    def test_cours_7_6_exponential_subset_blowup(self, nfa_cours_7_6):
        dfa = nfa_cours_7_6.to_dfa()
        assert len(dfa.states) == 8
        assert dfa.accepts("100") is True
        assert dfa.accepts("111") is True
        assert dfa.accepts("010") is False
        assert dfa.accepts("10") is False

    def test_determinize_with_renamed_states_and_edge_cases(self, nfa_table_8_1_b):
        renamed = nfa_table_8_1_b.determinize(retain_names=False)
        assert renamed.states == {"0", "1", "2"}
        assert renamed.is_equivalent(nfa_table_8_1_b.to_dfa()) is True

        # Automate à 1 état rejetant tout (langage vide)
        empty_nfa = ExtendedNFA(
            states={"q0"},
            input_symbols={"a"},
            transitions={"q0": {}},
            initial_state="q0",
            final_states=set(),
        )
        empty_dfa = empty_nfa.to_dfa()
        assert empty_dfa.states == {frozenset({"q0"})}
        assert empty_dfa.is_empty() is True


class TestReverseMixin:
    """Tests de renversement (langage miroir) et composition complète."""

    def test_reverse_dfa_and_pipeline(self, dfa_mod3_a):
        rev = dfa_mod3_a.reverse()
        assert isinstance(rev, ExtendedNFA)
        assert rev.accepts("aaa") is True
        assert rev.accepts("baaba") is True
        assert rev.accepts("aa") is False

        # Chaînage complet : reverse -> determinize -> minimize
        minimized_rev = dfa_mod3_a.reverse().determinize().minimize()
        assert minimized_rev.is_minimal() is True
        assert minimized_rev.is_equivalent(dfa_mod3_a) is True

    def test_reverse_nfa_multiple_finals_and_empty(self):
        # Langage {ab, ba} -> miroir {ba, ab}
        nfa = ExtendedNFA(
            states={"0", "1", "2", "3", "4"},
            input_symbols={"a", "b"},
            transitions={
                "0": {"a": {"1"}, "b": {"3"}},
                "1": {"b": {"2"}},
                "3": {"a": {"4"}},
            },
            initial_state="0",
            final_states={"2", "4"},
        )
        rev = nfa.reverse()
        assert rev.accepts("ba") is True
        assert rev.accepts("ab") is True
        assert rev.accepts("aa") is False
        assert rev.reverse().to_dfa().is_equivalent(nfa.to_dfa()) is True

        # Automate sans état final -> langage miroir vide
        no_final = ExtendedDFA(
            states={"q0"},
            input_symbols={"a"},
            transitions={"q0": {"a": "q0"}},
            initial_state="q0",
            final_states=set(),
        )
        assert no_final.reverse().is_empty() is True