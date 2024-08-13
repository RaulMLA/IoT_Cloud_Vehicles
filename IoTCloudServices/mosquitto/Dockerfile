# Crear la imagen del contenedor a partir de la correspondiente a debian:buster.
FROM debian:buster

# Actualizar el sistema e instalar mosquitto y mosquitto-clients.
RUN apt update && apt upgrade -y
RUN apt install -y mosquitto mosquitto-clients -y

# Crear el archivo passwd para mosquitto.
RUN touch /etc/mosquitto/passwd

# Añadir un usuario y contraseña al archivo passwd.
RUN mosquitto_passwd -b /etc/mosquitto/passwd admin javascript

# Lanzar mosquitto.
CMD ["/usr/sbin/mosquitto", "-c", "/etc/mosquitto/mosquitto.conf"]
