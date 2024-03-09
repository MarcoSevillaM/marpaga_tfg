#!/bin/bash

# Se va a gestionar un script para que cuando un usuario levante una maquina SOLO él tenga acceso a traves de la VPN
# Por ello se configurarán relgas iptables para que el usuario A pueda tener acceso a la maquina que ha levantado b.
# Los parámetros que este script va a recibir son:
# - IP del usuario que ha levantado la maquina
# - IP de la maquina que ha levantado el usuario
# - Si lo que se va a hacer es añadir o eliminar reglas:
#	- add: Será cuando el usuario levante la maquina para permitirle el acceso, para añadir la regla hacen falta la ip del usuario y la ip de la maquina
#	- del: Será cuando el usuario apague la maquina para eliminar la regla, ya que la maquina estará apagada, para eliminar la regla solo hace falta la ip del usuario
# Uso: ./iptables.sh <add/del> <IP_usuario> <IP_maquina>

# Se va a comprobar que el usuario que ejecuta el script es root (como el script se ejecutará desde el servidor, el usuario será )
function isRoot() {
	if [ "$EUID" -ne 0 ]; then
		return 1
	fi
}

function deleteRule(){
	# Se va a comprobar que el usuario que ejecuta el script es root
	if ! isRoot; then
		echo "El usuario no es root"
		exit 1
	fi

	# Se va a comprobar que el usuario ha introducido los parametros necesarios
	if [ $# -ne 2 ]; then
		echo "El numero de parametros es incorrecto"
		exit 1
	fi

	# Se va a comprobar que el usuario ha introducido el parametro correcto
	if [ $1 != "del" ]; then
		echo "El parametro introducido no es correcto"
		exit 1
	fi

	# Se va a comprobar que la IP correcta es
	if ! [[ $2 =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
		echo "La IP introducida no es correcta"
		exit 1
	fi
	IP_MAQUINA=$2
	# Se va a comprobar que haya reglas y mientras haya ir eliminando las reglas
	# while [ $(iptables -L -n | grep $2 | wc -l) -ne 0 ]; do
	# 	# Se va a eliminar la regla
	# 	obtenerLinea $IP_MAQUINA #Esta función obtiene la linea en la que se encuentra la regla para poder eliminarla
	# 	#iptables -D FORWARD $LINE
	# done
	iptables-save | grep -v "$IP_MAQUINA" | sudo iptables-restore

}

#Esta función se ejecutará cuando se levante una maquina para prohibir el acceso a todos los usuarios menos al que la ha levantado
function addRule(){
	# Se va a comprobar que el usuario que ejecuta el script es root
	if ! isRoot; then
		echo "El usuario no es root"
		exit 1
	fi

	# Se va a comprobar que el usuario ha introducido los parametros necesarios
	if [ $# -ne 3 ]; then
		echo "El numero de parametros es incorrecto"
		exit 1
	fi
	# Se va a comprobar que el usuario ha introducido el parametro correcto
	if [ $1 != "add" ]; then
		echo "El parametro introducido no es correcto"
		exit 1
	fi

	# Con el nombre del usuario obtener la ip asociada en la VPN desde el fichero /etc/openvpn/ipp.txt
	# Se va a comprobar que el usuario existe, la estructura del fichero es: marco,10.8.0.2,fd42:42:42:42::2
	# APUNTE usar: /var/log/openvpn/status.log mejor que ipp.txt
	if [ $(grep -c $2 /etc/openvpn/ipp.txt) -eq 0 ]; then
		echo "El usuario no existe"
		exit 1
	fi
	# Se va a obtener la IP del usuario
	IP_USUARIO=$(grep $2 /etc/openvpn/ipp.txt | awk -F',' '{print $2}')

	# Se va a comprobar que la IP del usuario es correcta 
	if ! [[ $IP_USUARIO =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
		echo "La IP<usuario> introducida no es correcta"
		exit 1
	fi
	# Se va a comprobar que la IP de la maquina es correcta
	if ! [[ $3 =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
		echo "La IP<maquina> introducida no es correcta"
		exit 1
	fi
	# Se va a comprobar que la regla no existe
	if [ $(iptables -L -n | grep $3 | wc -l) -ne 0 ]; then
		echo "La regla ya existe"
		exit 1
	fi
	IP_MAQUINA=$3
	# Se va a añadir la regla
	#Ej: iptables -A 23 FORWARD -s 10.8.0.3 -d 172.18.0.4 -j ACCEPT
	iptables -A FORWARD -s $IP_USUARIO -d $IP_MAQUINA -j ACCEPT
	iptables -A FORWARD -s 10.8.0.0/24 -d $IP_MAQUINA -j DROP

}

function obtenerLinea(){
	#Se va a obtener la linea en la que se encuentra la regla
	#Ej: iptables -L -n | grep
	LINE=$(($(iptables -L FORWARD | grep -n -m 1 172.29.0.4 | awk -F':' '{print $1}') - 2))
	#Le resto 2
	
}

#Control de parametros
if [ $# -eq 3 ]; then
	addRule $1 $2 $3 
	exit 0
elif [ $# -eq 2 ]; then
	deleteRule $1 $2
	exit 0
else
	echo "Uso: ./iptables.sh <add> <nombre_usuario> <IP_maquina>"
	echo "Uso: ./iptables.sh <del> <IP_maquina>"

	echo "El numero de parametros es incorrecto"
	exit 0
fi