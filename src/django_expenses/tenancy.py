from dataclasses import dataclass

from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.utils.module_loading import import_string

from .settings import EXPENSES


@dataclass(frozen=True)
class ContexteEntreprise:
    source: str
    reference: str
    libelle: str = ""

    @property
    def est_valide(self):
        return bool(self.source and self.reference)

    def as_kwargs(self):
        return {
            "entreprise_source": self.source,
            "entreprise_reference": self.reference,
            "entreprise_libelle": self.libelle,
        }


def _normaliser_contexte(value):
    if value is None:
        return None
    if isinstance(value, ContexteEntreprise):
        return value if value.est_valide else None
    if isinstance(value, dict):
        contexte = ContexteEntreprise(
            source=str(value.get("source") or value.get("entreprise_source") or ""),
            reference=str(value.get("reference") or value.get("entreprise_reference") or ""),
            libelle=str(value.get("libelle") or value.get("entreprise_libelle") or ""),
        )
        return contexte if contexte.est_valide else None

    contexte = ContexteEntreprise(
        source=str(
            getattr(value, "source", "")
            or getattr(value, "entreprise_source", "")
        ),
        reference=str(
            getattr(value, "reference", "")
            or getattr(value, "entreprise_reference", "")
        ),
        libelle=str(
            getattr(value, "libelle", "")
            or getattr(value, "entreprise_libelle", "")
        ),
    )
    return contexte if contexte.est_valide else None


def resoudre_entreprise(request=None, required=None):
    if not EXPENSES["ENABLE_MULTI_ENTREPRISE"]:
        return None

    resolver = EXPENSES.get("ENTREPRISE_RESOLVER")
    contexte = None
    if resolver:
        callable_resolver = import_string(resolver) if isinstance(resolver, str) else resolver
        contexte = _normaliser_contexte(callable_resolver(request))
    elif request is not None:
        contexte = _normaliser_contexte(getattr(request, "entreprise", None))
        if contexte is None:
            contexte = _normaliser_contexte({
                "entreprise_source": getattr(request, "entreprise_source", ""),
                "entreprise_reference": getattr(request, "entreprise_reference", ""),
                "entreprise_libelle": getattr(request, "entreprise_libelle", ""),
            })

    if required is None:
        required = True

    if contexte is None and required:
        raise PermissionDenied(
            "Contexte entreprise obligatoire. Configurez ENTREPRISE_RESOLVER "
            "ou injectez request.entreprise depuis un middleware/auth fiable."
        )
    return contexte


def filtrer_par_entreprise(
    queryset,
    contexte,
    *,
    prefix="",
    include_global=False,
):
    if contexte is None:
        return queryset

    source = f"{prefix}entreprise_source"
    reference = f"{prefix}entreprise_reference"
    tenant_q = Q(**{source: contexte.source, reference: contexte.reference})
    if include_global:
        return queryset.filter(
            tenant_q | Q(**{source: "", reference: ""})
        )
    return queryset.filter(tenant_q)


def appartient_a_entreprise(obj, contexte, *, allow_global=False):
    if obj is None or contexte is None:
        return True

    source = getattr(obj, "entreprise_source", "")
    reference = getattr(obj, "entreprise_reference", "")
    if allow_global and not source and not reference:
        return True
    return source == contexte.source and reference == contexte.reference


def verifier_appartenance(obj, contexte, *, allow_global=False, label="Objet"):
    if not appartient_a_entreprise(obj, contexte, allow_global=allow_global):
        raise PermissionDenied(
            f"{label} n'appartient pas à l'entreprise active."
        )
