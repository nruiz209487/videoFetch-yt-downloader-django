from django.urls import path
from . import views
app_name = 'app'
urlpatterns = [
    path('',views.home, name="app"),
    path('descargar-video/', views.descargar_video, name='descargar_video'),
    path('descargar-audio/', views.descargar_audio, name='descargar_audio'),
]