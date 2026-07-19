from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .managers import ExpenseQuerySet


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = _("Expense category")
        verbose_name_plural = _("Expense categories")

    def __str__(self):
        return self.name


class ExpenseType(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        ExpenseCategory, on_delete=models.CASCADE, related_name="expense_types"
    )
    description = models.TextField(blank=True)
    requires_approval = models.BooleanField(default=True)
    max_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Expense type")
        verbose_name_plural = _("Expense types")

    def __str__(self):
        return self.name


class CostCenter(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="managed_cost_centers",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        verbose_name = _("Cost center")
        verbose_name_plural = _("Cost centers")

    def __str__(self):
        return f"{self.code} - {self.name}"


class Expense(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Brouillon")
        SUBMITTED = "submitted", _("Soumise")
        PENDING_APPROVAL = "pending_approval", _("En attente d'approbation")
        APPROVED = "approved", _("Approuvée")
        REJECTED = "rejected", _("Rejetée")
        PAID = "paid", _("Payée")
        ARCHIVED = "archived", _("Archivée")
        CANCELLED = "cancelled", _("Annulée")

    class PaymentMethod(models.TextChoices):
        CASH = "cash", _("Espèces")
        CHECK = "check", _("Chèque")
        BANK_TRANSFER = "bank_transfer", _("Virement bancaire")
        MOBILE_MONEY = "mobile_money", _("Mobile Money")
        CARD = "card", _("Carte bancaire")
        OTHER = "other", _("Autre")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="expenses"
    )
    expense_type = models.ForeignKey(
        ExpenseType, on_delete=models.PROTECT, related_name="expenses"
    )
    cost_center = models.ForeignKey(
        CostCenter, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="expenses",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT,
        db_index=True,
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="XOF")
    description = models.TextField()
    vendor = models.CharField(max_length=300, blank=True)
    date_incurred = models.DateField()
    date_submitted = models.DateTimeField(null=True, blank=True)
    date_approved = models.DateTimeField(null=True, blank=True)
    date_paid = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="approved_expenses",
    )
    rejection_reason = models.TextField(blank=True)
    payment_method = models.CharField(
        max_length=20, choices=PaymentMethod.choices, blank=True,
    )
    reference_number = models.CharField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ExpenseQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Expense")
        verbose_name_plural = _("Expenses")
        permissions = [
            ("approve_expense", _("Can approve expenses")),
            ("pay_expense", _("Can mark expenses as paid")),
            ("view_expense_reports", _("Can view expense reports")),
        ]

    def __str__(self):
        return f"{self.reference_number or '---'} - {self.amount} {self.currency}"

    @property
    def total_amount(self):
        return self.amount + self.tax_amount

    @property
    def is_editable(self):
        return self.status in (self.Status.DRAFT, self.Status.REJECTED)


class ExpenseAttachment(models.Model):
    expense = models.ForeignKey(
        Expense, on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.FileField(upload_to="expenses/attachments/%Y/%m/")
    filename = models.CharField(max_length=500)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = _("Expense attachment")
        verbose_name_plural = _("Expense attachments")

    def __str__(self):
        return self.filename


class ExpenseApproval(models.Model):
    class Decision(models.TextChoices):
        APPROVED = "approved", _("Approuvée")
        REJECTED = "rejected", _("Rejetée")

    expense = models.ForeignKey(
        Expense, on_delete=models.CASCADE, related_name="approvals"
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="expense_approvals",
    )
    decision = models.CharField(max_length=10, choices=Decision.choices)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Expense approval")
        verbose_name_plural = _("Expense approvals")

    def __str__(self):
        return f"{self.expense} - {self.get_decision_display()}"


class ExpensePayment(models.Model):
    expense = models.ForeignKey(
        Expense, on_delete=models.CASCADE, related_name="payments"
    )
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(
        max_length=20, choices=Expense.PaymentMethod.choices, blank=True,
    )
    reference = models.CharField(max_length=200, blank=True)
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name="expense_payments",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-payment_date"]
        verbose_name = _("Expense payment")
        verbose_name_plural = _("Expense payments")

    def __str__(self):
        return f"{self.expense} - {self.amount_paid}"


class ExpenseComment(models.Model):
    expense = models.ForeignKey(
        Expense, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="expense_comments",
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("Expense comment")
        verbose_name_plural = _("Expense comments")

    def __str__(self):
        return f"{self.user} - {self.created_at}"
