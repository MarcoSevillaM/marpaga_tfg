#!/bin/bash
# Script que pasa el proyecto a /var/www/html/ y establece el servicio con gunicorn y nginx

RUTA="/home/marco/Escritorio/TFG/marpaga_tfg"

function addRule(){
    # Se copia todo el proyecto a /var/www/html/ y quedará la ruta /var/www/html/marpaga_tfg
    mkdir -p /var/www/html/marpaga_tfg && cp -r $RUTA /var/www/html/ && chown -R www-data:www-data /var/www/html/marpaga_tfg && echo "[+] Proyecto copiado"

    # Creo un entorno virtual, lo activo e instalo las dependencias
    cd /var/www/html/ && python3 -m venv env && chown -R www-data:www-data /var/www/html/env && source env/bin/activate && cd marpaga_tfg && pip install -r requirements.txt && pip install gunicorn && pip install django_cron && python3 /var/www/html/marpaga_tfg/manage.py makemigrations && python3 /var/www/html/marpaga_tfg/manage.py migrate && echo "[+] Entorno virtual creado e instaladas las dependencias"
    
    # Cambio la variable DEBUG a False
    sed -i 's/DEBUG = True/DEBUG = False/' /var/www/html/marpaga_tfg/marpaga/settings.py && echo "[+] DEBUG cambiado a False"
    # Decomento las lineas:
        #SECURE_SSL_REDIRECT = True
        #SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    sed -i 's/#SECURE_SSL_REDIRECT = True/SECURE_SSL_REDIRECT = True/' /var/www/html/marpaga_tfg/marpaga/settings.py && echo "[+] SECURE_SSL_REDIRECT descomentado"
    sed -i 's/#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')/SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')/' /var/www/html/marpaga_tfg/marpaga/settings.py
    # Hago las migraciones
    source /var/www/html/env/bin/activate && python3 /var/www/html/marpaga_tfg/manage.py makemigrations && python3 /var/www/html/marpaga_tfg/manage.py migrate && echo "[+] Migraciones hechas"
    
    #Ajusto los permisos
    chmod 777 /var/www/html/marpaga_tfg && chmod 664 /var/www/html/marpaga_tfg/db.sqlite3 && chown www-data:marco /var/www/html/marpaga_tfg/db.sqlite3 && echo "[+] Permisos ajustados"
    # El fichero marpaga_gunicorn.service se copia a /etc/systemd/system/ y se activa
    cp /var/www/html/marpaga_tfg/SERVICIO_GUN/marpaga_gunicorn.service /etc/systemd/system/ && systemctl daemon-reload && echo "[+] Fichero de servicio copiado y activado"
    
    systemctl start marpaga_gunicorn.service && systemctl enable marpaga_gunicorn.service


    # Instalamos nginx y copiamos el fichero de configuración
    apt-get install nginx -y
    
    # Doy permisos a la carpeta /var/www/html/marpaga_tfg/media
    chown -R www-data:marco /var/www/html/marpaga_tfg/media && chmod 775 -R /var/www/html/marpaga_tfg/media
    # Establecemos el cerfiticado SSL
    #apt-get install certbot python3-certbot-nginx -y 
    #certbot certonly --nginx -d marpaga.hopto.org
    cp /var/www/html/marpaga_tfg/SERVICIO_GUN/marpaga_nginx /etc/nginx/sites-available/ && ln -s /etc/nginx/sites-available/marpaga_nginx /etc/nginx/sites-enabled

    # Eliminamos el fichero por defecto de nginx
    rm /etc/nginx/sites-enabled/default 2>/dev/null
    systemctl restart nginx
    echo "[+] Servicio añadido"
}

#El script si se ejecuta con el parámetro add se crea todo y si se ejecuta con el parámetro rm se elimina todo 

if [ "$1" == "add" ]
then
    # Se ejecuta como root
    if [ "$EUID" -ne 0 ]
    then echo "Por favor, ejecutar como root"
    exit
    fi

    echo "[+] Añadiendo el servicio"
    addRule
elif [ "$1" == "rm" ]
then
    # Se ejecuta como root
    if [ "$EUID" -ne 0 ]
    then echo "Por favor, ejecutar como root"
    exit
    fi

    echo "[+] Eliminando el servicio"
    systemctl disable marpaga_gunicorn.service && systemctl stop marpaga_gunicorn.service && rm /etc/systemd/system/marpaga_gunicorn.service
    rm /etc/nginx/sites-enabled/marpaga_nginx && rm /etc/nginx/sites-available/marpaga_nginx && systemctl restart nginx && apt-get remove nginx -y
    rm -r /var/www/html/marpaga_tfg && rm -r /var/www/html/env
    exit
elif [ "$1" == "stop" ]
then
    # Se ejecuta como root
    if [ "$EUID" -ne 0 ]
    then echo "Por favor, ejecutar como root"
    exit
    fi

    echo "[+] Parando el servicio"
    systemctl disable marpaga_gunicorn.service && systemctl stop marpaga_gunicorn.service
    systemctl stop nginx && systemctl disable nginx
    exit
elif [ "$1" == "start" ]
then
    # Se ejecuta como root
    if [ "$EUID" -ne 0 ]
    then echo "Por favor, ejecutar como root"
    exit
    fi

    echo "[+] Arrancando el servicio"
    systemctl start marpaga_gunicorn.service && systemctl enable marpaga_gunicorn.service
    systemctl start nginx && systemctl enable nginx
    exit
elif [ "$1" == "restart" ]
then
    # Se ejecuta como root
    if [ "$EUID" -ne 0 ]
    then echo "Por favor, ejecutar como root"
    exit
    fi

    echo "[+] Reiniciando el servicio"
    systemctl restart marpaga_gunicorn.service && systemctl restart nginx
    exit
elif [ "$1" == "status" ]
then
    echo "Estado del servicio"
    systemctl status marpaga_gunicorn.service && systemctl status nginx || echo "No hay servicio"
    exit
elif [ "$1" == "update" ]
then
    echo "[+] Actualizando los ficheros"
    cp -r $RUTA /var/www/html/marpaga_tfg && chown -R www-data:www-data /var/www/html/marpaga_tfg && echo "[+] Proyecto copiado"
    exit
else
    echo "[!] Parámetro incorrecto"
    exit
fi