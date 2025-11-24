from django.contrib import admin
from .models import Membership, Recognition, Training, Publication, Certificate, CSEStatus

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization_name', 'position', 'membership_type', 'date_joined', 'is_current']
    list_filter = ['membership_type', 'date_joined']
    search_fields = ['user__username', 'user__email', 'organization_name', 'position']
    date_hierarchy = 'date_joined'


@admin.register(Recognition)
class RecognitionAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'issuing_organization', 'date_received']
    list_filter = ['date_received', 'issuing_organization']
    search_fields = ['user__username', 'user__email', 'title', 'issuing_organization']
    date_hierarchy = 'date_received'


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'organization', 'date_start', 'date_end', 'location']
    list_filter = ['date_start', 'organization']
    search_fields = ['user__username', 'user__email', 'title', 'organization', 'location']
    date_hierarchy = 'date_start'


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'publication_type', 'date_published', 'publisher']
    list_filter = ['publication_type', 'date_published']
    search_fields = ['user__username', 'user__email', 'title', 'authors', 'publisher', 'doi']
    date_hierarchy = 'date_published'


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['user', 'certificate_type', 'issuing_body', 'date_issued', 'expiry_date', 'is_active']
    list_filter = ['date_issued', 'issuing_body']
    search_fields = ['user__username', 'user__email', 'certificate_type', 'certificate_number', 'issuing_body']
    date_hierarchy = 'date_issued'


@admin.register(CSEStatus)
class CSEStatusAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'current_position', 'current_company', 'industry', 'is_current']
    list_filter = ['status', 'is_current']
    search_fields = ['user__username', 'user__email', 'current_position', 'current_company', 'industry']
    
# Register your models here.
