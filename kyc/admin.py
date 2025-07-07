from django.contrib import admin
from .models import KYCSubmission, ContactFormSubmission

@admin.register(KYCSubmission)
class KYCSubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'submitted_at', 'get_name', 'get_email']
    list_filter = ['status', 'submitted_at']
    search_fields = ['user__username', 'data__firstName', 'data__lastName', 'data__email']
    readonly_fields = ['submitted_at']
    
    def get_name(self, obj):
        data = obj.data
        if data.get('firstName') and data.get('lastName'):
            return f"{data['firstName']} {data['lastName']}"
        return 'N/A'
    get_name.short_description = 'Name'
    
    def get_email(self, obj):
        return obj.data.get('email', 'N/A')
    get_email.short_description = 'Email'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'status', 'submitted_at')
        }),
        ('KYC Data', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ContactFormSubmission)
class ContactFormSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'submitted_at', 'is_read']
    list_filter = ['is_read', 'submitted_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['submitted_at']
    list_editable = ['is_read']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'submitted_at')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
    )
