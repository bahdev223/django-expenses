from rest_framework import serializers
from ..models import (
    Expense,
    ExpenseCategory,
    CostCenter,
    ExpenseAttachment,
    ExpenseApproval,
    ExpensePayment,
    ExpenseComment,
)


class ExpenseCategorySerializer(serializers.ModelSerializer):
    full_path = serializers.CharField(source="get_full_path", read_only=True)
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = ExpenseCategory
        fields = "__all__"

    def get_children_count(self, obj):
        return obj.children.filter(is_active=True).count()


class ExpenseCategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = ExpenseCategory
        fields = [
            "id", "code", "name", "parent", "expense_nature",
            "default_account_code", "default_vat_rate",
            "color", "icon", "sort_order", "is_active", "children",
        ]

    def get_children(self, obj):
        qs = obj.children.filter(is_active=True).order_by("sort_order", "code")
        return ExpenseCategoryTreeSerializer(qs, many=True).data


class CostCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostCenter
        fields = "__all__"


class ExpenseAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseAttachment
        fields = "__all__"
        read_only_fields = ["uploaded_at"]


class ExpenseApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseApproval
        fields = "__all__"
        read_only_fields = ["created_at"]


class ExpensePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpensePayment
        fields = "__all__"
        read_only_fields = ["created_at"]


class ExpenseCommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = ExpenseComment
        fields = "__all__"
        read_only_fields = ["created_at"]


class ExpenseListSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    category_path = serializers.CharField(
        source="category.get_full_path", read_only=True
    )
    expense_nature_label = serializers.CharField(
        source="get_expense_nature_display", read_only=True
    )
    cost_center_name = serializers.CharField(
        source="cost_center.name", read_only=True
    )
    username = serializers.CharField(source="user.username", read_only=True)
    total = serializers.DecimalField(
        source="total_amount", max_digits=15, decimal_places=2, read_only=True
    )
    suggested_account = serializers.CharField(
        source="suggested_account_code", read_only=True
    )

    class Meta:
        model = Expense
        fields = [
            "id", "reference_number", "status", "status_label",
            "amount", "tax_amount", "total", "currency",
            "description", "vendor", "date_incurred",
            "category", "category_path",
            "expense_nature", "expense_nature_label",
            "cost_center", "cost_center_name",
            "user", "username", "payment_method",
            "suggested_account",
            "date_submitted", "date_approved", "date_paid",
            "created_at", "updated_at",
        ]


class ExpenseDetailSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    category_path = serializers.CharField(
        source="category.get_full_path", read_only=True
    )
    expense_nature_label = serializers.CharField(
        source="get_expense_nature_display", read_only=True
    )
    cost_center_name = serializers.CharField(
        source="cost_center.name", read_only=True
    )
    username = serializers.CharField(source="user.username", read_only=True)
    approved_by_username = serializers.CharField(
        source="approved_by.username", read_only=True
    )
    total = serializers.DecimalField(
        source="total_amount", max_digits=15, decimal_places=2, read_only=True
    )
    is_editable = serializers.BooleanField(read_only=True)
    suggested_account = serializers.CharField(
        source="suggested_account_code", read_only=True
    )
    attachments = ExpenseAttachmentSerializer(many=True, read_only=True)
    approvals = ExpenseApprovalSerializer(many=True, read_only=True)
    payments = ExpensePaymentSerializer(many=True, read_only=True)
    comments = ExpenseCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Expense
        fields = [
            "id", "reference_number", "status", "status_label",
            "amount", "tax_amount", "total", "currency",
            "description", "vendor", "date_incurred",
            "category", "category_path",
            "expense_nature", "expense_nature_label",
            "cost_center", "cost_center_name",
            "user", "username", "approved_by", "approved_by_username",
            "rejection_reason", "payment_method",
            "suggested_account",
            "date_submitted", "date_approved", "date_paid",
            "is_editable", "created_at", "updated_at",
            "attachments", "approvals", "payments", "comments",
        ]


class ExpenseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            "id", "category", "expense_nature", "cost_center",
            "amount", "tax_amount", "currency",
            "description", "vendor", "date_incurred",
            "payment_method",
        ]
        read_only_fields = ["id"]
