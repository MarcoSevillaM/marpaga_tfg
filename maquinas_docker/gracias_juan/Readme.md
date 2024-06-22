# Gracias Juan
## ENUNCIADO
Juan está de vacaciones y tenemos que hacer uso de su user. No sabemos si se ha dejado algo por aquí

## Pistas
### Pista 1
Juan solía dejar cosas importantes en Notas

## Pista 2
Es probable que haya algo interesante en alguna carpeta temporal

## Pista 3
A juan le encataba hacer scripts automatizados, y sin mirar cuidar permisos ni na'

## FLAG
flag{c29120a1ce92c3b3ed2ff82b72945085}

## Solucion
El usuario juanthanks está deshabilitado, pero existe un binario en /tmp llamado "activation_thanks_juan". Este fichero tiene la linea "#usermod -U juanthanks". Al tener permisos de escritura, podemos descomentarla. Este script está ejecutandose constantemente mediante un cronjob,  en el momento que se ejecute podremos loguearnos como juanthanks con las credenciales que tenemos en "Notas.txt" que veremos nada más conectarnos por ssh
Al ser juanthanks, podremos ver un script en monitoring que simplemente va recibiendo la hora. Este script tambien se ejecuta como root y es un cronjob, por lo que podremos insertar un comando como "cat /root/flag.txt > /home/juanthanks/flag.txt" y obtener la flag.

