"""Classe ``ExtendedGNFA`` étendant ``automata.fa.gnfa.GNFA`` par héritage multiple."""

from __future__ import annotations

from automata.fa.gnfa import GNFA

from automata_extensions.fa.fa import ExtendedFA


class ExtendedGNFA(ExtendedFA, GNFA):
    """Automate fini généralisé étendu (transitions étiquetées par des regex)."""

    pass