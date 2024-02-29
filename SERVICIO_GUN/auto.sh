#!/bin/bash
# Script que pasa el proyecto a /var/www/html/ y establece el servicio con gunicorn y nginx

# Se ejecuta como root
if [ "$EUID" -ne 0 ]
  then echo "Por favor, ejecutar como root"
  exit
fi

# Se copia todo el proyecto a /var/www/html/
cp -r /home/marco/Escritorio/TFG/marpaga_tfg /var/www/html/ && chown -R www-data:www-data /var/www/html/marpaga_tfg

# Creo un entorno virtual, lo activo e instalo las dependencias
cd /var/www/html/ && python3 -m venv env && source env/bin/activate && cd marpaga_tfg && pip install -r requirements.txt && pip install gunicorn

# El fichero marpaga_gunicorn.service se copia a /etc/systemd/system/ y se activa
cp /var/www/html/marpaga_tfg/SERVICIO_GUN/marpaga_gunicorn.service /etc/systemd/system/ && systemctl daemon-reload
systemctl start marpaga_gunicorn.service && systemctl enable marpaga_gunicorn.service

# Instalamos nginx y copiamos el fichero de configuración
apt-get install nginx -y
cp /var/www/html/marpaga_tfg/SERVICIO_GUN/marpaga_nginx /etc/nginx/sites-available/ && ln -s /etc/nginx/sites-available/marpaga_nginx /etc/nginx/sites-enabled

# Eliminamos el fichero por defecto de nginx
rm /etc/nginx/sites-enabled/default && systemctl restart nginx