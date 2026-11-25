"""Extension pédagogique de la bibliothèque automata-lib 9.2.0."""

from automata_extensions.utils.patches import patch_cached_method

# Applique automatiquement le correctif de cache dès l'import du paquet
patch_cached_method()

from automata_extensions.fa import (  # noqa: E402
    ExtendedDFA,
    ExtendedFA,
    ExtendedGNFA,
    ExtendedNFA,
)

__all__ = [
    "ExtendedFA",
    "ExtendedDFA",
    "ExtendedNFA",
    "ExtendedGNFA",
    "patch_cached_method",
]