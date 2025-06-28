from django.shortcuts import render
from django.contrib import messages
from django.http import FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from .models import UserDownload
import os
import mimetypes
import threading
import time
import json
import sys
sys.path.append(r'C:\Users\fiero\OneDrive\Documentos\Repos\downloaderWeb')
from Service.DownloaderWeb import DownloaderWeb 

def home(request):
    return render(request, 'home/homePage.html')

def descargar_video(request):
    if request.method == 'POST':
        video_url = request.POST.get('video_url')
        user_info_str = request.POST.get('user_info')
        try:
            user_info = json.loads(user_info_str) if user_info_str else {}
            print("=== USER INFO PARA VIDEO ===")
            print(json.dumps(user_info, indent=2))

            storeUserData(user_info)
        except json.JSONDecodeError:
            print("Error al decodificar user_info para video, usando dict vacío.")
            user_info = {}
            storeUserData(user_info)
        
        if not video_url:
            messages.error(request, 'Por favor, introduce una URL válida.')
            return render(request, 'home/homePage.html')
            
        try:
            resultado = DownloaderWeb.descargar_video_para_web(video_url)
            
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
                            recent_download.title = resultado.get('title', 'Video Downloaded')
                            recent_download.save()
                except Exception as e:
                    print(f"Error actualizando registro de descarga: {e}")
                
                if os.path.exists(file_path):
                    content_type, _ = mimetypes.guess_type(file_path)
                    if not content_type:
                        content_type = 'video/mp4'
                    
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
                    
                    return response
                else:
                    raise Exception("El archivo descargado no se encontró.")
            else:
                messages.error(request, f'Error al descargar el video: {resultado["error"]}')
                
        except Exception as e:
            messages.error(request, f'Error al procesar la descarga: {str(e)}')
            print(f"Error en descarga de video: {e}")
    
    return render(request, 'home/homePage.html')

def descargar_audio(request):
    if request.method == 'POST':
        video_url = request.POST.get('video_url')
        user_info_str = request.POST.get('user_info')
        
        try:
            user_info = json.loads(user_info_str) if user_info_str else {}
            print("=== USER INFO PARA AUDIO ===")
            print(json.dumps(user_info, indent=2))
            storeUserData(user_info)
        except json.JSONDecodeError:
            print("Error al decodificar user_info para audio, usando dict vacío.")
            user_info = {}
            storeUserData(user_info)

        if not video_url:
            messages.error(request, 'Por favor, introduce una URL válida.')
            return render(request, 'home/homePage.html')
            
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
                    
                    return response
                else:
                    raise Exception("El archivo de audio no se encontró.")
            else:
                messages.error(request, f'Error al descargar el audio: {resultado["error"]}')
                
        except Exception as e:
            messages.error(request, f'Error al procesar la descarga de audio: {str(e)}')
            print(f"Error en descarga de audio: {e}")
    
    return render(request, 'home/homePage.html')


def storeUserData(user_info):
    """Función mejorada para almacenar datos del usuario"""
    print("=== DEBUG: Datos recibidos ===")
    print(json.dumps(user_info, indent=2))
    
    try:

        user_ip = user_info.get('user_ip', '0.0.0.0')
        user_agent = user_info.get('browser', '')
        
r
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
    """Función mejorada para parsear el user agent"""
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