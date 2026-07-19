from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class ExpenseComment(models.Model):
    expense = models.ForeignKey(
        "Expense",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
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
