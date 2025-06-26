from django.shortcuts import render
from django.contrib import messages
from django.http import FileResponse
from .models import UserDownload
import os
import mimetypes
import threading
import time

import sys
sys.path.append(r'C:\Users\fiero\OneDrive\Documentos\Repos\downloaderWeb')
from Service.DownloaderWeb import DownloaderWeb 

def home(request):
    return render(request, 'home/homePage.html')

def descargar_video(request):
    if request.method == 'POST':
        video_url = request.POST.get('video_url')
        
        if not video_url:
            messages.error(request, 'Por favor, introduce una URL válida.')
            return render(request, 'home/homePage.html', {"elements": UserDownload.objects.all()})
        
        try:
            resultado = DownloaderWeb.descargar_video_para_web(video_url)
            
            if resultado['success']:
                file_path = resultado['file_path']
                filename = resultado['filename']
                temp_dir = resultado['temp_dir']
                
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
    
    return render(request, 'home/homePage.html')

def descargar_audio(request):
    if request.method == 'POST':
        video_url = request.POST.get('video_url')
        
        if not video_url:
            messages.error(request, 'Por favor, introduce una URL válida.')
            return render(request, 'home/homePage.html', {"elements": UserDownload.objects.all()})
        
        try:
            resultado = DownloaderWeb.descargar_audio_para_web(video_url)
            
            if resultado['success']:
                file_path = resultado['file_path']
                filename = resultado['filename']
                temp_dir = resultado['temp_dir']
                
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
    
    return render(request, 'home/homePage.html')