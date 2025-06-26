## Comandos para lanzar el proyecto
- Este proyecto esta bajo construcion es basicamente uan pagina que descarga videos usando yt.dpl.
- El proyecto es fines educativos si alguien coge el codigo y lo despliega no me hago responsable el repositorio tampoco sera compartido de manera activa.
Sigue estos pasos para configurar y ejecutar un proyecto Django desde cero, incluyendo la instalación de dependencias y la creación de la base de datos.

```bash
# Verifica la versión de Python y pip
python --version
pip --version

# Crea y activa un entorno virtual
python -m venv venv
venv\Scripts\activate

# Instala Django y otras dependencias necesarias
pip install django
pip install mysql
pip install requests

# Crea un nuevo proyecto Django y una aplicación
django-admin startproject DjangoProject
cd DjangoProject
python manage.py startapp app

# Realiza las migraciones iniciales y crea un superusuario
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Opcional: abre el shell de Django
python manage.py shell

# Inicia el servidor de desarrollo
python manage.py runserver
```
