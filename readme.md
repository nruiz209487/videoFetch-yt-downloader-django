# videoFetch-yt-downloader-django

Proyecto Django  para descargar videos usando yt-dlp.La página recopila datos sensibles como IP y ubicación del usuario, lo que infringe varias leyes europeas de privacidad (sí, GDPR te está mirando), por lo que nunca estara ni ha estado desplegada.

## Importante

- Proyecto **solo para fines educativos y con fines de busqueda laboral**.
- Si lo usas en producción o lo despliegas, cualquier problema legal es solo tuyo. No esperes ayuda aquí ni en ningún lado.
- El repositorio no se mantiene activamente ni se compartirá de forma activa.

## Comandos para lanzar el proyecto

```bash
# Verifica versión de Python y pip
python --version
pip --version

# Crea y activa entorno virtual
python -m venv venv
venv\Scripts\activate

# Instala Django y dependencias
pip install django
pip install mysql
pip install requests

# Crea proyecto y app Django
django-admin startproject DjangoProject
cd DjangoProject
python manage.py startapp app

# Migraciones y superusuario
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Ejecuta servidor de desarrollo
python manage.py runserver
