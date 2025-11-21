from django.contrib import admin
from .models import FIR, ActionLog

class FIRAdmin(admin.ModelAdmin):
    list_display = ('case_id', 'title', 'status', 'last_updated')
    readonly_fields = ('last_updated',)

    # Logic: Sirf Superuser (Main Admin) delete kar sakta hai
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    # Jab save ho tu current user save krne k liye (Optional helper)
    def save_model(self, request, obj, form, change):
        if not change: # Agar nayi FIR hai
             obj.officer_assigned = request.user
        super().save_model(request, obj, form, change)

admin.site.register(FIR, FIRAdmin)
admin.site.register(ActionLog)