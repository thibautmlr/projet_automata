"""Tests unitaires de l'Étape 3 : complétion, complément, produit, relations et minimisation."""

import pytest

from automata_extensions.fa import ExtendedDFA


@pytest.fixture
def dfa_cours_6_bis() -> ExtendedDFA:
    """Fixture ``automate_cours_6_bis`` (Cours 06)."""
    return ExtendedDFA(
        states={"1", "2", "3", "4", "5", "6", "7"},
        input_symbols={"a", "b"},
        transitions={
            "1": {"a": "2", "b": "4"},
            "2": {"a": "3", "b": "5"},
            "3": {"a": "3", "b": "6"},
            "4": {"a": "5", "b": "4"},
            "5": {"a": "6", "b": "7"},
            "6": {"a": "6", "b": "7"},
            "7": {"a": "7", "b": "7"},
        },
        initial_state="1",
        final_states={"1", "2", "3", "5", "6"},
    )


@pytest.fixture
def dfa_fig_6_1_a() -> ExtendedDFA:
    """Fixture ``automate_fig_6_1_a`` (TD6)."""
    return ExtendedDFA(
        states={"1", "2", "3", "4"},
        input_symbols={"a", "b"},
        transitions={
            "1": {"a": "2", "b": "1"},
            "2": {"a": "2", "b": "3"},
            "3": {"a": "4", "b": "3"},
            "4": {"a": "4", "b": "3"},
        },
        initial_state="1",
        final_states={"3", "4"},
    )


@pytest.fixture
def dfa_fig_6_1_b() -> ExtendedDFA:
    """Fixture ``automate_fig_6_1_b`` (TD6)."""
    return ExtendedDFA(
        states={"1", "2", "3", "4"},
        input_symbols={"a", "b"},
        transitions={
            "1": {"a": "2", "b": "1"},
            "2": {"a": "2", "b": "4"},
            "3": {"a": "3", "b": "1"},
            "4": {"a": "3", "b": "4"},
        },
        initial_state="1",
        final_states={"1", "4"},
    )


class TestCompletenessAndComplement:
    """Tests de complétude, complétion ('⊥'), complémentation et universalité."""

    def test_is_complete_and_complete_with_sink(self, dfa_mod3_a):
        assert dfa_mod3_a.is_complete() is True
        assert dfa_mod3_a.complete() == dfa_mod3_a

        partiel = ExtendedDFA(
            states={"0"},
            input_symbols={"a", "b"},
            transitions={"0": {"a": "0"}},
            initial_state="0",
            final_states={"0"},
            allow_partial=True,
        )
        assert partiel.is_complete() is False
        comp = partiel.complete()
        assert comp.is_complete() is True
        assert comp.states == {"0", "⊥"}
        assert comp.transitions["0"] == {"a": "0", "b": "⊥"}
        assert comp.transitions["⊥"] == {"a": "⊥", "b": "⊥"}
        assert comp.accepts("aaa") is True
        assert comp.accepts("ab") is False
        # Immutabilité
        assert partiel.states == {"0"}

    def test_complement_and_universality_doc_fixture(self, dfa_mod3_a):
        c1 = dfa_mod3_a.complement()
        c2 = dfa_mod3_a.complement(minify=True, retain_names=True)
        assert c1.accepts("a") is True
        assert c1.accepts("aaa") is False
        assert sorted(c2.states) == ["0", "1", "2"]
        assert dfa_mod3_a.is_universal() is False

        universal = ExtendedDFA(
            states={"q0"},
            input_symbols={"a", "b"},
            transitions={"q0": {"a": "q0", "b": "q0"}},
            initial_state="q0",
            final_states={"q0"},
        )
        assert universal.is_universal() is True
        assert universal.complement().is_empty() is True

    def test_complement_of_partial_dfa_completes_first(self):
        # Accepte uniquement 'a' sur {a, b} -> complément accepte tout sauf 'a' (y compris 'b', 'ab', '')
        only_a = ExtendedDFA(
            states={"0", "1"},
            input_symbols={"a", "b"},
            transitions={"0": {"a": "1"}, "1": {}},
            initial_state="0",
            final_states={"1"},
            allow_partial=True,
        )
        comp = only_a.complement()
        assert "⊥" in comp.states
        assert comp.accepts("") is True
        assert comp.accepts("a") is False
        assert comp.accepts("b") is True
        assert comp.accepts("ab") is True


class TestProductAndBooleanOperations:
    """Tests du produit cartésien, intersection, union, différence et relations."""

    def test_doc_product_and_intersection(self, dfa_mod3_a):
        assert dfa_mod3_a.intersection(dfa_mod3_a) == dfa_mod3_a
        prod = dfa_mod3_a.product(dfa_mod3_a, is_final=lambda s1, s2: s1 == s2)
        assert sorted(prod.states) == [("0", "0"), ("1", "1"), ("2", "2")]
        assert dfa_mod3_a.union(dfa_mod3_a).accepts("aaa") is True
        assert dfa_mod3_a.difference(dfa_mod3_a).is_empty() is True

    def test_td4_multiple_2_and_not_multiple_3(self, dfa_mod3_a):
        # TD4 Ex 21 : multiple de 2 'a' ET pas multiple de 3 'a'
        mult_2 = ExtendedDFA(
            states={"0", "1"},
            input_symbols={"a", "b"},
            transitions={"0": {"a": "1", "b": "0"}, "1": {"a": "0", "b": "1"}},
            initial_state="0",
            final_states={"0"},
        )
        not_mult_3 = dfa_mod3_a.complement()
        inter = mult_2.intersection(not_mult_3).minify()
        assert len(inter.states) == 6
        assert inter.accepts("") is False
        assert inter.accepts("aa") is True
        assert inter.accepts("aaaa") is True
        assert inter.accepts("aaaaaa") is False

    def test_inclusion_equivalence_disjointness_and_counterexample(
        self, dfa_fig_6_1_a, dfa_fig_6_1_b
    ):
        assert dfa_fig_6_1_a.is_included_in(dfa_fig_6_1_a) is True
        assert dfa_fig_6_1_a.is_equivalent(dfa_fig_6_1_a) is True
        assert dfa_fig_6_1_a.distinguishing_word(dfa_fig_6_1_a) is None

        # TD6 fig 6.1(a) vs 6.1(b) : '1' dans 6.1(a) non final, final dans 6.1(b) -> mot vide '' distingue
        assert dfa_fig_6_1_a.is_equivalent(dfa_fig_6_1_b) is False
        assert dfa_fig_6_1_a.distinguishing_word(dfa_fig_6_1_b) == ""

        # Langages disjoints : nombre pair vs impair de 'a'
        even_a = ExtendedDFA(
            states={"0", "1"},
            input_symbols={"a", "b"},
            transitions={"0": {"a": "1", "b": "0"}, "1": {"a": "0", "b": "1"}},
            initial_state="0",
            final_states={"0"},
        )
        odd_a = even_a.complement()
        assert even_a.is_disjoint(odd_a) is True
        assert even_a.distinguishing_word(odd_a) == ""

    def test_incompatible_alphabets_raise(self, dfa_mod3_a):
        other_alpha = ExtendedDFA(
            states={"0"},
            input_symbols={"a"},
            transitions={"0": {"a": "0"}},
            initial_state="0",
            final_states={"0"},
        )
        with pytest.raises(ValueError):
            dfa_mod3_a.intersection(other_alpha)
        with pytest.raises(ValueError):
            dfa_mod3_a.is_included_in(other_alpha)


class TestIsomorphismMixin:
    """Tests d'isomorphisme structurel entre automates."""

    def test_doc_isomorphism(self, dfa_mod3_a):
        assert dfa_mod3_a.is_isomorphic_to(dfa_mod3_a.minimize(keep_original_names=True)) is True

        renamed = ExtendedDFA(
            states={"A", "B", "C"},
            input_symbols={"a", "b"},
            transitions={
                "A": {"a": "B", "b": "A"},
                "B": {"a": "C", "b": "B"},
                "C": {"a": "A", "b": "C"},
            },
            initial_state="A",
            final_states={"A"},
        )
        iso = dfa_mod3_a.isomorphism_to(renamed)
        assert iso == {"0": "A", "1": "B", "2": "C"}
        assert dfa_mod3_a.is_isomorphic_to(renamed) is True

    def test_non_isomorphic_equivalent_dfas(self):
        # Deux DFA reconnaissant a* : l'un à 1 état, l'autre à 2 états (équivalents mais non isomorphes)
        one_state = ExtendedDFA(
            states={"q0"},
            input_symbols={"a"},
            transitions={"q0": {"a": "q0"}},
            initial_state="q0",
            final_states={"q0"},
        )
        two_states = ExtendedDFA(
            states={"q0", "q1"},
            input_symbols={"a"},
            transitions={"q0": {"a": "q1"}, "q1": {"a": "q1"}},
            initial_state="q0",
            final_states={"q0", "q1"},
        )
        assert one_state.is_equivalent(two_states) is True
        assert one_state.is_isomorphic_to(two_states) is False


class TestMinimizationMixin:
    """Tests de table des paires, classes de Myhill-Nerode, minimize() et minify()."""

    def test_doc_fixture_pair_table_and_minimize(self, dfa_mod3_a):
        assert dfa_mod3_a.distinguishable_states() == {
            frozenset({"1", "2"}),
            frozenset({"1", "0"}),
            frozenset({"0", "2"}),
        }
        assert dfa_mod3_a.pair_table_str(show_round=True) == "  0 1\n1 0\n2 0 1"
        assert dfa_mod3_a.equivalence_classes() == [
            frozenset({"0"}),
            frozenset({"1"}),
            frozenset({"2"}),
        ]
        assert dfa_mod3_a.is_minimal() is True
        assert sorted(map(str, dfa_mod3_a.minimize().states)) == [
            "frozenset({'0'})",
            "frozenset({'1'})",
            "frozenset({'2'})",
        ]
        assert sorted(dfa_mod3_a.minimize(keep_original_names=True).states) == ["0", "1", "2"]

    def test_cours_6_pair_table_and_minimization(self, dfa_cours_6):
        # Vérification exacte de la table de Cours 06 (rounds synchrones)
        expected_table_x = "\n".join(
            [
                "  1 2 3 4 5 6 7",
                "2 X",
                "3 X X",
                "4 X X X",
                "5 . X X X",
                "6 X X X . X",
                "7 X X X X X X",
                "8 X . X X X X X",
            ]
        )
        expected_table_rounds = "\n".join(
            [
                "  1 2 3 4 5 6 7",
                "2 1",
                "3 0 0",
                "4 1 1 0",
                "5 . 1 0 1",
                "6 1 1 0 . 1",
                "7 2 1 0 1 2 1",
                "8 1 . 0 1 1 1 1",
            ]
        )
        assert dfa_cours_6.pair_table_str(show_round=False) == expected_table_x
        assert dfa_cours_6.pair_table_str(show_round=True) == expected_table_rounds
        assert dfa_cours_6.is_minimal() is False

        minimized = dfa_cours_6.minimize()
        assert minimized.states == {
            frozenset({"1", "5"}),
            frozenset({"2", "8"}),
            frozenset({"3"}),
            frozenset({"6"}),
            frozenset({"7"}),
        }
        assert minimized.is_minimal() is True
        assert minimized.is_equivalent(dfa_cours_6) is True

        minified = dfa_cours_6.minify()
        assert minified.states == {"0", "1", "2", "3", "4"}
        assert minified.initial_state == "0"
        assert minified.is_equivalent(dfa_cours_6) is True

    def test_cours_6_bis_minimization(self, dfa_cours_6_bis):
        expected_rounds = "\n".join(
            [
                "  1 2 3 4 5 6",
                "2 1",
                "3 1 .",
                "4 0 0 0",
                "5 2 1 1 0",
                "6 2 1 1 0 .",
                "7 0 0 0 1 0 0",
            ]
        )
        assert dfa_cours_6_bis.pair_table_str(show_round=True) == expected_rounds
        minimized = dfa_cours_6_bis.minimize()
        assert minimized.states == {
            frozenset({"1"}),
            frozenset({"2", "3"}),
            frozenset({"4"}),
            frozenset({"5", "6"}),
            frozenset({"7"}),
        }
        assert minimized.is_equivalent(dfa_cours_6_bis) is True

    def test_single_state_minimization(self):
        single = ExtendedDFA(
            states={"q0"},
            input_symbols={"a"},
            transitions={"q0": {"a": "q0"}},
            initial_state="q0",
            final_states=set(),
        )
        assert single.is_minimal() is True
        assert single.pair_table_str() == ""
        assert single.minimize().states == {frozenset({"q0"})}
        assert single.minify().states == {"0"}