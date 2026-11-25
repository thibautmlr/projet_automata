"""Mixin de produit cartésien synchronisé et d'intersection de DFA."""

from __future__ import annotations

from collections import deque
from typing import Any, Callable, Deque, Dict, Set, Tuple

from automata.fa.dfa import DFA


class ProductMixin:
    """
    Fournit le produit cartésien synchronisé de deux DFA et l'intersection.
    """

    def _validate_compatible_dfa(self, other: Any) -> "ProductMixin":
        """
        Vérifie que ``other`` est un DFA partageant exactement le même alphabet.

        Parameters
        ----------
        other : Any
            Second automate à combiner.

        Returns
        -------
        ExtendedDFA
            ``other`` converti en instance d'``ExtendedDFA`` si nécessaire.

        Raises
        ------
        TypeError
            Si ``other`` n'est pas une instance de ``DFA``.
        ValueError
            Si les alphabets ``input_symbols`` diffèrent.
        """
        if not isinstance(other, DFA):
            raise TypeError(f"Un DFA était attendu, reçu : {type(other)!r}")

        self_alphabet = set(self.input_symbols)  # type: ignore[attr-defined]
        other_alphabet = set(other.input_symbols)
        if self_alphabet != other_alphabet:
            raise ValueError(
                f"Alphabets incompatibles : {self_alphabet!r} != {other_alphabet!r}."
            )

        cls = type(self)
        if isinstance(other, cls):
            return other
        return cls(
            states=set(other.states),
            input_symbols=other_alphabet,
            transitions={s: dict(other.transitions.get(s, {})) for s in other.states},
            initial_state=other.initial_state,
            final_states=set(other.final_states),
            allow_partial=True,
        )

    def product(
        self,
        other: DFA,
        is_final: Callable[[Any, Any], bool],
        lazy: bool = True,
    ) -> Any:
        """
        Construit le produit cartésien synchronisé de ``self`` et ``other``.

        Complète les deux automates si nécessaire, puis construit les couples
        d'états ``(q1, q2)`` (paresseusement par BFS depuis ``(q0_1, q0_2)`` si
        ``lazy=True``, ou sur tout ``Q1 × Q2`` si ``lazy=False``).

        Parameters
        ----------
        other : DFA
            Second automate fini déterministe sur le même alphabet.
        is_final : Callable[[Any, Any], bool]
            Prédicat déterminant si un couple ``(q1, q2)`` est un état accepteur.
        lazy : bool, default=True
            Si ``True``, ne construit que les couples accessibles depuis l'état initial.

        Returns
        -------
        ExtendedDFA
            Automate produit résultant.

        Complexity
        ----------
        O(|Q1| · |Q2| · |Σ|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        other_ext = self._validate_compatible_dfa(other)
        dfa1 = self.complete()  # type: ignore[attr-defined]
        dfa2 = other_ext.complete()  # type: ignore[attr-defined]

        alphabet = self._sorted_states(dfa1.input_symbols)  # type: ignore[attr-defined]
        init_pair: Tuple[Any, Any] = (dfa1.initial_state, dfa2.initial_state)

        product_states: Set[Tuple[Any, Any]] = set()
        product_transitions: Dict[Tuple[Any, Any], Dict[Any, Tuple[Any, Any]]] = {}

        if lazy:
            queue: Deque[Tuple[Any, Any]] = deque([init_pair])
            product_states.add(init_pair)
            while queue:
                s1, s2 = queue.popleft()
                row: Dict[Any, Tuple[Any, Any]] = {}
                for symbol in alphabet:
                    nxt = (dfa1.transitions[s1][symbol], dfa2.transitions[s2][symbol])
                    row[symbol] = nxt
                    if nxt not in product_states:
                        product_states.add(nxt)
                        queue.append(nxt)
                product_transitions[(s1, s2)] = row
        else:
            for s1 in dfa1.states:
                for s2 in dfa2.states:
                    pair = (s1, s2)
                    product_states.add(pair)
                    product_transitions[pair] = {
                        symbol: (dfa1.transitions[s1][symbol], dfa2.transitions[s2][symbol])
                        for symbol in alphabet
                    }

        product_finals = {pair for pair in product_states if is_final(pair[0], pair[1])}

        cls = type(self)
        return cls(
            states=product_states,
            input_symbols=set(alphabet),
            transitions=product_transitions,
            initial_state=init_pair,
            final_states=product_finals,
        )

    def intersection(self, other: DFA) -> Any:
        """
        Construit l'automate reconnaissant l'intersection ``L(self) ∩ L(other)``.

        Parameters
        ----------
        other : DFA
            Second automate fini déterministe sur le même alphabet.

        Returns
        -------
        ExtendedDFA
            Automate produit acceptant les mots reconnus simultanément par les deux DFA.

        Complexity
        ----------
        O(|Q1| · |Q2| · |Σ|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        other_ext = self._validate_compatible_dfa(other)
        dfa1 = self.complete()  # type: ignore[attr-defined]
        dfa2 = other_ext.complete()  # type: ignore[attr-defined]
        f1 = set(dfa1.final_states)
        f2 = set(dfa2.final_states)
        return dfa1.product(dfa2, is_final=lambda s1, s2: (s1 in f1) and (s2 in f2))