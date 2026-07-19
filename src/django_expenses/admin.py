from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Expense,
    ExpenseCategory,
    ExpenseType,
    CostCenter,
    ExpenseAttachment,
    ExpenseApproval,
    ExpensePayment,
    ExpenseComment,
)
from .services import ExpenseService


class ApprovalInline(admin.TabularInline):
    model = ExpenseApproval
    extra = 0
    readonly_fields = ["approved_by", "decision", "comment", "created_at"]
    can_delete = False


class PaymentInline(admin.TabularInline):
    model = ExpensePayment
    extra = 0
    readonly_fields = [
        "amount_paid", "payment_date", "payment_method", "reference", "paid_by"
    ]


class AttachmentInline(admin.TabularInline):
    model = ExpenseAttachment
    extra = 0
    readonly_fields = ["filename", "uploaded_at"]


class CommentInline(admin.TabularInline):
    model = ExpenseComment
    extra = 0
    readonly_fields = ["user", "comment", "created_at"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = [
        "reference_number",
        "colored_status",
        "user",
        "expense_type",
        "cost_center",
        "amount_display",
        "total_display",
        "date_incurred",
    ]
    list_filter = [
        "status",
        "expense_type__category",
        "cost_center",
        "currency",
        "date_incurred",
    ]
    search_fields = ["reference_number", "description", "vendor", "user__username"]
    list_select_related = ["user", "expense_type__category", "cost_center"]
    date_hierarchy = "date_incurred"
    readonly_fields = [
        "reference_number",
        "status",
        "date_submitted",
        "date_approved",
        "date_paid",
        "approved_by",
        "created_at",
        "updated_at",
    ]
    fieldsets = [
        ("Identification", {
            "fields": ["reference_number", "status", "user", "expense_type", "cost_center"]
        }),
        ("Montants", {"fields": ["amount", "tax_amount", "currency"]}),
        ("Détails", {"fields": ["description", "vendor", "date_incurred"]}),
        ("Paiement", {
            "fields": ["payment_method", "approved_by", "rejection_reason"]
        }),
        ("Dates", {
            "fields": [
                "date_submitted", "date_approved", "date_paid",
                "created_at", "updated_at"
            ]
        }),
    ]
    inlines = [ApprovalInline, PaymentInline, AttachmentInline, CommentInline]
    actions = ["export_csv", "mark_paid", "mark_archived"]

    def colored_status(self, obj):
        colors = {
            "draft": "gray",
            "submitted": "blue",
            "pending_approval": "orange",
            "approved": "green",
            "rejected": "red",
            "paid": "teal",
            "archived": "gray",
            "cancelled": "darkgray",
        }
        c = colors.get(obj.status, "gray")
        return format_html(
            '<span style="color:{};font-weight:bold;">{}</span>',
            c,
            obj.get_status_display(),
        )
    colored_status.short_description = "Status"

    def amount_display(self, obj):
        return f"{obj.amount:,.2f}"
    amount_display.short_description = "Montant"

    def total_display(self, obj):
        return f"{obj.total_amount:,.2f}"
    total_display.short_description = "Total TTC"

    def export_csv(self, request, queryset):
        return ExpenseService.export_csv(queryset)
    export_csv.short_description = "Export CSV sélection"

    def mark_paid(self, request, queryset):
        count = 0
        for expense in queryset.filter(status="approved"):
            ExpenseService.pay(expense, user=request.user)
            count += 1
        self.message_user(request, f"{count} dépenses marquées payées.")
    mark_paid.short_description = "Marquer comme payée(s)"

    def mark_archived(self, request, queryset):
        count = 0
        for expense in queryset.filter(status="paid"):
            ExpenseService.archive(expense, user=request.user)
            count += 1
        self.message_user(request, f"{count} dépenses archivées.")
    mark_archived.short_description = "Archiver la sélection"


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "sort_order", "is_active", "expense_count"]
    list_filter = ["is_active"]
    search_fields = ["name"]
    list_editable = ["sort_order", "is_active"]

    def expense_count(self, obj):
        return Expense.objects.filter(expense_type__category=obj).count()
    expense_count.short_description = "Dépenses"


@admin.register(ExpenseType)
class ExpenseTypeAdmin(admin.ModelAdmin):
    list_display = [
        "name", "category", "requires_approval", "max_amount", "is_active"
    ]
    list_filter = ["category", "requires_approval", "is_active"]
    search_fields = ["name"]
    autocomplete_fields = ["category"]


@admin.register(CostCenter)
class CostCenterAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "manager", "is_active", "expense_count"]
    list_filter = ["is_active"]
    search_fields = ["code", "name", "description"]
    autocomplete_fields = ["manager"]

    def expense_count(self, obj):
        return obj.expenses.count()
    expense_count.short_description = "Dépenses"


@admin.register(ExpenseApproval)
class ExpenseApprovalAdmin(admin.ModelAdmin):
    list_display = ["expense", "approved_by", "decision", "created_at"]
    list_filter = ["decision"]
    search_fields = ["expense__reference_number", "approved_by__username"]
    readonly_fields = ["expense", "approved_by", "decision", "comment", "created_at"]


@admin.register(ExpensePayment)
class ExpensePaymentAdmin(admin.ModelAdmin):
    list_display = ["expense", "amount_paid", "payment_date", "payment_method", "paid_by"]
    list_filter = ["payment_method", "payment_date"]
    search_fields = ["reference", "expense__reference_number"]


@admin.register(ExpenseAttachment)
class ExpenseAttachmentAdmin(admin.ModelAdmin):
    list_display = ["filename", "expense", "uploaded_at"]
    readonly_fields = ["expense", "file", "filename", "uploaded_at"]


@admin.register(ExpenseComment)
class ExpenseCommentAdmin(admin.ModelAdmin):
    list_display = ["expense", "user", "short_comment", "created_at"]
    readonly_fields = ["expense", "user", "comment", "created_at"]

    def short_comment(self, obj):
        return obj.comment[:80] + "..." if len(obj.comment) > 80 else obj.comment
    short_comment.short_description = "Commentaire"
