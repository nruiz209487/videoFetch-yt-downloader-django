from django.contrib import admin
from .models import UserDownload

@admin.register(UserDownload)
class UserDownloadAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'videoSlug', 'video_url', 'format', 'quality',
        'user_ip', 'user_agent', 'browser_name', 'browser_version',
        'operating_system', 'device_type', 'language', 'timezone',
        'screen_resolution', 'viewport_size', 'connection_type',
        'download_speed', 'session_duration', 'page_views', 'referrer',
        'date', 'last_activity', 'user_info', 'is_mobile', 'is_bot',
        'download_successful'
    )
    list_filter = (
        'format', 'date', 'user_ip', 'is_mobile', 'is_bot', 'download_successful',
        'operating_system', 'browser_name', 'device_type', 'language'
    )
    search_fields = (
        'title', 'videoSlug', 'video_url', 'user_ip', 'user_agent', 'referrer'
    )
