# Crear la imagen del contenedor a partir de la correspondiente a python:3.11.1
FROM python:3.11.1

# Copiar el código que está en la carpeta ./code a la carpeta /etc/usr/src/app
COPY ./code /etc/usr/src/app

# Establecer esta carpeta como directorio de trabajo.
WORKDIR /etc/usr/src/app

# Instalar los paquetes necesarios especificados en requirements.txt. Los paquetes necesarios son: requests y math, para ello ejecutar pip install <paquetes necesarios>
RUN pip install --no-cache-dir -r requirements.txt

# Ejecutar el código incluido en el fichero message_router.py
CMD ["python", "message_router.py"]
