
# models.py
from django.db import models
from django.utils import timezone
import json

class UserDownload(models.Model):
    # Información básica del video
    title = models.CharField(max_length=250, default='Unknown')
    videoSlug = models.SlugField(max_length=250, default='unknown')
    video_url = models.URLField()
    format = models.CharField(max_length=10, choices=[('video', 'Video'), ('audio', 'Audio')])
    quality = models.CharField(max_length=10, default='high')
    
    # Información del usuario
    user_ip = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    browser_name = models.CharField(max_length=100, blank=True, null=True)
    browser_version = models.CharField(max_length=50, blank=True, null=True)
    operating_system = models.CharField(max_length=100, blank=True, null=True)
    device_type = models.CharField(max_length=50, blank=True, null=True)  # mobile, desktop, tablet
    
    # Información de ubicación y configuración
    language = models.CharField(max_length=10, blank=True, null=True)
    timezone = models.CharField(max_length=50, blank=True, null=True)
    screen_resolution = models.CharField(max_length=20, blank=True, null=True)
    viewport_size = models.CharField(max_length=20, blank=True, null=True)
    
    # Información de red y rendimiento
    connection_type = models.CharField(max_length=20, blank=True, null=True)
    download_speed = models.CharField(max_length=20, blank=True, null=True)
    
    # Información de sesión
    session_duration = models.IntegerField(default=0)  # en segundos
    page_views = models.IntegerField(default=1)
    referrer = models.URLField(blank=True, null=True)
    
    # Timestamps
    date = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    # JSON con información adicional completa
    user_info = models.JSONField(null=True, blank=True)
    
    # Campos de análisis
    is_mobile = models.BooleanField(default=False)
    is_bot = models.BooleanField(default=False)
    download_successful = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user_ip', 'date']),
            models.Index(fields=['format', 'date']),
            models.Index(fields=['is_mobile', 'date']),
        ]

    def __str__(self):
        return f"{self.title} ({self.format}) - {self.user_ip} - {self.date.strftime('%Y-%m-%d %H:%M')}"
    
    def save(self, *args, **kwargs):
        # Detectar si es móvil basado en user_agent
        if self.user_agent:
            mobile_indicators = ['Mobile', 'Android', 'iPhone', 'iPad', 'Windows Phone']
            self.is_mobile = any(indicator in self.user_agent for indicator in mobile_indicators)
            
            # Detectar bots
            bot_indicators = ['bot', 'crawler', 'spider', 'scraper']
            self.is_bot = any(indicator.lower() in self.user_agent.lower() for indicator in bot_indicators)
        
        super().save(*args, **kwargs)
