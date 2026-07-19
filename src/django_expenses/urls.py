from django.urls import path
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Expense
from .services import ExpenseService


app_name = "expenses"


class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = "django_expenses/expense_list.html"
    paginate_by = 50

    def get_queryset(self):
        qs = Expense.objects.select_related(
            "user", "category", "cost_center"
        )
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_choices"] = Expense.Status.choices
        ctx["current_status"] = self.request.GET.get("status", "")
        return ctx


class ExpenseDetailView(LoginRequiredMixin, DetailView):
    model = Expense
    template_name = "django_expenses/expense_detail.html"

    def get_queryset(self):
        return Expense.objects.select_related(
            "user", "category", "cost_center", "approved_by"
        ).prefetch_related(
            "attachments",
            "approvals__approved_by",
            "payments",
            "comments__user",
        )


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    template_name = "django_expenses/expense_form.html"
    fields = [
        "category",
        "expense_nature",
        "cost_center",
        "amount",
        "tax_amount",
        "currency",
        "description",
        "vendor",
        "date_incurred",
    ]
    success_url = reverse_lazy("expenses:list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    model = Expense
    template_name = "django_expenses/expense_form.html"
    fields = [
        "category",
        "expense_nature",
        "cost_center",
        "amount",
        "tax_amount",
        "currency",
        "description",
        "vendor",
        "date_incurred",
    ]
    success_url = reverse_lazy("expenses:list")


class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    model = Expense
    template_name = "django_expenses/expense_confirm_delete.html"
    success_url = reverse_lazy("expenses:list")


urlpatterns = [
    path("", ExpenseListView.as_view(), name="list"),
    path("<int:pk>/", ExpenseDetailView.as_view(), name="detail"),
    path("create/", ExpenseCreateView.as_view(), name="create"),
    path("<int:pk>/update/", ExpenseUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", ExpenseDeleteView.as_view(), name="delete"),
]
