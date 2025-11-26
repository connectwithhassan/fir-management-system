from django.contrib import admin
from .models import FIR, Accused, ActionLog, PoliceOfficer, Remand, BailApplication, BailSurety

# --- Inlines for FIR Admin ---
class RemandInline(admin.StackedInline):
    model = Remand
    extra = 0
    verbose_name = "Remand Details"
    verbose_name_plural = "Remand"
    fieldsets = (
        (None, {
            'fields': ('date', 'accused_name', 'io_name', 'section_count', 'order_copy', 'remand_type')
        }),
        ('Police Remand', {
            'fields': ('police_remand_details',),
            'classes': ('collapse',), # Click to expand
        }),
        ('Judicial Remand', {
            'fields': ('judicial_remand_image',),
            'classes': ('collapse',),
        }),
    )

# --- Bail Surety Inline for Bail Application Admin ---
class BailSuretyInline(admin.TabularInline):
    model = BailSurety
    extra = 1
    verbose_name = "Bail Surety"

# --- Main Admin Classes ---

@admin.register(BailApplication)
class BailApplicationAdmin(admin.ModelAdmin):
    list_display = ('fir', 'date', 'advocate_name')
    inlines = [BailSuretyInline]

class PoliceOfficerAdmin(admin.ModelAdmin):
    list_display = ('name', 'rank', 'phone_number')
    search_fields = ('name', 'phone_number')
    verbose_name_plural = "Police Officers"

class AccusedAdmin(admin.ModelAdmin):
    list_display = ('name', 'father_name', 'cnic')
    search_fields = ['name', 'cnic', 'father_name']
    verbose_name_plural = "Accused"

class FIRAdmin(admin.ModelAdmin):
    list_display = ('fir_no', 'title', 'date_reported', 'status_badge', 'officer_assigned')
    list_filter = ('status', 'date_reported', 'officer_assigned', 'police_station')
    search_fields = ('fir_no', 'title', 'police_station', 'criminal_case_no')
    autocomplete_fields = ['accuseds', 'officer_assigned']

    fieldsets = (
        ('Basic Information', {'fields': ('fir_no', 'police_station', 'criminal_case_no', 'title', 'date_reported', 'status', 'officer_assigned')}),
        ('Accused Information', {'fields': ('is_unknown_accused', 'accuseds')}),
        ('Case Property & Investigation', {'fields': ('case_property_image', 'description', 'personal_search_item')}),
    )

    inlines = [RemandInline]

    def status_badge(self, obj):
        return obj.get_status_display()
    status_badge.short_description = 'Status'

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
admin.site.register(Accused, AccusedAdmin)
admin.site.register(PoliceOfficer, PoliceOfficerAdmin)
admin.site.register(ActionLog, ActionLogAdmin)