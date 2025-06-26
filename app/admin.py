from django.contrib import admin
from .models import UserDownload

@admin.register(UserDownload)
class PostAdmin(admin.ModelAdmin):
    list_display=['title','videoSlug','date','userIp']
    list_filter=['title','videoSlug','date','userIp']
    search_fields=['title','videoSlug','date','userIp']
    
