# Usa la imagen base de Ubuntu
FROM ubuntu:latest

COPY entrypoint.sh /root/entrypoint.sh

RUN chmod +x /root/entrypoint.sh

# Evita preguntas durante la instalación de paquetes
ARG DEBIAN_FRONTEND=noninteractive

# Instalar cron, sudo y vim (para editar scripts si es necesario)
RUN apt-get update && apt-get install -y cron sudo vim openssh-server && \
    mkdir /var/run/sshd

RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config && \
    sed -i 's/#ChallengeResponseAuthentication no/ChallengeResponseAuthentication yes/' /etc/ssh/sshd_config


# Crear el usuario 'cyberloquete' y 'juanthanks'
RUN useradd -m cyberloquete && \
    echo "cyberloquete:cyberloquete" | chpasswd && \
    useradd -m -s /bin/bash juanthanks && \
    echo "juanthanks:snowflake" | chpasswd && \
    usermod -L juanthanks  # Desactivar juanthanks 

RUN echo 'cyberloquete ALL=(ALL) NOPASSWD: /usr/sbin/usermod -U juanthanks' >> /etc/sudoers


RUN echo "flag{c29120a1ce92c3b3ed2ff82b72945085}" > /root/flag.txt

# Crear el directorio .ssh para el usuario cyberloquete y configurar las claves autorizadas
RUN mkdir -p /home/cyberloquete/.ssh && \
    chown cyberloquete:cyberloquete /home/cyberloquete/.ssh && \
    chmod 700 /home/cyberloquete/.ssh

# Crear el script activation_thanks_juan
RUN echo '#!/bin/bash' > /tmp/activation_thanks_juan && \
    echo 'usermod -U juanthanks' >> /tmp/activation_thanks_juan && \
    echo '#Pa cuando vuelva el juan (Gracias)' >> /tmp/activation_thanks_juan && \
    echo '#Creo que en algunos users falla, hay que darle una vuelta al comando' >> /tmp/activation_thanks_juan && \
    chmod 750 /tmp/activation_thanks_juan && \
    chown cyberloquete /tmp/activation_thanks_juan

# Crear el directorio y script de monitoreo
RUN mkdir -p /home/juanthanks/monitoring && \
    echo '#!/bin/bash' > /home/juanthanks/monitoring/monitor_flag.sh && \
    echo 'echo "$(date) Monitoring in progress..."' >> /home/juanthanks/monitoring/monitor_flag.sh && \
    chmod 755 /home/juanthanks/monitoring/monitor_flag.sh && \
    chown juanthanks:juanthanks /home/juanthanks/monitoring/monitor_flag.sh

# Configurar el cron job para ejecutar como root
RUN echo '* * * * * root /home/juanthanks/monitoring/monitor_flag.sh' > /etc/crontab 


# Crear archivo de credenciales en el home de cyberloquete
RUN echo 'Si hay que hacer algo como Juan, recuerda que es juanthanks:b0c5516f28a7c36bd0233dfd6f3bab3c2a0c4010' > /home/cyberloquete/Nota.txt && \
    chmod 600 /home/cyberloquete/Nota.txt && \
    chown cyberloquete:cyberloquete /home/cyberloquete/Nota.txt

# Habilitar y arrancar el cron
RUN touch /var/log/cron.log && \
    cron

# Exponer el puerto SSH (opcional, si se desea acceder a través de SSH en lugar de ejecutar directamente el contenedor)
EXPOSE 22

# Comando para mantener el contenedor corriendo
ENTRYPOINT ["/root/entrypoint.sh"]

