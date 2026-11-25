from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple


@dataclass(frozen=True)
class DerivationStep:
    """Représente une étape de dérivation dans une grammaire formelle."""

    current: str
    rule_lhs: str
    rule_rhs: str
    position: int


class Grammar:
    """Grammaire formelle G = (V, Sigma, P, S) avec support des grammaires régulières."""

    def __init__(
        self,
        variables: Set[str],
        terminals: Set[str],
        productions: Dict[str, Set[str]],
        start_symbol: str,
    ) -> None:
        if start_symbol not in variables:
            raise ValueError(f"Le symbole initial {start_symbol!r} doit appartenir à variables.")
        if not variables.isdisjoint(terminals):
            raise ValueError("Les ensembles variables et terminals doivent être disjoints.")

        self.variables: Set[str] = set(variables)
        self.terminals: Set[str] = set(terminals)
        self.start_symbol: str = start_symbol
        self.productions: Dict[str, Set[str]] = {v: set() for v in self.variables}

        for lhs, rhs_set in productions.items():
            if lhs not in self.variables:
                raise ValueError(f"Membre gauche invalide : {lhs!r} n'est pas une variable.")
            for rhs in rhs_set:
                for ch in rhs:
                    if ch not in self.variables and ch not in self.terminals:
                        raise ValueError(
                            f"Symbole inconnu {ch!r} dans la production {lhs} -> {rhs!r}."
                        )
                self.productions[lhs].add(rhs)

    def is_right_linear(self) -> bool:
        """Teste si la grammaire est linéaire droite (A -> wB ou A -> w avec w in Sigma*)."""
        for rhs_set in self.productions.values():
            for rhs in rhs_set:
                for idx, ch in enumerate(rhs):
                    if ch in self.variables and idx != len(rhs) - 1:
                        return False
        return True

    def is_regular(self) -> bool:
        """Teste si la grammaire est régulière (linéaire droite)."""
        return self.is_right_linear()

    def to_nfa(self):
        """
        Convertit une grammaire régulière (linéaire droite) en ExtendedNFA équivalent.
        """
        from ..fa.nfa import ExtendedNFA

        if not self.is_right_linear():
            raise ValueError("La conversion en automate fini exige une grammaire linéaire droite.")

        q_accept = "q_accept"
        while q_accept in self.variables:
            q_accept = f"_{q_accept}"

        states: Set[object] = set(self.variables) | {q_accept}
        transitions: Dict[object, Dict[str, Set[object]]] = {q: {} for q in states}
        aux_idx = 0

        def add_word_edge(src: object, word: str, dst: object) -> None:
            nonlocal aux_idx
            if word == "":
                transitions[src].setdefault("", set()).add(dst)
                return
            curr = src
            for ch in word[:-1]:
                mid = ("G", aux_idx)
                aux_idx += 1
                states.add(mid)
                transitions[mid] = {}
                transitions[curr].setdefault(ch, set()).add(mid)
                curr = mid
            transitions[curr].setdefault(word[-1], set()).add(dst)

        for lhs, rhs_set in self.productions.items():
            for rhs in rhs_set:
                if rhs == "":
                    add_word_edge(lhs, "", q_accept)
                elif rhs[-1] in self.variables:
                    prefix, next_var = rhs[:-1], rhs[-1]
                    add_word_edge(lhs, prefix, next_var)
                else:
                    add_word_edge(lhs, rhs, q_accept)

        return ExtendedNFA(
            states=states,
            input_symbols=set(self.terminals),
            transitions=transitions,
            initial_state=self.start_symbol,
            final_states={q_accept},
        )

    def derive(self, word: str, max_steps: int = 500) -> Optional[List[DerivationStep]]:
        """
        Recherche une dérivation la plus à gauche produisant `word`.
        Retourne la liste des DerivationStep ou None si le mot n'est pas dérivable.
        """
        if any(ch not in self.terminals for ch in word):
            return None

        queue: deque[Tuple[str, List[DerivationStep]]] = deque([(self.start_symbol, [])])
        visited: Set[str] = {self.start_symbol}
        max_len = max(len(word) + len(self.variables) + 2, 10)

        steps_done = 0
        while queue and steps_done < max_steps:
            sentential, trace = queue.popleft()
            steps_done += 1

            if sentential == word:
                return trace

            # Première variable la plus à gauche
            var_pos = next((i for i, ch in enumerate(sentential) if ch in self.variables), -1)
            if var_pos == -1:
                continue

            # Élagage rapide sur le préfixe terminal déjà fixé
            if not word.startswith(sentential[:var_pos]):
                continue

            var = sentential[var_pos]
            for rhs in sorted(self.productions.get(var, set())):
                nxt = sentential[:var_pos] + rhs + sentential[var_pos + 1 :]
                if len(nxt) <= max_len and nxt not in visited:
                    visited.add(nxt)
                    step = DerivationStep(
                        current=nxt,
                        rule_lhs=var,
                        rule_rhs=rhs,
                        position=var_pos,
                    )
                    queue.append((nxt, [*trace, step]))

        return None

    def accepts(self, word: str) -> bool:
        """Teste si `word` appartient au langage engendré par la grammaire."""
        if self.is_right_linear():
            return self.to_nfa().accepts(word)
        return self.derive(word) is not None