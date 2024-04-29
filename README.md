# facturacion
Proyecto OpenAPI

# Instrucciones de montaje
**Una vez instalados los requerimientos:** \
1- Crear un entorno virtual de Python \
**python -m venv “nombre del entorno virtual”** \

Activar entorno virtual \
**source “nombre del entorno virtual”/bin/activate** \

Instalar los requerimientos \
Correr el siguiente archivo con el siguiente comando \
**pip install -r requirements.txt** \

Crear una base de datos con el mismo nombre de la configuración por defecto llamado “facturación” \

En “settings.py” establecer el usuario y contraseña de su respectivo gestor de base de datos. \

Ejecutar los comando para migrar las tablas \
**python manage.py makemigrations** \
**python manage.py migrate** \

Crear un super usuario \
**python manage.py createsuperuser** \

Correr el servidor \
**python manage.py runserver** (por defecto corre en localhost:8000)