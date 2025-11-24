from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import FIR, ActionLog

@receiver(post_save, sender=FIR)
def log_fir_save(sender, instance, created, **kwargs):
    action_type = "New FIR Registered" if created else "FIR Updated"
    ActionLog.objects.create(action=f"{action_type}: {instance.case_id} (Status: {instance.status})")

@receiver(post_delete, sender=FIR)
def log_fir_delete(sender, instance, **kwargs):
    ActionLog.objects.create(action=f"FIR DELETED: {instance.case_id}")