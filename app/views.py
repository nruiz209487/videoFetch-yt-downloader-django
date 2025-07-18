from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from .models import UserDownload
import os
import mimetypes
import threading
import time
import json
import sys
import re
import uuid

from .service.DownloaderWeb import DownloaderWeb

def home(request):
    return render(request, 'home/homePage.html')

def validate_video_url(url):
    errors = []
    
    if not url:
        errors.append('La URL del video es obligatoria.')
        return errors
    
    if not re.match(r'^https?://', url):
        errors.append('La URL debe comenzar con http:// o https://')
    
    dominios_validos = [
        'youtube.com', 'youtu.be', 'vimeo.com', 'facebook.com',
        'instagram.com', 'twitter.com', 'tiktok.com', 'dailymotion.com',
        'twitch.tv', 'streamable.com'
    ]
    
    if not any(dominio in url.lower() for dominio in dominios_validos):
        errors.append('Esta plataforma no está soportada. Prueba con YouTube, Vimeo, Facebook, Instagram, Twitter, TikTok, etc.')
    
    if 'playlist' in url.lower():
        errors.append('Las listas de reproducción no están soportadas. Por favor, usa el enlace de un video individual.')
    
    return errors

def safe_redirect_to_home(request):
    """Función helper para redireccionar de forma segura al home"""
    try:
        return redirect('home')
    except:
        return redirect('/')

def descargar_video(request):
    if request.method == 'POST':
        video_url = request.POST.get('video_url')
        user_info_str = request.POST.get('user_info')
        
        validation_errors = validate_video_url(video_url)
        if validation_errors:
            for error in validation_errors:
                messages.error(request, error)
            return safe_redirect_to_home(request)
        
        try:
            user_info = json.loads(user_info_str) if user_info_str else {}
            print("=== USER INFO PARA DESCARGA ===")
            print(json.dumps(user_info, indent=2))
            storeUserData(user_info)
        except json.JSONDecodeError:
            print("Error al decodificar user_info para descarga, usando dict vacío.")
            user_info = {}
            storeUserData(user_info)
        
        format_requested = user_info.get('format', 'video')
        
        try:
            if format_requested == 'audio':
                resultado = DownloaderWeb.descargar_audio_para_web(video_url)
                content_type = 'audio/mpeg'
                success_message = f'Audio "{resultado.get("title", "Audio")}" descargado exitosamente.'
            else:
                resultado = DownloaderWeb.descargar_video_para_web(video_url)
                content_type, _ = mimetypes.guess_type(resultado.get('file_path', ''))
                if not content_type:
                    content_type = 'video/mp4'
                success_message = f'Video "{resultado.get("title", "Video")}" descargado exitosamente.'
            
            if resultado['success']:
                file_path = resultado['file_path']
                filename = resultado['filename']
                temp_dir = resultado['temp_dir']
                
                try:
                    if user_info.get('user_ip'):
                        recent_download = UserDownload.objects.filter(
                            user_ip=user_info.get('user_ip'),
                            video_url=video_url
                        ).order_by('-date').first()
                        
                        if recent_download:
                            recent_download.download_successful = True
                            recent_download.title = resultado.get('title', 'Downloaded')
                            recent_download.save()
                except Exception as e:
                    print(f"Error actualizando registro de descarga: {e}")
                
                if os.path.exists(file_path):
                    response = FileResponse(
                        open(file_path, 'rb'),
                        content_type=content_type,
                        as_attachment=True,
                        filename=filename
                    )
                    
                    def limpiar_despues():
                        time.sleep(10) 
                        DownloaderWeb.limpiar_archivo_temporal(temp_dir)
                    
                    thread = threading.Thread(target=limpiar_despues)
                    thread.daemon = True
                    thread.start()
                    
                    messages.success(request, success_message)
                    return response
                else:
                    raise Exception("El archivo descargado no se encontró.")
            else:
                error_message = f'Error al descargar el {"audio" if format_requested == "audio" else "video"}: {resultado["error"]}'
                messages.error(request, error_message)
                
        except Exception as e:
            error_message = f'Error al procesar la descarga de {"audio" if format_requested == "audio" else "video"}: {str(e)}'
            messages.error(request, error_message)
            print(f"Error en descarga: {e}")
    
    return safe_redirect_to_home(request)

def descargar_audio(request):
    if request.method == 'POST':
        video_url = request.POST.get('video_url')
        videoQuality = request.POST.get('videoQuality')
        user_info_str = request.POST.get('user_info')
        
        validation_errors = validate_video_url(video_url)
        if validation_errors:
            for error in validation_errors:
                messages.error(request, error)
            return safe_redirect_to_home(request)
        
        try:
            user_info = json.loads(user_info_str) if user_info_str else {}
            print("=== USER INFO PARA AUDIO ===")
            print(json.dumps(user_info, indent=2))
            storeUserData(user_info)
        except json.JSONDecodeError:
            print("Error al decodificar user_info para audio, usando dict vacío.")
            user_info = {}
            storeUserData(user_info)

        try:
            resultado = DownloaderWeb.descargar_audio_para_web(video_url)
            
            if resultado['success']:
                file_path = resultado['file_path']
                filename = resultado['filename']
                temp_dir = resultado['temp_dir']
                
                try:
                    if user_info.get('user_ip'):
                        recent_download = UserDownload.objects.filter(
                            user_ip=user_info.get('user_ip'),
                            video_url=video_url
                        ).order_by('-date').first()
                        
                        if recent_download:
                            recent_download.download_successful = True
                            recent_download.title = resultado.get('title', 'Audio Downloaded')
                            recent_download.save()
                except Exception as e:
                    print(f"Error actualizando registro de descarga: {e}")
                
                if os.path.exists(file_path):
                    response = FileResponse(
                        open(file_path, 'rb'),
                        content_type='audio/mpeg',
                        as_attachment=True,
                        filename=filename
                    )
                    
                    def limpiar_despues():
                        time.sleep(10)
                        DownloaderWeb.limpiar_archivo_temporal(temp_dir)
                    
                    thread = threading.Thread(target=limpiar_despues)
                    thread.daemon = True
                    thread.start()
                    
                    messages.success(request, f'Audio "{resultado.get("title", "Audio")}" descargado exitosamente.')
                    
                    return response
                else:
                    raise Exception("El archivo de audio no se encontró.")
            else:
                messages.error(request, f'Error al descargar el audio: {resultado["error"]}')
                
        except Exception as e:
            messages.error(request, f'Error al procesar la descarga de audio: {str(e)}')
            print(f"Error en descarga de audio: {e}")

    return safe_redirect_to_home(request)


def storeUserData(user_info):
    """Función mejorada para almacenar datos del usuario"""
    print("=== DEBUG: Datos recibidos ===")
    print(json.dumps(user_info, indent=2))
    
    try:
        user_ip = user_info.get('user_ip', '0.0.0.0')
        user_agent = user_info.get('browser', '')
        
        browser_info = parse_user_agent(user_agent)

        user_download = UserDownload.objects.create(
            title=user_info.get('title', 'Unknown'),
            videoSlug=user_info.get('video_slug', 'unknown'),
            video_url=user_info.get('video_url', ''),
            format=user_info.get('format', 'video'),
            quality=user_info.get('quality', 'high'),
            
            user_ip=user_ip,
            user_agent=user_agent,
            browser_name=browser_info.get('name', ''),
            browser_version=browser_info.get('version', ''),
            operating_system=browser_info.get('os', ''),
            device_type=browser_info.get('device_type', ''),
            
            language=user_info.get('language', ''),
            timezone=user_info.get('user_timezone', user_info.get('timezone', '')),
            screen_resolution=user_info.get('screen_resolution', ''),
            viewport_size=user_info.get('viewport_size', ''),
            
            connection_type=user_info.get('connection_type', ''),
            download_speed=user_info.get('download_speed', ''),
            
            session_duration=user_info.get('session_duration', 0),
            page_views=user_info.get('page_views', 1),
            referrer=user_info.get('referrer', ''),
            
            user_info=user_info,
            
            is_mobile=browser_info.get('device_type') == 'mobile',
        )
        
        print(f"✅ Usuario guardado exitosamente: ID {user_download.id}")
        print(f"   - IP: {user_ip}")
        print(f"   - Navegador: {browser_info.get('name')} en {browser_info.get('os')}")
        print(f"   - Dispositivo: {browser_info.get('device_type')}")
        print(f"   - Formato: {user_info.get('format', 'video')}")
        print(f"   - URL: {user_info.get('video_url', 'N/A')}")
        
        return user_download
        
    except Exception as e:
        print(f"❌ Error al guardar usuario: {e}")
        print(f"   - Tipo de error: {type(e).__name__}")
        print(f"   - Datos que causaron el error: {user_info}")
        return None

def parse_user_agent(user_agent):
    if not user_agent:
        return {'name': '', 'version': '', 'os': '', 'device_type': 'desktop'}
    
    ua = user_agent.lower()
    
    if 'edg' in ua: 
        browser = 'Edge'
    elif 'chrome' in ua and 'chromium' not in ua:
        browser = 'Chrome'
    elif 'firefox' in ua:
        browser = 'Firefox'
    elif 'safari' in ua and 'chrome' not in ua:
        browser = 'Safari'
    elif 'opera' in ua or 'opr' in ua:
        browser = 'Opera'
    else:
        browser = 'Unknown'
        
    if 'windows nt 10' in ua:
        os_name = 'Windows 10/11'
    elif 'windows nt' in ua:
        os_name = 'Windows'
    elif 'mac os x' in ua:
        os_name = 'macOS'
    elif 'linux' in ua and 'android' not in ua:
        os_name = 'Linux'
    elif 'android' in ua:
        os_name = 'Android'
    elif 'iphone' in ua or 'ipad' in ua:
        os_name = 'iOS'
    else:
        os_name = 'Unknown'
    
    if any(x in ua for x in ['mobile', 'android', 'iphone']):
        device_type = 'mobile'
    elif 'tablet' in ua or 'ipad' in ua:
        device_type = 'tablet'
    else:
        device_type = 'desktop'
    
    return {
        'name': browser,
        'version': '', 
        'os': os_name,
        'device_type': device_type
    }