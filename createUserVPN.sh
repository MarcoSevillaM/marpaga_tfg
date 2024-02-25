#!/bin/bash

# Script que se ejecutará:
#   + Al crear un nuevo usuario en el sistema y colocará el fichero creado en la ruta: /home/marco/Escritorio/TFG/marpaga_tfg/media/vpns/
#   + Al eliminar un usuario del sistema y eliminará el fichero creado en la ruta: /home/marco/Escritorio/TFG/marpaga_tfg/media/vpns/

function newClient() {

    PASS=1
	CLIENTEXISTS=$(tail -n +2 /etc/openvpn/easy-rsa/pki/index.txt | grep -c -E "/CN=$CLIENT\$")
    CLIENTEXISTS=0
	if [[ $CLIENTEXISTS == '1' ]]; then
		echo ""
		echo "The specified client CN was already found in easy-rsa, please choose another name."
		exit
	else
		cd /etc/openvpn/easy-rsa/ || return
		case $PASS in
		1)
			./easyrsa --batch build-client-full "$CLIENT" nopass
			;;
		2)
			echo "⚠️ You will be asked for the client password below ⚠️"
			./easyrsa --batch build-client-full "$CLIENT"
			;;
		esac
	fi

	# Home directory of the user, where the client configuration will be written
	# if [ -e "/home/${CLIENT}" ]; then
	# 	# if $1 is a user name
	# 	homeDir="/home/${CLIENT}"
	# elif [ "${SUDO_USER}" ]; then
	# 	# if not, use SUDO_USER
	# 	if [ "${SUDO_USER}" == "root" ]; then
	# 		# If running sudo as root
	# 		homeDir="/root"
	# 	else
	# 		homeDir="/home/${SUDO_USER}"
	# 	fi
	# else
	# 	# if not SUDO_USER, use /root
	# 	homeDir="/root"
	# fi
    homeDir="/home/marco/Escritorio/TFG/marpaga_tfg/media/vpns"
	# Determine if we use tls-auth or tls-crypt
	if grep -qs "^tls-crypt" /etc/openvpn/server.conf; then
		TLS_SIG="1"
	elif grep -qs "^tls-auth" /etc/openvpn/server.conf; then #Se usa esto
		TLS_SIG="2"
	fi

	# Generates the custom client.ovpn
	#cp /etc/openvpn/client-template.txt "$homeDir/$CLIENT.ovpn"
	cp /etc/openvpn/client-template.txt "$homeDir/$CLIENT.ovpn"
	{
		echo "<ca>"
		cat "/etc/openvpn/easy-rsa/pki/ca.crt"
		echo "</ca>"

		echo "<cert>"
		awk '/BEGIN/,/END CERTIFICATE/' "/etc/openvpn/easy-rsa/pki/issued/$CLIENT.crt"
		echo "</cert>"

		echo "<key>"
		cat "/etc/openvpn/easy-rsa/pki/private/$CLIENT.key"
		echo "</key>"

		case $TLS_SIG in
		1)
			echo "<tls-crypt>"
			cat /etc/openvpn/tls-crypt.key
			echo "</tls-crypt>"
			;;
		2)
			echo "key-direction 1"
			echo "<tls-auth>"
			cat /etc/openvpn/tls-auth.key
			echo "</tls-auth>"
			;;
		esac
	} >> "$homeDir/$CLIENT.ovpn"

	echo ""
	echo "The configuration file has been written to $homeDir/$CLIENT.ovpn."
	echo "Download the .ovpn file and import it in your OpenVPN client."

	exit 0
}

function revokeClient() {
	NUMBEROFCLIENTS=$(tail -n +2 /etc/openvpn/easy-rsa/pki/index.txt | grep -c "^V")
	if [[ $NUMBEROFCLIENTS == '0' ]]; then
		exit 1
	fi

	# echo ""
	# echo "Select the existing client certificate you want to revoke"
	# tail -n +2 /etc/openvpn/easy-rsa/pki/index.txt | grep "^V" | cut -d '=' -f 2 | nl -s ') '
	# until [[ $CLIENTNUMBER -ge 1 && $CLIENTNUMBER -le $NUMBEROFCLIENTS ]]; do
	# 	if [[ $CLIENTNUMBER == '1' ]]; then
	# 		read -rp "Select one client [1]: " CLIENTNUMBER
	# 	else
	# 		read -rp "Select one client [1-$NUMBEROFCLIENTS]: " CLIENTNUMBER
	# 	fi
	# done
	# CLIENT=$(tail -n +2 /etc/openvpn/easy-rsa/pki/index.txt | grep "^V" | cut -d '=' -f 2 | sed -n "$CLIENTNUMBER"p)
	cd /etc/openvpn/easy-rsa/ || return
	./easyrsa --batch revoke "$CLIENT"
	EASYRSA_CRL_DAYS=3650 ./easyrsa gen-crl
	rm -f /etc/openvpn/crl.pem
	cp /etc/openvpn/easy-rsa/pki/crl.pem /etc/openvpn/crl.pem
	chmod 644 /etc/openvpn/crl.pem
	find /home/ -maxdepth 2 -name "$CLIENT.ovpn" -delete
	rm -f "/root/$CLIENT.ovpn"
    # Elimino el fichero .ovpn de la ruta /home/marco/Escritorio/TFG/marpaga_tfg/media/vpns/
    rm -f "/home/marco/Escritorio/TFG/marpaga_tfg/media/vpns/$CLIENT.ovpn"
    sed -i "/.*\/CN=$CLIENT/d" /etc/openvpn/easy-rsa/pki/index.txt
	sed -i "/^$CLIENT,.*/d" /etc/openvpn/ipp.txt
	cp /etc/openvpn/easy-rsa/pki/index.txt{,.bk}
}

# Controlo los parametros que se le pasan al script si es add o rm
# Uso: ./createUserVPN.sh add <nombreUsuario>

# Controlo que sean 2 parametros
if [ "$#" -ne 2 ]; then
    exit 1
fi
if [ "$1" == "add" ]; then
    CLIENT=$2
    newClient
elif [ "$1" == "del" ]; then
    CLIENT=$2
    revokeClient
else
    echo "Error en los parametros"
fi

