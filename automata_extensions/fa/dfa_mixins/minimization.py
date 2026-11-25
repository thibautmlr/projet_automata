"""Mixin de minimisation par remplissage de table (Myhill–Nerode) sur DFA."""

from __future__ import annotations

from typing import Any, Dict, FrozenSet, List, Optional, Set


class MinimizationMixin:
    """
    Fournit l'algorithme de remplissage de table (table-filling / Myhill–Nerode),
    l'affichage pédagogique de la table triangulaire des paires distinguables,
    le calcul des classes d'équivalence, ``minimize()`` et ``minify()``.
    """

    def _compute_pair_table_data(
        self,
    ) -> tuple[Any, List[Any], Dict[FrozenSet[Any], Optional[int]]]:
        """
        Exécute l'algorithme itératif de marquage des paires d'états distinguables.

        Complète d'abord le DFA si nécessaire (avec l'état puits ``'⊥'``), puis :
        - Round 0 : marque toute paire ``{p, q}`` telle que ``(p ∈ F) != (q ∈ F)``.
        - Round ``r ≥ 1`` : marque toute paire ``{p, q}`` non encore marquée telle qu'il
          existe ``a ∈ Σ`` avec ``{δ(p, a), δ(q, a)}`` marquée au round ``< r``.

        Returns
        -------
        tuple[ExtendedDFA, List[Any], Dict[FrozenSet[Any], Optional[int]]]
            Triplet ``(dfa_complet, états_ordonnés, table_des_paires)`` où chaque valeur
            de ``table_des_paires`` vaut le numéro du round de distinction (``0, 1, ...``)
            ou ``None`` si les deux états sont équivalents.

        Complexity
        ----------
        O(|Q|² · |Σ|)
        """
        working_dfa = self.complete()  # type: ignore[attr-defined]
        ordered_states: List[Any] = self._sorted_states(working_dfa.states)  # type: ignore[attr-defined]
        alphabet: List[Any] = self._sorted_states(working_dfa.input_symbols)  # type: ignore[attr-defined]
        finals: Set[Any] = set(working_dfa.final_states)
        transitions = working_dfa.transitions

        table: Dict[FrozenSet[Any], Optional[int]] = {}
        n = len(ordered_states)

        # Round 0 : séparation états finaux / non finaux
        for i in range(n):
            for j in range(i + 1, n):
                p, q = ordered_states[i], ordered_states[j]
                pair = frozenset({p, q})
                if (p in finals) != (q in finals):
                    table[pair] = 0
                else:
                    table[pair] = None

        # Rounds 1, 2, ... jusqu'au point fixe
        round_num = 1
        while True:
            newly_marked: List[FrozenSet[Any]] = []
            for pair, mark in table.items():
                if mark is not None:
                    continue
                p, q = tuple(pair)
                for symbol in alphabet:
                    np = transitions[p][symbol]
                    nq = transitions[q][symbol]
                    if np == nq:
                        continue
                    next_pair = frozenset({np, nq})
                    if table.get(next_pair) is not None:
                        newly_marked.append(pair)
                        break

            if not newly_marked:
                break

            for pair in newly_marked:
                table[pair] = round_num
            round_num += 1

        return working_dfa, ordered_states, table

    def pair_table(self) -> Dict[FrozenSet[Any], Optional[int]]:
        """
        Retourne la table complète des paires d'états avec leur round de distinction.

        Parameters
        ----------
        None

        Returns
        -------
        Dict[FrozenSet[Any], Optional[int]]
            Dictionnaire associant chaque paire ``frozenset({p, q})`` au numéro de
            round où elle a été distinguée (``0, 1, 2, ...``) ou ``None`` si les
            états sont équivalents au sens de Myhill–Nerode.

        Complexity
        ----------
        O(|Q|² · |Σ|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        _, _, table = self._compute_pair_table_data()
        return table

    def distinguishable_states(self) -> Set[FrozenSet[Any]]:
        """
        Calcule l'ensemble des paires d'états distinguables ``{p, q}``.

        Parameters
        ----------
        None

        Returns
        -------
        Set[FrozenSet[Any]]
            Ensemble des paires ``frozenset({p, q})`` pour lesquelles il existe un mot
            séparateur ``w`` tel que ``(δ*(p, w) ∈ F) != (δ*(q, w) ∈ F)``.

        Complexity
        ----------
        O(|Q|² · |Σ|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        table = self.pair_table()
        return {pair for pair, round_num in table.items() if round_num is not None}

    def pair_table_str(self, show_round: bool = False) -> str:
        """
        Génère le rendu ASCII triangulaire de la table des paires distinguables.

        Parameters
        ----------
        show_round : bool, default=False
            Si ``True``, affiche le numéro du round de distinction (``0, 1, 2, ...``) ;
            si ``False``, affiche ``'X'`` pour les paires distinguables. Les paires
            équivalentes sont représentées par ``'.'``.

        Returns
        -------
        str
            Représentation textuelle triangulaire de la table.

        Complexity
        ----------
        O(|Q|² · |Σ|)

        References
        ----------
        Documentation automata_extensions, Section 14 ; Cours 06.
        """
        _, ordered_states, table = self._compute_pair_table_data()
        n = len(ordered_states)
        if n <= 1:
            return ""

        labels = [str(s) for s in ordered_states]
        row_width = max(len(lbl) for lbl in labels[1:])
        col_widths = [max(1, len(labels[j])) for j in range(n - 1)]

        lines: List[str] = []
        header_cells = [labels[j].ljust(col_widths[j]) for j in range(n - 1)]
        lines.append(" " * (row_width + 1) + " ".join(header_cells).rstrip())

        for i in range(1, n):
            row_cells: List[str] = []
            for j in range(i):
                pair = frozenset({ordered_states[i], ordered_states[j]})
                mark = table[pair]
                if mark is None:
                    cell = "."
                elif show_round:
                    cell = str(mark)
                else:
                    cell = "X"
                row_cells.append(cell.ljust(col_widths[j]))
            lines.append(f"{labels[i].ljust(row_width)} {' '.join(row_cells).rstrip()}")

        return "\n".join(lines)

    def print_pair_table(self, show_round: bool = False) -> None:
        """
        Affiche sur la sortie standard la table triangulaire des paires distinguables.

        Parameters
        ----------
        show_round : bool, default=False
            Si ``True``, affiche le numéro du round de distinction ; sinon ``'X'``.

        Returns
        -------
        None

        Complexity
        ----------
        O(|Q|² · |Σ|)

        References
        ----------
        Documentation automata_extensions, Section 14 ; Cours 06.
        """
        print(self.pair_table_str(show_round=show_round))

    def equivalence_classes(self) -> List[FrozenSet[Any]]:
        """
        Calcule les classes d'équivalence de Myhill–Nerode sur les états accessibles.

        Deux états accessibles sont dans la même classe d'équivalence s'ils sont
        indistinguables dans la table des paires.

        Parameters
        ----------
        None

        Returns
        -------
        List[FrozenSet[Any]]
            Partition des états accessibles en classes d'équivalence immuables.

        Complexity
        ----------
        O(|Q|² · |Σ|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        working_dfa, _, table = self._compute_pair_table_data()
        accessible: Set[Any] = working_dfa.accessible_states()
        ordered_acc: List[Any] = self._sorted_states(accessible)  # type: ignore[attr-defined]

        visited: Set[Any] = set()
        classes: List[FrozenSet[Any]] = []

        for state in ordered_acc:
            if state in visited:
                continue
            eq_group: Set[Any] = {state}
            for other in ordered_acc:
                if other == state:
                    continue
                pair = frozenset({state, other})
                if table.get(pair) is None:
                    eq_group.add(other)
            visited.update(eq_group)
            classes.append(frozenset(eq_group))

        return classes

    def is_minimal(self) -> bool:
        """
        Teste si l'automate fini déterministe est minimal.

        Un DFA est minimal si tous ses états sont accessibles depuis l'état initial
        et si chaque classe d'équivalence de Myhill–Nerode est réduite à un singleton
        (aucune paire d'états distincts n'est équivalente).

        Parameters
        ----------
        None

        Returns
        -------
        bool
            ``True`` si le DFA est minimal, ``False`` sinon.

        Complexity
        ----------
        O(|Q|² · |Σ|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        states: Set[Any] = set(self.states)  # type: ignore[attr-defined]
        if self.accessible_states() != states:  # type: ignore[attr-defined]
            return False

        classes = self.equivalence_classes()
        return all(len(eq_class) == 1 for eq_class in classes)

    def minimize(self, keep_original_names: bool = False) -> Any:
        """
        Construit l'automate fini déterministe minimal équivalent par quotient
        selon les classes d'équivalence de Myhill–Nerode.

        Les états inaccessibles sont éliminés et chaque classe d'équivalence
        accessible est fusionnée en un unique état.

        Parameters
        ----------
        keep_original_names : bool, default=False
            Si ``False``, chaque état du DFA minimal est le ``frozenset`` de sa
            classe d'équivalence (ex. ``frozenset({'1', '5'})``).
            Si ``True``, chaque classe est nommée par un représentant canonique
            issu de la classe (ex. ``'1'``).

        Returns
        -------
        ExtendedDFA
            Nouvelle instance minimale d'``ExtendedDFA``, sans modifier ``self``.

        Complexity
        ----------
        O(|Q|² · |Σ|)

        References
        ----------
        Hopcroft, Motwani & Ullman, Introduction to Automata Theory, Languages, and Computation.
        """
        working_dfa, _, table = self._compute_pair_table_data()
        accessible: Set[Any] = working_dfa.accessible_states()
        ordered_acc: List[Any] = self._sorted_states(accessible)  # type: ignore[attr-defined]
        alphabet: List[Any] = self._sorted_states(working_dfa.input_symbols)  # type: ignore[attr-defined]
        finals: Set[Any] = set(working_dfa.final_states)

        visited: Set[Any] = set()
        classes: List[FrozenSet[Any]] = []
        state_to_class: Dict[Any, FrozenSet[Any]] = {}

        for state in ordered_acc:
            if state in visited:
                continue
            eq_group: Set[Any] = {state}
            for other in ordered_acc:
                if other != state and table.get(frozenset({state, other})) is None:
                    eq_group.add(other)
            frozen_group = frozenset(eq_group)
            classes.append(frozen_group)
            for member in frozen_group:
                visited.add(member)
                state_to_class[member] = frozen_group

        def _class_name(eq_class: FrozenSet[Any]) -> Any:
            if keep_original_names:
                return self._sorted_states(eq_class)[0]  # type: ignore[attr-defined]
            return eq_class

        new_states: Set[Any] = set()
        new_finals: Set[Any] = set()
        new_transitions: Dict[Any, Dict[Any, Any]] = {}

        for eq_class in classes:
            rep = self._sorted_states(eq_class)[0]  # type: ignore[attr-defined]
            cname = _class_name(eq_class)
            new_states.add(cname)
            if rep in finals:
                new_finals.add(cname)

            row: Dict[Any, Any] = {}
            for symbol in alphabet:
                target_state = working_dfa.transitions[rep][symbol]
                target_class = state_to_class[target_state]
                row[symbol] = _class_name(target_class)
            new_transitions[cname] = row

        init_class = state_to_class[working_dfa.initial_state]
        new_initial = _class_name(init_class)

        cls = type(self)
        return cls(
            states=new_states,
            input_symbols=set(alphabet),
            transitions=new_transitions,
            initial_state=new_initial,
            final_states=new_finals,
        )

    def minify(self, retain_names: bool = False) -> Any:
        """
        Construit l'automate fini déterministe minimal avec renommage canonique
        des états en chaînes entières ``'0'``, ``'1'``, ``'2'``, ...

        Parameters
        ----------
        retain_names : bool, default=False
            Si ``True``, conserve les ensembles d'états fusionnés (``frozenset``)
            comme noms d'états ; si ``False``, renumérote les états ``'0'``, ``'1'``, ...

        Returns
        -------
        ExtendedDFA
            Nouvelle instance minimale d'``ExtendedDFA``.

        Complexity
        ----------
        O(|Q|² · |Σ|)

        References
        ----------
        Cours 06 ; Documentation automata-lib & automata_extensions.
        """
        minimized = self.minimize(keep_original_names=False)
        if retain_names:
            return minimized

        ordered_classes: List[Any] = self._sorted_states(minimized.states)  # type: ignore[attr-defined]
        # Place l'état initial en '0', puis numérote les autres de manière déterministe
        ordered_classes.remove(minimized.initial_state)
        ordered_classes.insert(0, minimized.initial_state)

        rename_map: Dict[Any, str] = {
            old_state: str(idx) for idx, old_state in enumerate(ordered_classes)
        }

        new_states = set(rename_map.values())
        new_initial = rename_map[minimized.initial_state]
        new_finals = {rename_map[s] for s in minimized.final_states}
        new_transitions: Dict[str, Dict[Any, str]] = {
            rename_map[src]: {
                sym: rename_map[dst] for sym, dst in minimized.transitions[src].items()
            }
            for src in ordered_classes
        }

        cls = type(self)
        return cls(
            states=new_states,
            input_symbols=set(minimized.input_symbols),
            transitions=new_transitions,
            initial_state=new_initial,
            final_states=new_finals,
        )