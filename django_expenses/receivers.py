from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Expense
from .signals import (
    expense_created,
    expense_updated,
    expense_submitted,
    expense_approved,
    expense_rejected,
    expense_paid,
    expense_cancelled,
)


@receiver(pre_save, sender=Expense, dispatch_uid="expense_auto_reference")
def expense_auto_reference(sender, instance, **kwargs):
    if not instance.reference_number and instance.pk:
        instance.reference_number = generate_reference(instance)


@receiver(post_save, sender=Expense, dispatch_uid="expense_emit_signals")
def expense_emit_signals(sender, instance, created, **kwargs):
    if created:
        expense_created.send(sender=Expense, expense=instance, user=instance.user)
    else:
        expense_updated.send(sender=Expense, expense=instance, user=instance.user)


def emit_status_signal(instance, old_status):
    signal_map = {
        "submitted": expense_submitted,
        "approved": expense_approved,
        "rejected": expense_rejected,
        "paid": expense_paid,
        "cancelled": expense_cancelled,
    }
    signal = signal_map.get(instance.status)
    if signal and instance.status != old_status:
        signal.send(sender=Expense, expense=instance, user=instance.user)


def generate_reference(instance):
    prefix = "DEP"
    year = instance.created_at.strftime("%Y")
    month = instance.created_at.strftime("%m")
    return f"{prefix}-{year}{month}-{instance.pk:06d}"
