"""Correctifs non intrusifs pour automata-lib 9.2.0."""

from __future__ import annotations

from functools import wraps
from typing import Any

from cached_method import cached_method


def patch_cached_method() -> None:
    """
    Corrige le descripteur ``cached_method`` utilisé par automata-lib 9.2.0.

    Dans le paquet tiers ``cached_method``, ``cached_method.__get__`` renvoie une
    fermeture contenant une référence faible (``weakref.ref``) vers l'instance au lieu
    d'une véritable méthode liée. Lors d'un appel chaîné sur un objet temporaire
    non lié à une variable (ex. ``(d - d).isempty()``), l'instance peut être collectée
    par le ramasse-miettes avant l'exécution effective, levant ``RuntimeError``.

    Ce correctif maintient une référence forte locale sur ``instance`` uniquement
    pendant la durée de l'appel, tout en conservant le cache faible d'origine.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Complexity
    ----------
    O(1)

    References
    ----------
    Documentation automata_extensions, Historique & Section 11.
    """
    orig_get = cached_method.__get__
    if getattr(orig_get, "_is_patched_by_extensions", False):
        return

    def _safe_get(self: Any, instance: Any, owner: Any = None) -> Any:
        bound = orig_get(self, instance, owner)
        if instance is None:
            return bound

        @wraps(bound)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Maintient une référence forte sur l'instance pendant toute la durée de l'appel
            _keep_alive = instance
            return bound(*args, **kwargs)

        return wrapper

    _safe_get._is_patched_by_extensions = True  # type: ignore[attr-defined]
    cached_method.__get__ = _safe_get  # type: ignore[method-assign]