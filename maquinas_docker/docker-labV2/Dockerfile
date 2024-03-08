FROM httpd:2.4.50
COPY ./httpd.conf /usr/local/apache2/conf/httpd.conf
COPY ./comand.sh /var/www/html/comand.sh
COPY ./flag.txt /root/flag.txt
RUN chmod +sx /var/www/html/comand.sh
