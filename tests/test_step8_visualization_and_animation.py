"""Tests unitaires de l'Étape 8 : visualisation (DOT, TikZ, LaTeX, SVG/PNG/PDF) et animation."""

from types import SimpleNamespace
from unittest.mock import patch
import pytest

from automata_extensions.fa import ExtendedDFA, ExtendedNFA


@pytest.fixture
def dfa_simple() -> ExtendedDFA:
    return ExtendedDFA(
        states={"q0", "q1"},
        input_symbols={"a", "b"},
        transitions={
            "q0": {"a": "q1", "b": "q0"},
            "q1": {"a": "q1", "b": "q0"},
        },
        initial_state="q0",
        final_states={"q1"},
    )


class TestVisualizationMixin:
    def test_dot_tikz_and_latex_generation(self, dfa_simple):
        dot_str = dfa_simple.to_dot()
        assert dot_str == dfa_simple.dot()
        assert "digraph Automaton" in dot_str
        assert "doublecircle" in dot_str
        assert "__start__ ->" in dot_str

        tikz_str = dfa_simple.to_tikz()
        assert tikz_str == dfa_simple.tikz() == dfa_simple.latex_tikz()
        assert r"\begin{tikzpicture}" in tikz_str
        assert r"\end{tikzpicture}" in tikz_str
        assert "accepting" in tikz_str

        latex_str = dfa_simple.latex()
        assert r"\documentclass" in latex_str
        assert tikz_str in latex_str

    def test_nfa_epsilon_and_frozenset_labels(self):
        nfa = ExtendedNFA(
            states={"0", "1"},
            input_symbols={"a"},
            transitions={"0": {"": {"1"}}, "1": {"a": {"1"}}},
            initial_state="0",
            final_states={"1"},
        )
        assert "ε" in nfa.to_dot()
        assert r"\varepsilon" in nfa.to_tikz()

        det = nfa.to_dfa()
        assert "{0, 1}" in det.to_dot()

    def test_svg_png_pdf_export_via_graphviz_subprocess(self, dfa_simple, tmp_path):
        fake_svg = b'<svg xmlns="http://www.w3.org/2000/svg"></svg>'

        with patch.object(ExtendedDFA, "_find_graphviz_bin", return_value="dot"), patch(
            "subprocess.run",
            return_value=SimpleNamespace(returncode=0, stdout=fake_svg, stderr=b""),
        ):
            svg_out = tmp_path / "automate.svg"
            content = dfa_simple.to_svg(svg_out)
            assert "<svg" in content
            assert svg_out.read_text(encoding="utf-8") == content

            pdf_bytes = dfa_simple.to_pdf()
            assert pdf_bytes == fake_svg


class TestAnimationMixin:
    def test_run_and_animate_dfa_and_nfa(self, dfa_simple, tmp_path):
        trace_ok = dfa_simple.run("ba")
        assert trace_ok == "q0 --b--> q0 --a--> q1 (accept)"

        trace_ko = dfa_simple.run("ab")
        assert trace_ko == "q0 --a--> q1 --b--> q0 (reject)"

        html_path = tmp_path / "anim.html"
        html_code = dfa_simple.animate("ba", filename=html_path)
        assert "<!DOCTYPE html>" in html_code
        assert "ACCEPTÉ" in html_code
        assert html_path.exists()

        nfa = ExtendedNFA.from_regex("a*b", input_symbols={"a", "b"})
        nfa_trace = nfa.run("ab")
        assert nfa_trace.endswith("(accept)")