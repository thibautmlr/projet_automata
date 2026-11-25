from __future__ import annotations
from typing import Dict, List, Optional, Set, Tuple


class ThompsonMixin:
    """Construction de Thompson : conversion d'une expression régulière en ExtendedNFA."""

    @classmethod
    def from_regex(cls, regex: str, input_symbols: Optional[Set[str]] = None):
        """
        Construit un ExtendedNFA reconnaissant le langage de `regex` par l'algorithme de Thompson.

        Syntaxe supportée :
        - symboles littéraux (1 caractère)
        - '()' ou 'ε' : mot vide
        - '∅' : langage vide
        - '|' : union
        - concaténation implicite
        - '*' (étoile de Kleene), '+' (plus), '?' (optionnel)
        - parenthèses '(...)'
        """
        counter = 0

        def new_state() -> str:
            nonlocal counter
            s = f"q{counter}"
            counter += 1
            return s

        tokens: List[str] = []
        i = 0
        while i < len(regex):
            ch = regex[i]
            if ch.isspace():
                i += 1
                continue
            if ch == "(" and i + 1 < len(regex) and regex[i + 1] == ")":
                tokens.append("EPS")
                i += 2
                continue
            if ch == "ε":
                tokens.append("EPS")
            elif ch == "∅":
                tokens.append("EMPTY")
            elif ch in {"|", "*", "+", "?", "(", ")"}:
                tokens.append(ch)
            else:
                tokens.append(f"SYM:{ch}")
            i += 1

        def is_atom_end(tok: str) -> bool:
            return tok.startswith("SYM:") or tok in {"EPS", "EMPTY", ")", "*", "+", "?"}

        def is_atom_start(tok: str) -> bool:
            return tok.startswith("SYM:") or tok in {"EPS", "EMPTY", "("}

        with_concat: List[str] = []
        for idx, tok in enumerate(tokens):
            with_concat.append(tok)
            if idx + 1 < len(tokens) and is_atom_end(tok) and is_atom_start(tokens[idx + 1]):
                with_concat.append(".")

        precedence = {"|": 1, ".": 2, "*": 3, "+": 3, "?": 3}
        output: List[str] = []
        ops: List[str] = []

        for tok in with_concat:
            if tok.startswith("SYM:") or tok in {"EPS", "EMPTY"}:
                output.append(tok)
            elif tok == "(":
                ops.append(tok)
            elif tok == ")":
                while ops and ops[-1] != "(":
                    output.append(ops.pop())
                if not ops:
                    raise ValueError(f"Parenthèses non équilibrées dans {regex!r}.")
                ops.pop()
            else:
                while ops and ops[-1] != "(" and precedence.get(ops[-1], 0) >= precedence[tok]:
                    output.append(ops.pop())
                ops.append(tok)

        while ops:
            op = ops.pop()
            if op == "(":
                raise ValueError(f"Parenthèses non équilibrées dans {regex!r}.")
            output.append(op)

        transitions: Dict[str, Dict[str, Set[str]]] = {}
        all_states: Set[str] = set()
        detected_symbols: Set[str] = set()

        def add_edge(u: str, sym: str, v: str) -> None:
            all_states.update({u, v})
            transitions.setdefault(u, {}).setdefault(sym, set()).add(v)
            transitions.setdefault(v, {})

        if not output:
            s0 = new_state()
            all_states.add(s0)
            transitions[s0] = {}
            syms = set(input_symbols) if input_symbols is not None else set()
            return cls(
                states=all_states,
                input_symbols=syms,
                transitions=transitions,
                initial_state=s0,
                final_states={s0},
            )

        stack: List[Tuple[str, str]] = []
        for tok in output:
            if tok.startswith("SYM:"):
                sym = tok[4:]
                detected_symbols.add(sym)
                s, e = new_state(), new_state()
                add_edge(s, sym, e)
                stack.append((s, e))
            elif tok == "EPS":
                s, e = new_state(), new_state()
                add_edge(s, "", e)
                stack.append((s, e))
            elif tok == "EMPTY":
                s, e = new_state(), new_state()
                all_states.update({s, e})
                transitions.setdefault(s, {})
                transitions.setdefault(e, {})
                stack.append((s, e))
            elif tok == ".":
                s2, e2 = stack.pop()
                s1, e1 = stack.pop()
                add_edge(e1, "", s2)
                stack.append((s1, e2))
            elif tok == "|":
                s2, e2 = stack.pop()
                s1, e1 = stack.pop()
                s, e = new_state(), new_state()
                add_edge(s, "", s1)
                add_edge(s, "", s2)
                add_edge(e1, "", e)
                add_edge(e2, "", e)
                stack.append((s, e))
            elif tok == "*":
                s1, e1 = stack.pop()
                s, e = new_state(), new_state()
                add_edge(s, "", s1)
                add_edge(s, "", e)
                add_edge(e1, "", s1)
                add_edge(e1, "", e)
                stack.append((s, e))
            elif tok == "+":
                s1, e1 = stack.pop()
                s, e = new_state(), new_state()
                add_edge(s, "", s1)
                add_edge(e1, "", s1)
                add_edge(e1, "", e)
                stack.append((s, e))
            elif tok == "?":
                s1, e1 = stack.pop()
                s, e = new_state(), new_state()
                add_edge(s, "", s1)
                add_edge(s, "", e)
                add_edge(e1, "", e)
                stack.append((s, e))

        if len(stack) != 1:
            raise ValueError(f"Expression régulière invalide : {regex!r}.")

        start_state, end_state = stack[0]
        final_symbols = set(input_symbols) if input_symbols is not None else detected_symbols
        if not detected_symbols.issubset(final_symbols):
            raise ValueError(
                f"Symboles inconnus {detected_symbols - final_symbols} hors de input_symbols."
            )

        return cls(
            states=all_states,
            input_symbols=final_symbols,
            transitions=transitions,
            initial_state=start_state,
            final_states={end_state},
        )