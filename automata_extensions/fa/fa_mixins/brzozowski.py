from __future__ import annotations


class BrzozowskiMixin:
    """Minimisation par l'algorithme de Brzozowski : det(rev(det(rev(A))))."""

    def brzozowski_minimize(self):
        """
        Calcule le DFA minimal complet reconnaissant L(self) par double renversement
        et déterminisation (algorithme de Brzozowski).

        Complexity
        ----------
        O(2^(2^|Q|)) dans le pire cas, très efficace en pratique.
        """
        return self.reverse().to_dfa().reverse().to_dfa().complete()

    def to_dfa_brzozowski(self):
        """Alias de brzozowski_minimize()."""
        return self.brzozowski_minimize()