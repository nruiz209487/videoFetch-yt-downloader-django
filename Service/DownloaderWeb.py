import yt_dlp
import os
import re
import tempfile
import shutil
from dotenv import load_dotenv

load_dotenv()

class DownloaderWeb:
    """Versión del descargador adaptada para Django - descarga y retorna el archivo el cambio esta en el uso de capetas temporales el vido se descarga en lcoal y se envia el archivo temporal"""
    
    FFMPEG_DOMINIOS = ["youtube.com", "youtu.be"]
    SIMPLE_DOMINIOS = ["tiktok.com", "instagram.com", "facebook.com"]

    @staticmethod
    def descargar_video_para_web(url):
        if DownloaderWeb.necesita_ffmpeg(url):
            return DownloaderWeb.descargar_video_con_ffmpeg_web(url)
        else:
            return DownloaderWeb.descargar_video_simple_web(url)

    @staticmethod
    def necesita_ffmpeg(url):
        return any(dominio in url for dominio in DownloaderWeb.FFMPEG_DOMINIOS)

    @staticmethod
    def descargar_video_simple_web(url, format='best'):
        temp_dir = tempfile.mkdtemp()
        outtmpl = os.path.join(temp_dir, '%(title)s.%(ext)s')
        
        try:
            opciones = {
                'format': format,
                'outtmpl': outtmpl,
                'quiet': True,
            }

            with yt_dlp.YoutubeDL(opciones) as ydl:
                info = ydl.extract_info(url, download=True)
                if info:
                    titulo_limpio = re.sub(r'[\\/*?:"<>|]', "", info.get('title', 'video'))
                    extension = info.get('ext', 'mp4')
                    nombre_archivo = f"{titulo_limpio}.{extension}"
                    
                    for archivo in os.listdir(temp_dir):
                        if archivo.endswith(('.' + extension, '.mp4', '.webm', '.mkv')):
                            ruta_archivo = os.path.join(temp_dir, archivo)
                            return {
                                'success': True,
                                'file_path': ruta_archivo,
                                'filename': nombre_archivo,
                                'title': info.get('title', 'video'),
                                'temp_dir': temp_dir
                            }
                    
            return {'success': False, 'error': 'No se encontró el archivo descargado'}

        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return {'success': False, 'error': str(e)}


    @staticmethod
    def descargar_video_con_ffmpeg_web(url):
        temp_dir = tempfile.mkdtemp()
        try:
            ffmpeg_path = os.getenv('FFMPEG_PATH')
            if not ffmpeg_path:
                raise Exception("FFmpeg no está configurado correctamente en el archivo .env")

            info_opciones = {
                'quiet': True,
                'ffmpeg_location': ffmpeg_path,
            }
            with yt_dlp.YoutubeDL(info_opciones) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("No se pudo obtener información del video")
                titulo_limpio = re.sub(r'[\\/*?:"<>|]', "", info.get('title', 'video'))
                extension = 'mp4'
                nombre_archivo = f"{titulo_limpio}.{extension}"

            outtmpl = os.path.join(temp_dir, f"{titulo_limpio}.%(ext)s")
            opciones = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': outtmpl,
                'quiet': True,
                'ffmpeg_location': ffmpeg_path,
                'merge_output_format': 'mp4',
                'noplaylist': True,
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            }

            with yt_dlp.YoutubeDL(opciones) as ydl:
                ydl.download([url])

            for archivo in os.listdir(temp_dir):
                if archivo.startswith(titulo_limpio) and archivo.endswith('.mp4'):
                    ruta_archivo = os.path.join(temp_dir, archivo)
                    return {
                        'success': True,
                        'file_path': ruta_archivo,
                        'filename': nombre_archivo,
                        'title': info.get('title', 'video'),
                        'temp_dir': temp_dir
                    }

            return {'success': False, 'error': 'No se encontró el archivo descargado'}

        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return {'success': False, 'error': str(e)}

    @staticmethod
    def descargar_audio_para_web(url, format='bestaudio'):
        temp_dir = tempfile.mkdtemp()
        outtmpl = os.path.join(temp_dir, '%(title)s.%(ext)s')
        
        try:
            ffmpeg_path = os.getenv('FFMPEG_PATH')
            if not ffmpeg_path:
                raise Exception("FFmpeg no está configurado correctamente en el archivo .env")

            opciones = {
                'format': format,
                'outtmpl': outtmpl,
                'quiet': True,
                'ffmpeg_location': ffmpeg_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
                'noplaylist': True,
            }

            with yt_dlp.YoutubeDL(opciones) as ydl:
                info = ydl.extract_info(url, download=True)
                if info:
                    titulo_limpio = re.sub(r'[\\/*?:"<>|]', "", info.get('title', 'audio'))
                    nombre_archivo = f"{titulo_limpio}.mp3"
                    
                    for archivo in os.listdir(temp_dir):
                        if archivo.endswith('.mp3'):
                            ruta_archivo = os.path.join(temp_dir, archivo)
                            return {
                                'success': True,
                                'file_path': ruta_archivo,
                                'filename': nombre_archivo,
                                'title': info.get('title', 'audio'),
                                'temp_dir': temp_dir
                            }
                    
            return {'success': False, 'error': 'No se encontró el archivo de audio descargado'}
            
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return {'success': False, 'error': str(e)}

    @staticmethod
    def limpiar_archivo_temporal(temp_dir):
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass