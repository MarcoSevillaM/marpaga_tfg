server {
	listen 80;
	server_name marpaga.hopto.org;

		location = /favicon.ico { access_log off; log_not_found off; }

	location /static/ {
		root /var/www/html/marpaga_tfg; # Cambiar la ruta a la correspondiente
	}
		location / {

		include proxy_params;
		proxy_pass http://127.0.0.1:8000;
	}
}