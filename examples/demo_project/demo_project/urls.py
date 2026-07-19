from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("expenses/", include("django_expenses.urls", namespace="expenses")),
    path("api/", include("django_expenses.api.urls")),
]
