from __future__ import annotations
from typing import Any, Dict, Set


class EliminationMixin:
    """Mixin fournissant l'élimination des transitions epsilon, la normalisation et l'élimination d'états."""

    def remove_epsilon_transitions(self):
        """
        Construit un NFA équivalent sans transitions epsilon.

        Complexity
        ----------
        O(|Q|^2 * |Sigma|)
        """
        if not self.has_epsilon_transitions():
            return self.copy()

        closures = {q: self.epsilon_closure(q) for q in self.states}

        new_transitions: Dict[Any, Dict[str, Set[Any]]] = {q: {} for q in self.states}
        for q in self.states:
            for a in self.input_symbols:
                targets: Set[Any] = set()
                for p in closures[q]:
                    for r in self.transitions.get(p, {}).get(a, set()):
                        targets.update(closures[r])
                if targets:
                    new_transitions[q][a] = targets

        new_finals = {
            q for q in self.states if not closures[q].isdisjoint(self.final_states)
        }

        return type(self)(
            states=set(self.states),
            input_symbols=set(self.input_symbols),
            transitions=new_transitions,
            initial_state=self.initial_state,
            final_states=new_finals,
        )

    def eliminate_lambda(self):
        """Surcharge la méthode d'automata-lib pour déléguer à remove_epsilon_transitions."""
        return self.remove_epsilon_transitions()

    def _fresh_state_name(self, base: str, existing: Set[Any]) -> str:
        candidate = base
        idx = 0
        while candidate in existing:
            idx += 1
            candidate = f"{base}_{idx}"
        return candidate

    def normalize(self):
        """
        Normalise le NFA : ajoute un unique état initial ('q_start') sans transition entrante
        et un unique état final ('q_accept') sans transition sortante reliés par epsilon.

        Complexity
        ----------
        O(|Q| + |E|)
        """
        new_states = set(self.states)
        new_init = self._fresh_state_name("q_start", new_states)
        new_states.add(new_init)
        new_final = self._fresh_state_name("q_accept", new_states)
        new_states.add(new_final)

        new_transitions: Dict[Any, Dict[str, Set[Any]]] = {q: {} for q in new_states}
        for q, trans in self.transitions.items():
            for sym, targets in trans.items():
                if targets:
                    new_transitions[q][sym] = set(targets)

        # Transition epsilon du nouvel initial vers l'ancien initial
        new_transitions[new_init][""] = {self.initial_state}

        # Transitions epsilon des anciens finaux vers le nouvel état final
        for f in self.final_states:
            new_transitions[f].setdefault("", set()).add(new_final)

        return type(self)(
            states=new_states,
            input_symbols=set(self.input_symbols),
            transitions=new_transitions,
            initial_state=new_init,
            final_states={new_final},
        )

    def eliminate_state(self, state: Any):
        """
        Élimine un état intermédiaire en court-circuitant ses transitions entrantes et sortantes.

        Complexity
        ----------
        O(|Q|^2 * |Sigma|^2)
        """
        if state not in self.states:
            raise ValueError(f"L'état {state!r} n'appartient pas à l'automate.")
        if state == self.initial_state or state in self.final_states:
            raise ValueError("Impossible d'éliminer l'état initial ou un état final.")

        remaining_states = set(self.states) - {state}
        new_symbols = set(self.input_symbols)

        incoming = []
        loops = set()
        outgoing = []

        for p, trans in self.transitions.items():
            for sym, targets in trans.items():
                if state in targets:
                    if p == state:
                        loops.add(sym)
                    else:
                        incoming.append((p, sym))

        for sym, targets in self.transitions.get(state, {}).items():
            for r in targets:
                if r != state:
                    outgoing.append((sym, r))

        loop_expr = ""
        non_eps_loops = sorted(s for s in loops if s != "")
        if non_eps_loops:
            joined = "|".join(non_eps_loops)
            loop_expr = f"({joined})*" if len(non_eps_loops) > 1 or len(joined) > 1 else f"{joined}*"

        new_transitions: Dict[Any, Dict[str, Set[Any]]] = {q: {} for q in remaining_states}
        for p in remaining_states:
            for sym, targets in self.transitions.get(p, {}).items():
                kept = set(targets) - {state}
                if kept:
                    new_transitions[p][sym] = kept

        for p, sym_in in incoming:
            for sym_out, r in outgoing:
                label = f"{sym_in}{loop_expr}{sym_out}"
                if label != "":
                    new_symbols.add(label)
                new_transitions[p].setdefault(label, set()).add(r)

        return type(self)(
            states=remaining_states,
            input_symbols=new_symbols,
            transitions=new_transitions,
            initial_state=self.initial_state,
            final_states=set(self.final_states),
        )