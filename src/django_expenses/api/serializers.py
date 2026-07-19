from rest_framework import serializers
from ..models import (
    Expense,
    ExpenseCategory,
    ExpenseType,
    CostCenter,
    ExpenseAttachment,
    ExpenseApproval,
    ExpensePayment,
    ExpenseComment,
)


class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = "__all__"


class ExpenseTypeSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = ExpenseType
        fields = "__all__"


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
    expense_type_name = serializers.CharField(
        source="expense_type.name", read_only=True
    )
    category_name = serializers.CharField(
        source="expense_type.category.name", read_only=True
    )
    cost_center_name = serializers.CharField(
        source="cost_center.name", read_only=True
    )
    username = serializers.CharField(source="user.username", read_only=True)
    total = serializers.DecimalField(
        source="total_amount", max_digits=15, decimal_places=2, read_only=True
    )

    class Meta:
        model = Expense
        fields = [
            "id", "reference_number", "status", "status_label",
            "amount", "tax_amount", "total", "currency",
            "description", "vendor", "date_incurred",
            "expense_type", "expense_type_name", "category_name",
            "cost_center", "cost_center_name",
            "user", "username", "payment_method",
            "date_submitted", "date_approved", "date_paid",
            "created_at", "updated_at",
        ]


class ExpenseDetailSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    expense_type_name = serializers.CharField(
        source="expense_type.name", read_only=True
    )
    category_name = serializers.CharField(
        source="expense_type.category.name", read_only=True
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
            "expense_type", "expense_type_name", "category_name",
            "cost_center", "cost_center_name",
            "user", "username", "approved_by", "approved_by_username",
            "rejection_reason", "payment_method",
            "date_submitted", "date_approved", "date_paid",
            "is_editable", "created_at", "updated_at",
            "attachments", "approvals", "payments", "comments",
        ]


class ExpenseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            "expense_type", "cost_center", "amount", "tax_amount",
            "currency", "description", "vendor", "date_incurred",
            "payment_method",
        ]
