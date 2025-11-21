from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'type', 'title', 'created_at', 'is_read']
    list_filter = ['type', 'read_at', 'created_at']
    search_fields = ['user__email', 'title', 'message']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def is_read(self, obj):
        return obj.is_read
    is_read.boolean = True

