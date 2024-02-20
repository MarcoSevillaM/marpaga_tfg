import subprocess
import re
import sys

def is_root():
    return subprocess.run(["id", "-u"], capture_output=True, text=True).stdout.strip() == "0"

def delete_rule():
    # Check if the user running the script is root
    if not is_root():
        print("El usuario no es root")
        sys.exit(1)

    # Check if the user has provided the necessary parameters
    if len(sys.argv) != 3:
        print("El numero de parametros es incorrecto")
        sys.exit(1)

    # Check if the user has provided the correct parameter
    if sys.argv[1] != "del":
        print("El parametro introducido no es correcto")
        sys.exit(1)

    # Check if the IP address is correct
    if not re.match(r'^\d+\.\d+\.\d+\.\d+$', sys.argv[2]):
        print("La IP introducida no es correcta")
        sys.exit(1)

    IP_MAQUINA = sys.argv[2]
    subprocess.run(["iptables-save"], capture_output=True, text=True)
    subprocess.run(["grep", "-v", IP_MAQUINA], input="iptables-restore", capture_output=True, text=True, check=True)

def add_rule():
    # Check if the user running the script is root
    if not is_root():
        print("El usuario no es root")
        sys.exit(1)

    # Check if the user has provided the necessary parameters
    if len(sys.argv) != 4:
        print("El numero de parametros es incorrecto")
        sys.exit(1)

    # Check if the user has provided the correct parameter
    if sys.argv[1] != "add":
        print("El parametro introducido no es correcto")
        sys.exit(1)

    # Check if the user IP address is correct
    if not re.match(r'^\d+\.\d+\.\d+\.\d+$', sys.argv[2]):
        print("La IP<usuario> introducida no es correcta")
        sys.exit(1)

    # Check if the machine IP address is correct
    if not re.match(r'^\d+\.\d+\.\d+\.\d+$', sys.argv[3]):
        print("La IP<maquina> introducida no es correcta")
        sys.exit(1)

    # Check if the rule already exists
    if subprocess.run(["iptables", "-L", "-n"], capture_output=True, text=True).stdout.count(sys.argv[3]) != 0:
        print("La regla ya existe")
        sys.exit(1)

    IP_USUARIO = sys.argv[2]
    IP_MAQUINA = sys.argv[3]
    subprocess.run(["iptables", "-A", "FORWARD", "-s", IP_USUARIO, "-d", IP_MAQUINA, "-j", "ACCEPT"])
    subprocess.run(["iptables", "-A", "FORWARD", "-s", "10.8.0.0/24", "-d", IP_MAQUINA, "-j", "DROP"])

# Control de parametros
if len(sys.argv) == 4:
    add_rule()
    sys.exit(0)
elif len(sys.argv) == 3:
    delete_rule()
    sys.exit(0)
else:
    print("El numero de parametros es incorrecto")
    sys.exit(0)
