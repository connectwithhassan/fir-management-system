from django.db import models
from django.contrib.auth.models import User

# Options
STATUS_CHOICES = (
    ('PENDING', 'Pending Investigation'),
    ('SOLVED', 'Case Solved'),
    ('SNOOZED', 'Snoozed (Warning)'), 
    ('EXPIRED', 'Expired Case'),
)

# 1. FIR Model
class FIR(models.Model):
    case_id = models.CharField(max_length=20, unique=True, help_text="Example: FIR-2024-001")
    title = models.CharField(max_length=200)
    description = models.TextField()
    officer_assigned = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="firs")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    created_at = models.DateTimeField(auto_now_add=True)  # Jab bani
    last_updated = models.DateTimeField(auto_now=True)    # Jab bhi change hoi

    def __str__(self):
        return f"{self.case_id} - {self.title}"

# 2. Activity Log (Jo Admin dekhega)
class ActionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    action = models.CharField(max_length=255) # E.g., "Created FIR-001"
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action}"