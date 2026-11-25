"""Mixin de test de complétude et de complétion d'un automate fini déterministe."""

from __future__ import annotations

from typing import Any, Dict, Set


class CompletenessMixin:
    """
    Fournit les algorithmes de vérification de complétude et d'ajout d'état puits
    sur un ``ExtendedDFA``.
    """

    def is_complete(self) -> bool:
        """
        Teste si la fonction de transition du DFA est totale (automate complet).

        Un DFA est complet si pour tout état ``q ∈ Q`` et tout symbole ``a ∈ Σ``,
        la transition ``δ(q, a)`` est définie.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            ``True`` si le DFA est complet, ``False`` sinon.

        Complexity
        ----------
        O(|Q| · |Σ|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        alphabet = self.input_symbols  # type: ignore[attr-defined]
        transitions = self.transitions  # type: ignore[attr-defined]
        for state in self.states:  # type: ignore[attr-defined]
            state_transitions = transitions.get(state, {})
            for symbol in alphabet:
                if symbol not in state_transitions or state_transitions[symbol] is None:
                    return False
        return True

    def complete(self, sink_state: Any = "⊥") -> Any:
        """
        Construit un nouvel ``ExtendedDFA`` complet équivalent.

        Si l'automate est déjà complet, retourne une copie indépendante reconstruite
        directement sans ajouter d'état puits inutile. Sinon, ajoute un état puits
        (nommé ``sink_state``, par défaut ``'⊥'``) bouclant sur lui-même pour tout
        symbole et redirige toutes les transitions manquantes vers cet état puits.

        Parameters
        ----------
        sink_state : Any, default="⊥"
            Nom de l'état puits ajouté si l'automate est incomplet. Si ce nom
            existe déjà dans ``self.states``, un suffixe numérique est ajouté.

        Returns
        -------
        ExtendedDFA
            Nouvelle instance complète d'``ExtendedDFA``, sans modifier ``self``.

        Complexity
        ----------
        O(|Q| · |Σ|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        states: Set[Any] = set(self.states)  # type: ignore[attr-defined]
        alphabet: Set[Any] = set(self.input_symbols)  # type: ignore[attr-defined]
        orig_transitions = self.transitions  # type: ignore[attr-defined]
        cls = type(self)

        if self.is_complete():
            return cls(
                states=states,
                input_symbols=alphabet,
                transitions={s: dict(orig_transitions[s]) for s in states},
                initial_state=self.initial_state,  # type: ignore[attr-defined]
                final_states=set(self.final_states),  # type: ignore[attr-defined]
            )

        actual_sink = sink_state
        if actual_sink in states:
            counter = 1
            while f"{sink_state}_{counter}" in states:
                counter += 1
            actual_sink = f"{sink_state}_{counter}"

        new_states = states | {actual_sink}
        new_transitions: Dict[Any, Dict[Any, Any]] = {}

        for state in states:
            row: Dict[Any, Any] = {}
            orig_row = orig_transitions.get(state, {})
            for symbol in alphabet:
                target = orig_row.get(symbol)
                row[symbol] = actual_sink if target is None else target
            new_transitions[state] = row

        new_transitions[actual_sink] = {symbol: actual_sink for symbol in alphabet}

        return cls(
            states=new_states,
            input_symbols=alphabet,
            transitions=new_transitions,
            initial_state=self.initial_state,  # type: ignore[attr-defined]
            final_states=set(self.final_states),  # type: ignore[attr-defined]
        )