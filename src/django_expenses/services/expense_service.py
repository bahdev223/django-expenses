from datetime import date
from decimal import Decimal
from pathlib import Path

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from ..constants import ExpenseStatus
from ..exceptions import WorkflowError
from ..hooks import HookRegistry
from ..models import (
    Expense,
    ExpenseAttachment,
    ExpenseApproval,
    ExpensePayment,
    ExpenseComment,
    EvenementDepense,
)
from ..permissions import CHANGE_EXPENSE, DELETE_EXPENSE
from ..settings import EXPENSES
from ..tenancy import ContexteEntreprise, appartient_a_entreprise
from ..signals import (
    expense_created,
    expense_updated,
    expense_submitted,
    expense_approved,
    expense_rejected,
    expense_payment_recorded,
    expense_paid,
    expense_cancelled,
    expense_deleted,
)
from ..workflows import ExpenseWorkflow


class ExpenseService:
    """Unified service layer for expense lifecycle management."""

    @staticmethod
    def _journaliser(expense, action, user=None, donnees=None):
        EvenementDepense.objects.create(
            entreprise_source=expense.entreprise_source,
            entreprise_reference=expense.entreprise_reference,
            entreprise_libelle=expense.entreprise_libelle,
            depense=expense,
            reference_depense=expense.reference_number,
            action=action,
            acteur=user,
            donnees=donnees or {},
        )

    @staticmethod
    def _validate_core(data, instance=None):
        amount = data.get("amount", getattr(instance, "amount", None))
        tax_amount = data.get("tax_amount", getattr(instance, "tax_amount", Decimal("0")))
        if amount is None or Decimal(str(amount)) <= 0:
            raise ValidationError({"amount": "Le montant doit être supérieur à zéro."})
        if tax_amount is not None and Decimal(str(tax_amount)) < 0:
            raise ValidationError({"tax_amount": "Le montant de taxe ne peut pas être négatif."})
        projet_source = data.get("projet_source", getattr(instance, "projet_source", ""))
        projet_reference = data.get("projet_reference", getattr(instance, "projet_reference", ""))
        if bool(projet_source) != bool(projet_reference):
            raise ValidationError({
                "projet_reference": (
                    "projet_source et projet_reference doivent être renseignés ensemble."
                )
            })

        entreprise_source = data.get(
            "entreprise_source", getattr(instance, "entreprise_source", "")
        )
        entreprise_reference = data.get(
            "entreprise_reference", getattr(instance, "entreprise_reference", "")
        )
        if bool(entreprise_source) != bool(entreprise_reference):
            raise ValidationError({
                "entreprise_reference": (
                    "entreprise_source et entreprise_reference doivent être renseignés ensemble."
                )
            })
        if EXPENSES["ENABLE_MULTI_ENTREPRISE"] and not (
            entreprise_source and entreprise_reference
        ):
            raise ValidationError("Une entreprise est obligatoire en mode multi-entreprise.")

        contexte = (
            ContexteEntreprise(entreprise_source, entreprise_reference)
            if entreprise_source and entreprise_reference else None
        )
        category = data.get("category", getattr(instance, "category", None))
        if category is not None and contexte is not None:
            allow_global = EXPENSES["ALLOW_GLOBAL_CATEGORIES"]
            if not appartient_a_entreprise(category, contexte, allow_global=allow_global):
                raise ValidationError({"category": "La catégorie appartient à une autre entreprise."})
        cost_center = data.get("cost_center", getattr(instance, "cost_center", None))
        if cost_center is not None and contexte is not None:
            if not appartient_a_entreprise(cost_center, contexte):
                raise ValidationError({
                    "cost_center": "Le centre de coût appartient à une autre entreprise."
                })

    @staticmethod
    def _validate_submission(expense):
        category = expense.category
        if category.requires_vendor and not expense.vendor.strip():
            raise ValidationError({"vendor": "Un fournisseur/tiers est obligatoire pour cette catégorie."})
        if category.requires_receipt and not expense.attachments.exists():
            raise ValidationError("Un justificatif est obligatoire pour cette catégorie avant soumission.")

    @staticmethod
    @transaction.atomic
    def create(data, user=None):
        ExpenseService._validate_core(data)
        hooks = HookRegistry.get_hooks()
        payload = dict(data)
        if not payload.get("currency"):
            payload["currency"] = EXPENSES["CURRENCY"]
        for hook in hooks:
            payload = hook.before_create(payload, user) or payload
        expense = Expense.objects.create(**payload)
        expense_created.send(sender=Expense, expense=expense, user=user)
        ExpenseService._journaliser(expense, "creation", user)
        for hook in hooks:
            hook.after_create(expense, user)
        return expense

    @staticmethod
    @transaction.atomic
    def update(expense, data, user=None):
        _assert_has_perm(user, CHANGE_EXPENSE)
        expense = Expense.objects.select_for_update().get(pk=expense.pk)
        _assert_editable(expense)
        ExpenseService._validate_core(data, instance=expense)
        for key, value in data.items():
            if key in {"user", "status", "reference_number", "approved_by"}:
                continue
            setattr(expense, key, value)
        expense.full_clean(exclude=["reference_number"])
        expense.save()
        expense_updated.send(sender=Expense, expense=expense, user=user)
        ExpenseService._journaliser(expense, "modification", user)
        return expense

    @staticmethod
    @transaction.atomic
    def submit(expense, user=None):
        _assert_has_perm(user, CHANGE_EXPENSE)
        expense = Expense.objects.select_for_update().get(pk=expense.pk)
        _assert_editable(expense)
        ExpenseService._validate_submission(expense)
        ExpenseWorkflow.assert_allowed(expense.status, ExpenseStatus.SUBMITTED)
        previous = expense.status
        expense.status = ExpenseStatus.SUBMITTED
        expense.date_submitted = timezone.now()
        expense.save(update_fields=["status", "date_submitted", "updated_at"])
        expense_submitted.send(sender=Expense, expense=expense, user=user)
        ExpenseService._journaliser(expense, "soumission", user)
        for hook in HookRegistry.get_hooks():
            hook.after_transition(expense, previous, user)
        return expense

    @staticmethod
    @transaction.atomic
    def request_approval(expense, user=None):
        _assert_has_perm(user, CHANGE_EXPENSE)
        expense = Expense.objects.select_for_update().get(pk=expense.pk)
        requires_approval = EXPENSES["REQUIRE_APPROVAL"] and expense.category.requires_approval
        if not requires_approval:
            from .budget_service import BudgetService

            BudgetService.verifier_depense(expense)
            ExpenseWorkflow.assert_allowed(expense.status, ExpenseStatus.APPROVED)
            previous = expense.status
            expense.status = ExpenseStatus.APPROVED
            expense.date_approved = timezone.now()
            expense.save(update_fields=["status", "date_approved", "updated_at"])
            expense_approved.send(sender=Expense, expense=expense, user=user)
            ExpenseService._journaliser(expense, "approbation_automatique", user)
            for hook in HookRegistry.get_hooks():
                hook.after_transition(expense, previous, user)
            return expense

        ExpenseWorkflow.assert_allowed(expense.status, ExpenseStatus.PENDING_APPROVAL)
        previous = expense.status
        expense.status = ExpenseStatus.PENDING_APPROVAL
        expense.save(update_fields=["status", "updated_at"])
        ExpenseService._journaliser(expense, "demande_approbation", user)
        for hook in HookRegistry.get_hooks():
            hook.after_transition(expense, previous, user)
        return expense

    @staticmethod
    @transaction.atomic
    def approve(expense, user=None, comment=""):
        _assert_has_perm(user, "django_expenses.approve_expense")
        expense = Expense.objects.select_for_update().get(pk=expense.pk)
        hooks = HookRegistry.get_hooks()
        ExpenseWorkflow.assert_allowed(expense.status, ExpenseStatus.APPROVED)
        from .budget_service import BudgetService

        BudgetService.verifier_depense(expense)
        previous = expense.status
        for hook in hooks:
            hook.before_transition(expense, ExpenseStatus.APPROVED, user)
        expense.status = ExpenseStatus.APPROVED
        expense.approved_by = user
        expense.date_approved = timezone.now()
        expense.save(update_fields=["status", "approved_by", "date_approved", "updated_at"])
        ExpenseApproval.objects.create(
            expense=expense,
            approved_by=user,
            decision=ExpenseApproval.Decision.APPROVED,
            comment=comment,
        )
        expense_approved.send(sender=Expense, expense=expense, user=user)
        ExpenseService._journaliser(expense, "approbation", user, {"commentaire": comment})
        for hook in hooks:
            hook.after_transition(expense, previous, user)
        return expense

    @staticmethod
    @transaction.atomic
    def reject(expense, user=None, reason=""):
        _assert_has_perm(user, "django_expenses.approve_expense")
        expense = Expense.objects.select_for_update().get(pk=expense.pk)
        ExpenseWorkflow.assert_allowed(expense.status, ExpenseStatus.REJECTED)
        expense.status = ExpenseStatus.REJECTED
        expense.rejection_reason = reason
        expense.save(update_fields=["status", "rejection_reason", "updated_at"])
        ExpenseApproval.objects.create(
            expense=expense,
            approved_by=user,
            decision=ExpenseApproval.Decision.REJECTED,
            comment=reason,
        )
        expense_rejected.send(sender=Expense, expense=expense, user=user)
        ExpenseService._journaliser(expense, "rejet", user, {"motif": reason})
        return expense

    @staticmethod
    @transaction.atomic
    def pay(expense, user=None, payment_data=None):
        _assert_has_perm(user, "django_expenses.pay_expense")
        expense = Expense.objects.select_for_update().get(pk=expense.pk)
        if expense.status not in {ExpenseStatus.APPROVED, ExpenseStatus.PARTIALLY_PAID}:
            raise WorkflowError(f"Cannot record a payment from status '{expense.status}'.")

        payload = dict(payment_data or {})
        hooks = HookRegistry.get_hooks()
        for hook in hooks:
            payload = hook.before_pay(expense, payload, user) or payload

        cle_idempotence = payload.get("cle_idempotence")
        if cle_idempotence:
            existing = ExpensePayment.objects.filter(cle_idempotence=cle_idempotence).first()
            if existing:
                if existing.expense_id != expense.pk:
                    raise ValidationError("Cette clé d'idempotence est déjà utilisée pour une autre dépense.")
                return expense

        remaining = expense.remaining_amount
        raw_amount = payload.get("amount_paid")
        amount = remaining if raw_amount in (None, "") else Decimal(str(raw_amount))
        if amount <= 0:
            raise ValidationError({"amount_paid": "Le montant payé doit être supérieur à zéro."})
        if amount > remaining:
            raise ValidationError(
                {"amount_paid": f"Surpaiement interdit. Reste à payer : {remaining}."}
            )
        if amount < remaining and not EXPENSES["ALLOW_PARTIAL_PAYMENTS"]:
            raise ValidationError("Les paiements partiels sont désactivés.")
        compte_reference = payload.get("compte_reference", "")
        if EXPENSES["REQUIRE_ACCOUNT_REFERENCE"] and not compte_reference:
            raise ValidationError({"compte_reference": "Une référence de compte de trésorerie est obligatoire."})

        new_remaining = remaining - amount
        target_status = ExpenseStatus.PAID if new_remaining == 0 else ExpenseStatus.PARTIALLY_PAID
        ExpenseWorkflow.assert_allowed(expense.status, target_status)

        payment_method = payload.get("payment_method", expense.payment_method or "")
        payment = ExpensePayment.objects.create(
            expense=expense,
            amount_paid=amount,
            payment_date=payload.get("payment_date", date.today()),
            payment_method=payment_method,
            reference=payload.get("reference", ""),
            paid_by=user,
            notes=payload.get("notes", ""),
            compte_reference=compte_reference,
            cle_idempotence=cle_idempotence or None,
        )

        expense.status = target_status
        expense.payment_method = payment_method
        fields = ["status", "payment_method", "updated_at"]
        if target_status == ExpenseStatus.PAID:
            expense.date_paid = timezone.now()
            fields.append("date_paid")
        expense.save(update_fields=fields)

        expense_payment_recorded.send(
            sender=ExpensePayment,
            expense=expense,
            payment=payment,
            user=user,
        )
        ExpenseService._journaliser(
            expense,
            "paiement",
            user,
            {"montant": str(amount), "reste": str(new_remaining), "paiement_id": payment.pk},
        )
        if target_status == ExpenseStatus.PAID:
            expense_paid.send(sender=Expense, expense=expense, user=user)
        for hook in hooks:
            hook.after_pay(expense, payment, user)
        return expense

    @staticmethod
    @transaction.atomic
    def cancel(expense, user=None):
        _assert_has_perm(user, CHANGE_EXPENSE)
        expense = Expense.objects.select_for_update().get(pk=expense.pk)
        ExpenseWorkflow.assert_allowed(expense.status, ExpenseStatus.CANCELLED)
        expense.status = ExpenseStatus.CANCELLED
        expense.save(update_fields=["status", "updated_at"])
        expense_cancelled.send(sender=Expense, expense=expense, user=user)
        ExpenseService._journaliser(expense, "annulation", user)
        return expense

    @staticmethod
    @transaction.atomic
    def archive(expense, user=None):
        _assert_has_perm(user, CHANGE_EXPENSE)
        expense = Expense.objects.select_for_update().get(pk=expense.pk)
        ExpenseWorkflow.assert_allowed(expense.status, ExpenseStatus.ARCHIVED)
        expense.status = ExpenseStatus.ARCHIVED
        expense.save(update_fields=["status", "updated_at"])
        ExpenseService._journaliser(expense, "archivage", user)
        return expense

    @staticmethod
    @transaction.atomic
    def delete(expense, user=None):
        _assert_has_perm(user, DELETE_EXPENSE)
        expense = Expense.objects.select_for_update().get(pk=expense.pk)
        if expense.status != ExpenseStatus.DRAFT:
            raise WorkflowError("Seule une dépense brouillon peut être supprimée logiquement.")
        expense.status = ExpenseStatus.CANCELLED
        expense.supprime_le = timezone.now()
        expense.supprime_par = user
        expense.save(update_fields=["status", "supprime_le", "supprime_par", "updated_at"])
        ExpenseService._journaliser(expense, "suppression_logique", user)
        expense_deleted.send(sender=Expense, reference_number=expense.reference_number, user=user)

    @staticmethod
    def add_attachment(expense, file, filename=None, user=None):
        _assert_has_perm(user, CHANGE_EXPENSE)
        if expense.attachments.count() >= EXPENSES["MAX_ATTACHMENTS"]:
            raise ValidationError("Nombre maximum de justificatifs atteint.")
        name = filename or getattr(file, "name", "justificatif")
        extension = Path(name).suffix.lower().lstrip(".")
        allowed = {str(ext).lower().lstrip(".") for ext in EXPENSES["ALLOWED_ATTACHMENT_TYPES"]}
        if extension and extension not in allowed:
            raise ValidationError(f"Type de fichier non autorisé : .{extension}")
        piece = ExpenseAttachment.objects.create(expense=expense, file=file, filename=name)
        ExpenseService._journaliser(
            expense, "ajout_justificatif", user, {"piece_id": piece.pk, "nom": name}
        )
        return piece

    @staticmethod
    def add_comment(expense, text, user=None):
        _assert_has_perm(user, CHANGE_EXPENSE)
        if not EXPENSES["ENABLE_COMMENTS"]:
            raise ValidationError("Les commentaires sont désactivés.")
        commentaire = ExpenseComment.objects.create(expense=expense, user=user, comment=text)
        ExpenseService._journaliser(
            expense, "ajout_commentaire", user, {"commentaire_id": commentaire.pk}
        )
        return commentaire


def _assert_editable(expense):
    if not expense.is_editable:
        raise WorkflowError(
            f"Expense is in status '{expense.get_status_display()}' and cannot be edited."
        )


def _assert_has_perm(user, perm):
    if user is None or not user.has_perm(perm):
        raise PermissionDenied(f"Missing permission: {perm}")


class ServiceDepense:
    """Façade française stable pour les nouveaux projets SahelTech."""

    creer = staticmethod(ExpenseService.create)
    modifier = staticmethod(ExpenseService.update)
    soumettre = staticmethod(ExpenseService.submit)
    demander_approbation = staticmethod(ExpenseService.request_approval)
    approuver = staticmethod(ExpenseService.approve)
    rejeter = staticmethod(ExpenseService.reject)
    payer = staticmethod(ExpenseService.pay)
    annuler = staticmethod(ExpenseService.cancel)
    archiver = staticmethod(ExpenseService.archive)
    supprimer = staticmethod(ExpenseService.delete)
    ajouter_justificatif = staticmethod(ExpenseService.add_attachment)
    ajouter_commentaire = staticmethod(ExpenseService.add_comment)
