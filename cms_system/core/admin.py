from django.contrib import admin
from .models import FIR, Criminal, ActionLog, PoliceOfficer

class PoliceOfficerAdmin(admin.ModelAdmin):
    list_display = ('name', 'rank', 'badge_number')
    search_fields = ('name', 'badge_number')

class CriminalAdmin(admin.ModelAdmin):
    list_display = ('name', 'alias', 'cnic')
    search_fields = ['name', 'cnic', 'alias']

class FIRAdmin(admin.ModelAdmin):
    list_display = ('case_id', 'title', 'date_reported', 'status', 'officer_assigned')
    list_filter = ('status', 'date_reported', 'officer_assigned')
    autocomplete_fields = ['suspects', 'officer_assigned']
    
    fieldsets = (
        ('Case Info', {'fields': ('case_id', 'title', 'date_reported', 'status', 'officer_assigned')}),
        ('Suspect Info', {'fields': ('is_unknown_suspect', 'suspects')}),
        ('Evidence', {'fields': ('fir_image', 'description')}),
    )
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    list_filter = ('user', 'timestamp')
    def has_module_permission(self, request): return request.user.is_superuser
    def has_view_permission(self, request, obj=None): return request.user.is_superuser
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

admin.site.register(FIR, FIRAdmin)
admin.site.register(Criminal, CriminalAdmin)
admin.site.register(PoliceOfficer, PoliceOfficerAdmin)
admin.site.register(ActionLog, ActionLogAdmin)