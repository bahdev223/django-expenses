from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import include, path, reverse_lazy
from importlib.util import find_spec
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .constants import ExpenseStatus
from .hooks import HookRegistry
from .models import Expense
from .permissions import ADD_EXPENSE, CHANGE_EXPENSE, DELETE_EXPENSE, VIEW_EXPENSE
from .services import ExpenseService


app_name = "expenses"


class ExpenseQuerysetMixin:
    def scoped_queryset(self, qs):
        return HookRegistry.filter_queryset(qs, user=self.request.user, request=self.request)


class ExpenseListView(LoginRequiredMixin, PermissionRequiredMixin, ExpenseQuerysetMixin, ListView):
    permission_required = VIEW_EXPENSE
    raise_exception = True
    model = Expense
    template_name = "django_expenses/expense_list.html"
    paginate_by = 50

    def get_queryset(self):
        qs = Expense.objects.select_related("user", "category", "cost_center").filter(supprime_le__isnull=True)
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return self.scoped_queryset(qs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_choices"] = ExpenseStatus.CHOICES
        ctx["current_status"] = self.request.GET.get("status", "")
        return ctx


class ExpenseDetailView(LoginRequiredMixin, PermissionRequiredMixin, ExpenseQuerysetMixin, DetailView):
    permission_required = VIEW_EXPENSE
    raise_exception = True
    model = Expense
    template_name = "django_expenses/expense_detail.html"

    def get_queryset(self):
        qs = Expense.objects.select_related(
            "user", "category", "cost_center", "approved_by"
        ).prefetch_related(
            "attachments", "approvals__approved_by", "payments", "comments__user", "evenements"
        )
        return self.scoped_queryset(qs)


class ExpenseCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ADD_EXPENSE
    raise_exception = True
    model = Expense
    template_name = "django_expenses/expense_form.html"
    fields = [
        "category", "expense_nature", "cost_center", "amount", "tax_amount",
        "currency", "description", "vendor", "date_incurred",
    ]
    success_url = reverse_lazy("expenses:list")

    def form_valid(self, form):
        data = {name: form.cleaned_data.get(name) for name in self.fields}
        self.object = ExpenseService.create({**data, "user": self.request.user}, user=self.request.user)
        return HttpResponseRedirect(self.get_success_url())


class ExpenseUpdateView(LoginRequiredMixin, PermissionRequiredMixin, ExpenseQuerysetMixin, UpdateView):
    permission_required = CHANGE_EXPENSE
    raise_exception = True
    model = Expense
    template_name = "django_expenses/expense_form.html"
    fields = [
        "category", "expense_nature", "cost_center", "amount", "tax_amount",
        "currency", "description", "vendor", "date_incurred",
    ]
    success_url = reverse_lazy("expenses:list")

    def get_queryset(self):
        return self.scoped_queryset(Expense.objects.all())

    def form_valid(self, form):
        data = {name: form.cleaned_data.get(name) for name in self.fields}
        self.object = ExpenseService.update(self.get_object(), data, user=self.request.user)
        return HttpResponseRedirect(self.get_success_url())


class ExpenseDeleteView(LoginRequiredMixin, PermissionRequiredMixin, ExpenseQuerysetMixin, DeleteView):
    permission_required = DELETE_EXPENSE
    raise_exception = True
    model = Expense
    template_name = "django_expenses/expense_confirm_delete.html"
    success_url = reverse_lazy("expenses:list")

    def get_queryset(self):
        return self.scoped_queryset(Expense.objects.all())

    def form_valid(self, form):
        ExpenseService.delete(self.object, user=self.request.user)
        return HttpResponseRedirect(self.get_success_url())


urlpatterns = [
    path("", ExpenseListView.as_view(), name="list"),
    path("<int:pk>/", ExpenseDetailView.as_view(), name="detail"),
    path("create/", ExpenseCreateView.as_view(), name="create"),
    path("<int:pk>/update/", ExpenseUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", ExpenseDeleteView.as_view(), name="delete"),
]

if find_spec("rest_framework") is not None:
    urlpatterns.append(
        path("api/", include("django_expenses.api.urls", namespace="expenses_api"))
    )
