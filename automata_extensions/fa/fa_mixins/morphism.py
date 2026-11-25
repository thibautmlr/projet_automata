from __future__ import annotations
from typing import Any, Dict, Mapping, Optional, Set


class MorphismMixin:
    """Image directe h(L) et image réciproque h^{-1}(L) par un morphisme de monoïdes."""

    def apply_morphism(self, morphism: Mapping[str, str]):
        """
        Construit un ExtendedNFA reconnaissant l'image directe h(L(self)),
        où h : Sigma* -> Gamma* est défini par `morphism` sur chaque lettre de self.input_symbols.

        Complexity
        ----------
        O(|Q| + |E| * max(|h(a)|))
        """
        from ..nfa import ExtendedNFA

        missing = set(self.input_symbols) - set(morphism.keys())
        if missing:
            raise ValueError(f"Morphism non défini pour les symboles : {missing}.")

        target_alphabet: Set[str] = set()
        for img in morphism.values():
            target_alphabet.update(img)

        states: Set[Any] = set(self.states)
        transitions: Dict[Any, Dict[str, Set[Any]]] = {q: {} for q in states}
        aux_counter = 0

        def add_word_path(src: Any, word: str, dst: Any) -> None:
            nonlocal aux_counter
            if word == "":
                transitions[src].setdefault("", set()).add(dst)
                return
            curr = src
            for ch in word[:-1]:
                mid = ("MORPH", aux_counter)
                while mid in states:
                    aux_counter += 1
                    mid = ("MORPH", aux_counter)
                aux_counter += 1
                states.add(mid)
                transitions[mid] = {}
                transitions[curr].setdefault(ch, set()).add(mid)
                curr = mid
            transitions[curr].setdefault(word[-1], set()).add(dst)

        for u, trans in self.transitions.items():
            for sym, target in trans.items():
                mapped = "" if sym == "" else morphism[sym]
                if isinstance(target, (set, frozenset)):
                    for v in target:
                        add_word_path(u, mapped, v)
                elif target is not None:
                    add_word_path(u, mapped, target)

        return ExtendedNFA(
            states=states,
            input_symbols=target_alphabet,
            transitions=transitions,
            initial_state=self.initial_state,
            final_states=set(self.final_states),
        )

    def inverse_morphism(
        self,
        morphism: Mapping[str, str],
        source_alphabet: Optional[Set[str]] = None,
    ):
        """
        Construit un ExtendedNFA reconnaissant h^{-1}(L(self)) = { w in Gamma* | h(w) in L(self) },
        où `morphism` associe à chaque lettre b de Gamma un mot h(b) sur self.input_symbols.

        Complexity
        ----------
        O(|Q| * |Gamma| * max(|h(b)|))
        """
        from ..nfa import ExtendedNFA

        gamma = set(source_alphabet) if source_alphabet is not None else set(morphism.keys())
        missing = gamma - set(morphism.keys())
        if missing:
            raise ValueError(f"Morphism non défini pour les symboles sources : {missing}.")

        for b in gamma:
            unknown = set(morphism[b]) - set(self.input_symbols)
            if unknown:
                raise ValueError(
                    f"L'image h({b!r})={morphism[b]!r} contient des symboles hors de {self.input_symbols}."
                )

        # Convertit self en vue NFA uniforme pour simuler la lecture de h(b) depuis chaque état
        def step_word(start_state: Any, word: str) -> Set[Any]:
            if hasattr(self, "epsilon_closure"):
                current = set(self.epsilon_closure(start_state))
            else:
                current = {start_state}

            for ch in word:
                nxt: Set[Any] = set()
                for q in current:
                    target = self.transitions.get(q, {}).get(ch)
                    if isinstance(target, (set, frozenset)):
                        for t in target:
                            nxt.update(self.epsilon_closure(t))
                    elif target is not None:
                        nxt.add(target)
                current = nxt
            return current

        transitions: Dict[Any, Dict[str, Set[Any]]] = {q: {} for q in self.states}
        for q in self.states:
            for b in gamma:
                reached = step_word(q, morphism[b])
                if reached:
                    transitions[q][b] = reached

        return ExtendedNFA(
            states=set(self.states),
            input_symbols=gamma,
            transitions=transitions,
            initial_state=self.initial_state,
            final_states=set(self.final_states),
        )