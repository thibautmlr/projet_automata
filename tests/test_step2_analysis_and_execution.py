"""Tests unitaires de l'Étape 2 : CFC, cycles, langage vide/fini, simulation, déterminisme et préfixes."""

from automata.base.exceptions import RejectionException
import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedNFA


class TestSCCMixin:
    """Tests des composantes fortement connexes (algorithme de Tarjan)."""

    def test_doc_fixture_strongly_connected(self, dfa_mod3_a):
        assert dfa_mod3_a.strongly_connected_components() == [frozenset({"0", "1", "2"})]
        assert dfa_mod3_a.is_strongly_connected() is True

    def test_multiple_sccs(self, dfa_with_sink_and_unreachable):
        sccs = dfa_with_sink_and_unreachable.strongly_connected_components()
        assert dfa_with_sink_and_unreachable.is_strongly_connected() is False
        assert frozenset({"q0"}) in sccs
        assert frozenset({"q1"}) in sccs
        assert frozenset({"q2"}) in sccs
        assert frozenset({"sink"}) in sccs
        assert frozenset({"unreach1", "unreach2"}) in sccs
        assert len(sccs) == 5

    def test_single_state_scc(self):
        single = ExtendedDFA(
            states={"q0"},
            input_symbols={"a"},
            transitions={"q0": {}},
            initial_state="q0",
            final_states=set(),
            allow_partial=True,
        )
        assert single.strongly_connected_components() == [frozenset({"q0"})]
        assert single.is_strongly_connected() is True


class TestCycleAndFinitenessMixin:
    """Tests de détection de cycles et décision des langages vide et fini/infini."""

    def test_doc_fixture_cycles_and_infinite(self, dfa_mod3_a):
        assert dfa_mod3_a.has_cycle() is True
        assert dfa_mod3_a.has_cycle_from("0") is True
        assert dfa_mod3_a.is_empty() is False
        assert dfa_mod3_a.is_finite() is False
        assert dfa_mod3_a.is_infinite() is True

    def test_acyclic_finite_language(self):
        finite_dfa = ExtendedDFA(
            states={"q0", "q1", "q2"},
            input_symbols={"a", "b"},
            transitions={
                "q0": {"a": "q1"},
                "q1": {"b": "q2"},
                "q2": {},
            },
            initial_state="q0",
            final_states={"q2"},
            allow_partial=True,
        )
        assert finite_dfa.has_cycle() is False
        assert finite_dfa.has_cycle_from("q0") is False
        assert finite_dfa.is_empty() is False
        assert finite_dfa.is_finite() is True
        assert finite_dfa.is_infinite() is False

    def test_cycle_only_in_non_coaccessible_sink_is_still_finite(self):
        # Boucle sur 'sink' non coaccessible -> langage fini {'a'} malgré un cycle dans le graphe
        dfa = ExtendedDFA(
            states={"q0", "q1", "sink"},
            input_symbols={"a", "b"},
            transitions={
                "q0": {"a": "q1", "b": "sink"},
                "q1": {"a": "sink", "b": "sink"},
                "sink": {"a": "sink", "b": "sink"},
            },
            initial_state="q0",
            final_states={"q1"},
        )
        assert dfa.has_cycle() is True
        assert dfa.has_cycle_from("q0") is True
        assert dfa.has_cycle_from("q1") is True
        assert dfa.is_finite() is True

    def test_unreachable_cycle_detected_by_has_cycle_only(self):
        dfa = ExtendedDFA(
            states={"q0", "q1", "u1", "u2"},
            input_symbols={"a"},
            transitions={
                "q0": {"a": "q1"},
                "q1": {},
                "u1": {"a": "u2"},
                "u2": {"a": "u1"},
            },
            initial_state="q0",
            final_states={"q1"},
            allow_partial=True,
        )
        assert dfa.has_cycle() is True
        assert dfa.has_cycle_from("q0") is False
        assert dfa.has_cycle_from("u1") is True
        assert dfa.is_finite() is True

    def test_empty_language_is_empty_and_finite(self):
        empty_dfa = ExtendedDFA(
            states={"q0", "q1"},
            input_symbols={"a"},
            transitions={"q0": {"a": "q0"}, "q1": {"a": "q1"}},
            initial_state="q0",
            final_states={"q1"},
        )
        assert empty_dfa.is_empty() is True
        assert empty_dfa.is_finite() is True
        assert empty_dfa.is_infinite() is False

    def test_nfa_with_pure_epsilon_cycle_is_finite(self):
        # Cycle epsilon q0 <-> q1, puis transition 'a' vers q2 final : L = {'a'} (fini !)
        nfa_eps_cycle = ExtendedNFA(
            states={"q0", "q1", "q2"},
            input_symbols={"a"},
            transitions={
                "q0": {"": {"q1"}, "a": {"q2"}},
                "q1": {"": {"q0"}},
                "q2": {},
            },
            initial_state="q0",
            final_states={"q2"},
        )
        assert nfa_eps_cycle.has_cycle() is True
        assert nfa_eps_cycle.is_empty() is False
        assert nfa_eps_cycle.is_finite() is True


class TestWordAndDeterminismMixin:
    """Tests de reconnaissance de mots (accepts) et de déterminisme (is_deterministic)."""

    def test_accepts_on_dfa_nfa_and_gnfa(self, dfa_mod3_a, nfa_with_epsilon, gnfa_from_mod3):
        assert dfa_mod3_a.accepts("") is True
        assert dfa_mod3_a.accepts("aaa") is True
        assert dfa_mod3_a.accepts("aa") is False

        assert nfa_with_epsilon.accepts("") is True  # via epsilon p -> r
        assert nfa_with_epsilon.accepts("a") is True
        assert nfa_with_epsilon.accepts("ab") is True
        assert nfa_with_epsilon.accepts("b") is False

        assert gnfa_from_mod3.accepts("aaa") is True
        assert gnfa_from_mod3.accepts("a") is False

    def test_is_deterministic(self, dfa_mod3_a, nfa_with_epsilon):
        assert dfa_mod3_a.is_deterministic() is True
        assert dfa_mod3_a.is_deterministic(require_complete=True) is True
        assert nfa_with_epsilon.is_deterministic() is False

        # NFA structurellement déterministe (sans epsilon et au plus 1 cible par symbole)
        det_like_nfa = ExtendedNFA(
            states={"q0", "q1"},
            input_symbols={"a", "b"},
            transitions={
                "q0": {"a": {"q1"}},
                "q1": {"b": {"q0"}},
            },
            initial_state="q0",
            final_states={"q0"},
        )
        assert det_like_nfa.is_deterministic() is True
        assert det_like_nfa.is_deterministic(require_complete=True) is False


class TestExecutionMixin:
    """Tests des traces d'exécution pas à pas sur ExtendedDFA et ExtendedNFA."""

    def test_dfa_execution_trace_doc_fixture(self, dfa_mod3_a):
        assert dfa_mod3_a.execution_trace("") == []
        assert dfa_mod3_a.execution_trace("aab") == [
            ("0", "a", "1"),
            ("1", "a", "2"),
            ("2", "b", "2"),
        ]

    def test_dfa_execution_trace_partial_rejection(self):
        partial_dfa = ExtendedDFA(
            states={"q0", "q1"},
            input_symbols={"a", "b"},
            transitions={"q0": {"a": "q1"}, "q1": {}},
            initial_state="q0",
            final_states={"q1"},
            allow_partial=True,
        )
        assert partial_dfa.execution_trace("a") == [("q0", "a", "q1")]
        with pytest.raises(RejectionException):
            partial_dfa.execution_trace("ab")
        with pytest.raises(RejectionException):
            partial_dfa.execution_trace("c")

    def test_nfa_execution_trace(self, nfa_with_epsilon):
        trace = nfa_with_epsilon.execution_trace("ab")
        assert trace == [
            (frozenset({"p", "r"}), "a", frozenset({"p", "q", "r"})),
            (frozenset({"p", "q", "r"}), "b", frozenset({"q"})),
        ]


class TestPrefixMixin:
    """Tests de clôture par préfixe et extraction du plus grand sous-langage préfixe-clos."""

    def test_doc_fixture_prefix_closed(self, dfa_mod3_a):
        assert dfa_mod3_a.is_prefix_closed() is False
        sub = dfa_mod3_a.prefix_closed_sublanguage()
        assert isinstance(sub, ExtendedDFA)
        assert sub.is_prefix_closed() is True
        assert sub.accepts("") is True
        assert sub.accepts("bbb") is True
        assert sub.accepts("aaa") is False  # 'a' et 'aa' ne sont pas dans L(d)

    def test_already_prefix_closed_language(self):
        # Langage {ε, a, ab} : tous les états utiles sont finaux
        dfa = ExtendedDFA(
            states={"q0", "q1", "q2", "sink"},
            input_symbols={"a", "b"},
            transitions={
                "q0": {"a": "q1", "b": "sink"},
                "q1": {"a": "sink", "b": "q2"},
                "q2": {"a": "sink", "b": "sink"},
                "sink": {"a": "sink", "b": "sink"},
            },
            initial_state="q0",
            final_states={"q0", "q1", "q2"},
        )
        assert dfa.is_prefix_closed() is True
        sub = dfa.prefix_closed_sublanguage()
        assert sub.states == {"q0", "q1", "q2"}
        assert sub.accepts("") is True
        assert sub.accepts("a") is True
        assert sub.accepts("ab") is True
        assert sub.accepts("aba") is False

    def test_non_final_initial_state_prefix_sublanguage_is_empty(self):
        dfa = ExtendedDFA(
            states={"q0", "q1"},
            input_symbols={"a"},
            transitions={"q0": {"a": "q1"}, "q1": {"a": "q1"}},
            initial_state="q0",
            final_states={"q1"},
        )
        assert dfa.is_prefix_closed() is False
        sub = dfa.prefix_closed_sublanguage()
        assert sub.is_empty() is True
        assert sub.is_prefix_closed() is True

    def test_empty_language_is_vacuously_prefix_closed(self):
        empty_dfa = ExtendedDFA(
            states={"q0"},
            input_symbols={"a"},
            transitions={"q0": {"a": "q0"}},
            initial_state="q0",
            final_states=set(),
        )
        assert empty_dfa.is_prefix_closed() is True
        assert empty_dfa.prefix_closed_sublanguage().is_empty() is True