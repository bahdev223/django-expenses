from django.contrib import admin
from django.utils.html import format_html

from .settings import EXPENSES
from .tenancy import filtrer_par_entreprise, resoudre_entreprise

from .models import (
    Expense,
    ExpenseCategory,
    CostCenter,
    ExpenseAttachment,
    ExpenseApproval,
    ExpensePayment,
    ExpenseComment,
    BudgetDepense,
    AvanceDepense,
    JustificationAvance,
    EvenementDepense,
)
from .services import ExpenseService, ReportService


class EntrepriseAdminMixin:
    entreprise_prefix = ""
    include_global_entreprise = False

    def _contexte_entreprise(self, request):
        if not EXPENSES["ENABLE_MULTI_ENTREPRISE"]:
            return None
        if (
            request.user.is_superuser
            and EXPENSES["MULTI_ENTREPRISE_SUPERUSER_GLOBAL"]
        ):
            return None
        return resoudre_entreprise(request, required=True)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        contexte = self._contexte_entreprise(request)
        if contexte is None:
            return qs
        return filtrer_par_entreprise(
            qs,
            contexte,
            prefix=self.entreprise_prefix,
            include_global=self.include_global_entreprise,
        )

    def _injecter_entreprise(self, obj, request):
        contexte = self._contexte_entreprise(request)
        if contexte is None or self.entreprise_prefix:
            return
        obj.entreprise_source = contexte.source
        obj.entreprise_reference = contexte.reference
        obj.entreprise_libelle = contexte.libelle

    def save_model(self, request, obj, form, change):
        self._injecter_entreprise(obj, request)
        obj.full_clean()
        super().save_model(request, obj, form, change)


class ApprovalInline(admin.TabularInline):
    model = ExpenseApproval
    extra = 0
    def has_add_permission(self, request, obj=None): return False
    readonly_fields = ["approved_by", "decision", "comment", "created_at"]
    can_delete = False


class PaymentInline(admin.TabularInline):
    model = ExpensePayment
    extra = 0
    def has_add_permission(self, request, obj=None): return False
    readonly_fields = [
        "amount_paid", "payment_date", "payment_method", "reference", "paid_by",
        "compte_reference", "cle_idempotence", "created_at",
    ]
    can_delete = False


class AttachmentInline(admin.TabularInline):
    model = ExpenseAttachment
    extra = 0
    def has_add_permission(self, request, obj=None): return False
    readonly_fields = ["filename", "uploaded_at"]


class CommentInline(admin.TabularInline):
    model = ExpenseComment
    extra = 0
    def has_add_permission(self, request, obj=None): return False
    readonly_fields = ["user", "comment", "created_at"]


class EventInline(admin.TabularInline):
    model = EvenementDepense
    extra = 0
    def has_add_permission(self, request, obj=None): return False
    readonly_fields = ["action", "acteur", "donnees", "cree_le"]
    can_delete = False


@admin.register(Expense)
class ExpenseAdmin(EntrepriseAdminMixin, admin.ModelAdmin):
    list_display = [
        "reference_number", "colored_status", "user", "category_path", "expense_nature",
        "cost_center", "projet_reference", "amount_display", "paid_display", "remaining_display", "date_incurred",
    ]
    list_filter = [
        "status", "expense_nature", "category", "cost_center", "currency",
        "projet_source", "date_incurred",
    ]
    search_fields = [
        "reference_number", "description", "vendor", "user__username",
        "projet_reference", "projet_libelle",
    ]
    list_select_related = ["user", "category", "cost_center"]
    date_hierarchy = "date_incurred"
    readonly_fields = [
        "reference_number", "status", "date_submitted", "date_approved", "date_paid",
        "approved_by", "created_at", "updated_at", "suggested_account_code",
        "paid_amount", "remaining_amount", "supprime_le", "supprime_par",
    ]
    fieldsets = [
        ("Identification", {"fields": ["reference_number", "status", "user", "category", "expense_nature", "cost_center"]}),
        ("Projet", {"fields": ["projet_source", "projet_reference", "projet_libelle"]}),
        ("Montants", {"fields": ["amount", "tax_amount", "currency", "paid_amount", "remaining_amount"]}),
        ("Détails", {"fields": ["description", "vendor", "date_incurred"]}),
        ("Comptabilité", {"fields": ["suggested_account_code"]}),
        ("Paiement", {"fields": ["payment_method", "approved_by", "rejection_reason"]}),
        ("Audit", {"fields": ["supprime_le", "supprime_par", "date_submitted", "date_approved", "date_paid", "created_at", "updated_at"]}),
    ]
    inlines = [ApprovalInline, PaymentInline, AttachmentInline, CommentInline, EventInline]
    actions = ["export_csv", "mark_paid", "mark_archived"]

    def save_model(self, request, obj, form, change):
        self._injecter_entreprise(obj, request)
        data = {
            "entreprise_source": obj.entreprise_source,
            "entreprise_reference": obj.entreprise_reference,
            "entreprise_libelle": obj.entreprise_libelle,
            "category": obj.category,
            "expense_nature": obj.expense_nature,
            "cost_center": obj.cost_center,
            "projet_source": obj.projet_source,
            "projet_reference": obj.projet_reference,
            "projet_libelle": obj.projet_libelle,
            "amount": obj.amount,
            "tax_amount": obj.tax_amount,
            "currency": obj.currency,
            "description": obj.description,
            "vendor": obj.vendor,
            "date_incurred": obj.date_incurred,
            "payment_method": obj.payment_method,
        }
        if change:
            updated = ExpenseService.update(Expense.objects.get(pk=obj.pk), data, user=request.user)
            for field in Expense._meta.concrete_fields:
                setattr(obj, field.attname, getattr(updated, field.attname))
        else:
            created = ExpenseService.create({**data, "user": obj.user if obj.user_id else request.user}, user=request.user)
            for field in Expense._meta.concrete_fields:
                setattr(obj, field.attname, getattr(created, field.attname))
            obj._state.adding = False
            obj._state.db = created._state.db

    def get_readonly_fields(self, request, obj=None):
        base = list(super().get_readonly_fields(request, obj))
        if obj and not obj.is_editable:
            base.extend([
                "user", "category", "expense_nature", "cost_center",
                "projet_source", "projet_reference", "projet_libelle",
                "amount", "tax_amount", "currency", "description", "vendor",
                "date_incurred", "payment_method",
            ])
        return list(dict.fromkeys(base))

    def has_delete_permission(self, request, obj=None):
        allowed = super().has_delete_permission(request, obj)
        return allowed and (obj is None or obj.status == "draft")

    def delete_model(self, request, obj):
        ExpenseService.delete(obj, user=request.user)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            ExpenseService.delete(obj, user=request.user)

    def category_path(self, obj):
        return obj.category.get_full_path() if obj.category else "-"
    category_path.short_description = "Catégorie"

    def colored_status(self, obj):
        colors = {
            "draft": "gray", "submitted": "blue", "pending_approval": "orange",
            "approved": "green", "rejected": "red", "partiellement_payee": "darkorange",
            "paid": "teal", "archived": "gray", "cancelled": "darkgray",
        }
        return format_html(
            '<span style="color:{};font-weight:bold;">{}</span>',
            colors.get(obj.status, "gray"), obj.get_status_display(),
        )
    colored_status.short_description = "Statut"

    def amount_display(self, obj):
        return f"{obj.total_amount:,.2f}"
    amount_display.short_description = "Total"

    def paid_display(self, obj):
        return f"{obj.paid_amount:,.2f}"
    paid_display.short_description = "Payé"

    def remaining_display(self, obj):
        return f"{obj.remaining_amount:,.2f}"
    remaining_display.short_description = "Reste"

    def export_csv(self, request, queryset):
        return ReportService.export_csv(queryset)
    export_csv.short_description = "Exporter CSV"

    def mark_paid(self, request, queryset):
        count = 0
        for expense in queryset.filter(status__in=["approved", "partiellement_payee"]):
            ExpenseService.pay(expense, user=request.user)
            count += 1
        self.message_user(request, f"{count} dépense(s) soldée(s).")
    mark_paid.short_description = "Solder la sélection"

    def mark_archived(self, request, queryset):
        count = 0
        for expense in queryset.filter(status="paid"):
            ExpenseService.archive(expense, user=request.user)
            count += 1
        self.message_user(request, f"{count} dépense(s) archivée(s).")
    mark_archived.short_description = "Archiver la sélection"


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(EntrepriseAdminMixin, admin.ModelAdmin):
    include_global_entreprise = True
    list_display = [
        "code", "name", "entreprise_reference", "parent", "expense_nature",
        "default_account_code", "is_active", "sort_order",
    ]
    list_filter = ["expense_nature", "is_active", "requires_approval", "requires_receipt", "requires_vendor"]
    search_fields = ["code", "name", "default_account_code"]
    list_editable = ["sort_order", "is_active"]


@admin.register(CostCenter)
class CostCenterAdmin(EntrepriseAdminMixin, admin.ModelAdmin):
    list_display = ["code", "name", "entreprise_reference", "manager", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["code", "name", "description"]


@admin.register(ExpenseApproval)
class ExpenseApprovalAdmin(EntrepriseAdminMixin, admin.ModelAdmin):
    entreprise_prefix = "expense__"
    list_display = ["expense", "approved_by", "decision", "created_at"]
    readonly_fields = ["expense", "approved_by", "decision", "comment", "created_at"]
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False


@admin.register(ExpensePayment)
class ExpensePaymentAdmin(EntrepriseAdminMixin, admin.ModelAdmin):
    entreprise_prefix = "expense__"
    list_display = ["expense", "amount_paid", "payment_date", "payment_method", "compte_reference", "paid_by"]
    list_filter = ["payment_method", "payment_date"]
    search_fields = ["reference", "expense__reference_number", "compte_reference", "cle_idempotence"]
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False


@admin.register(ExpenseAttachment)
class ExpenseAttachmentAdmin(EntrepriseAdminMixin, admin.ModelAdmin):
    entreprise_prefix = "expense__"
    list_display = ["filename", "expense", "uploaded_at"]
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False


@admin.register(ExpenseComment)
class ExpenseCommentAdmin(EntrepriseAdminMixin, admin.ModelAdmin):
    entreprise_prefix = "expense__"
    list_display = ["expense", "user", "created_at"]
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False


@admin.register(BudgetDepense)
class BudgetDepenseAdmin(EntrepriseAdminMixin, admin.ModelAdmin):
    list_display = [
        "nom", "entreprise_reference", "projet_reference", "date_debut", "date_fin", "montant_alloue",
        "montant_consomme", "montant_disponible", "bloquant", "actif",
    ]
    list_filter = ["actif", "bloquant", "categorie", "centre_cout", "projet_source"]
    search_fields = ["nom", "projet_reference", "projet_libelle"]


class JustificationInline(admin.TabularInline):
    model = JustificationAvance
    extra = 0
    readonly_fields = ["montant", "date_depense", "description", "depense", "piece", "cree_le"]


@admin.register(AvanceDepense)
class AvanceDepenseAdmin(EntrepriseAdminMixin, admin.ModelAdmin):
    list_display = [
        "reference", "entreprise_reference", "beneficiaire", "montant_accorde",
        "montant_justifie", "reste_a_justifier", "statut", "date_avance",
    ]
    list_filter = ["statut", "date_avance"]
    search_fields = ["reference", "objet", "beneficiaire__username"]
    inlines = [JustificationInline]


@admin.register(EvenementDepense)
class EvenementDepenseAdmin(EntrepriseAdminMixin, admin.ModelAdmin):
    list_display = ["reference_depense", "action", "acteur", "cree_le"]
    list_filter = ["action", "cree_le"]
    search_fields = ["reference_depense", "action"]
    readonly_fields = ["depense", "reference_depense", "action", "acteur", "donnees", "cree_le"]
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
