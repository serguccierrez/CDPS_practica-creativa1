#!/usr/bin/env python

import logging, sys, json
from lib_VMNET import VM, Red
from subprocess import call
from sys import argv
from sys import exit

#---------------------------------------------------------[VARIABLES GLOBALES]--------------------------------------------------------------

# Lista inicial de máquinas virtuales a la que se añadirán el número de servidores a crear y lista de redes a definir
vmNames = [ "c1","lb"]
redNames = [ "LAN1","LAN2"]

# Lista para almacenar las configuraciones
ifs = []  

# Configuraciones de red para cada máquina
configs = {
    "c1": {"addr": "10.1.1.2", "mask": "255.255.255.0", "gateway": "10.1.1.1"},
    "Host": {"addr": "10.1.1.3", "mask": "255.255.255.0", "gateway": "10.1.1.1"},
    "lb0": {"addr": "10.1.1.1", "mask": "255.255.255.0"},
    "lb1": {"addr": "10.1.2.1", "mask": "255.255.255.0"},
    "s1": {"addr": "10.1.2.11", "mask": "255.255.255.0", "gateway": "10.1.2.1"},
    "s2": {"addr": "10.1.2.12", "mask": "255.255.255.0", "gateway": "10.1.2.1"},
    "s3": {"addr": "10.1.2.13", "mask": "255.255.255.0", "gateway": "10.1.2.1"},
    "s4": {"addr": "10.1.2.14", "mask": "255.255.255.0", "gateway": "10.1.2.1"},
    "s5": {"addr": "10.1.2.15", "mask": "255.255.255.0", "gateway": "10.1.2.1"}, 
    }

# Crear las configuraciones y añadirlas a la lista ifs
for name, config in configs.items():
    ifs.append((name, config))

# Variable para controlar el modo debug
isDebug = False


#---------------------------------------------------------[JSON]----------------------------------------------------------------
def read_json():

    global isDebug

    # Ruta del archivo de configuración
    config_file = 'manage-p2.json'

    # Leer el archivo JSON
    with open(config_file, 'r') as file:
        config = json.load(file)

    # Extraer el número de servidores
    num_servers = config.get("number_of_servers")

    # Validar el número de servidores que además no puede ser letras
    if not isinstance(num_servers, int) or num_servers < 1 or num_servers > 5:
        print("ERROR: El número de servidores debe ser un entero entre 1 y 5")
        exit(1)

    # COmprueba si el modo debug esta activado
    isDebug = config.get("debug")

    if isDebug:
        print(f"El modo depuración está activado")
    else:
        print(f"El modo depuración no está activado")

    # Imprimir el número de servidores si es válido
    print(f"Se configuraron {num_servers} servidores web para arrancar")
    
    for i in range(num_servers):
        vmNames.append(f"s{i + 1}")


#---------------------------------------------------------[LOG]----------------------------------------------------------------
def init_log():
    # Creacion y configuracion del logger

    logging.basicConfig(level=logging.DEBUG if isDebug else logging.INFO)

    log = logging.getLogger('auto_p2')
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)
    log.addHandler(ch)
    log.propagate = False


#---------------------------------------------------------[CREATE_AUX]----------------------------------------------------------------
def host_network():
    # Levantar la interfaz LAN1
    call("sudo ifconfig LAN1 up", shell=True)

    # Asignar la dirección IP y máscara de red a LAN1
    call("sudo ifconfig LAN1 10.1.1.3/24", shell=True)

    # Agregar una ruta estática
    call("sudo ip route add 10.1.0.0/16 via 10.1.1.1", shell=True)


#---------------------------------------------------------[CREATE]----------------------------------------------------------------
def create(): 

    # Comando necesario para arrancar VM KVM y switches OVS
    call(["/lab/cnvr/bin/prepare-vnx-debian"], shell=True)

    # Crear los bridges de tipo ovs correspondientes a las dos redes virtuales
    for red in redNames:
        red=Red(red)
        red.create_network()
        

    for numerodemv in vmNames:
        # Creamos el objeto correspondiente a cada Maquina Virtual
        Vm=VM(numerodemv)
        Vm.crear_y_cargar_archivos()
        

        #Buscamos la etiqueta name imprimimos su valor y luego lo cambiamos por el nombre correspondeinte de cada VM
        Vm.change_name()
        
        
        #Obtenemos el valor del campo 'file' de la etiqueta 'source' de 'disk y lo cambiamos por la ruta del fichero qcow2 de la VM 
        Vm.set_route()
        
        
        # Incluimos en la secion interface los bridges basados en la solucion openswicth 
        Vm.add_virtualport()
        
        
        # Cambiamos el bridge de la interfaz de red de la VM
        Vm.change_bridge()
        

        # Salva los archivos xml modificados para cada maquina 
        Vm.save_xml()
        

        # Define las maquinas a partir de los archivos xml
        Vm.define_vm()
        

        # Cambiamos el nombre de host de las VM y asignamos el porpio de cada una
        Vm.change_hostName()
        

        print("Creando interfaces")
        Vm.create_interfaces_file(ifs)

    # Configuramos la red del host para que haya comunicación con el resto de máquinas
    host_network()


#---------------------------------------------------------[START SERVICES]----------------------------------------------------------------



#---------------------------------------------------------[START]----------------------------------------------------------------
def start(orden2):
    if orden2:
        vm = VM(orden2)
        vm.start()
        
    else:
        for vm in vmNames:
            vm = VM(vm)
            vm.start()
            
    

#---------------------------------------------------------[STOP]----------------------------------------------------------------
def stop(orden2):
    if orden2:
        vm = VM(orden2)
        vm.stop()

    else:
        for vm in vmNames:
            vm = VM(vm)
            vm.stop()
            

#---------------------------------------------------------[DESTROY]----------------------------------------------------------------
def destroy():
    for vm in vmNames:
        vm = VM(vm)
        vm.destroy()
        
    for red in redNames:
        red = Red(red)
        red.destroy_network()
        
    
#-------------------------------------------------------------[DETECCION DE COMANDOS]-----------------------------------------------------

# Tabla con las posibles órdenes permitidas
table = (
    "+----------+--------------------------------------------------------------+\n"
    "| Orden    | Descripción                                                  |\n"
    "+----------+--------------------------------------------------------------+\n"
    "|  create  | Inicializa las máquinas virtuales y crea el escenario.       |\n"
    "|  start   | Arranca las máquinas virtuales y muestra su consola. Si no   |\n"
    "|          | se especifica un nombre, se ejecuta para todas las VM.       |\n"
    "|  stop    | Detiene las máquinas virtuales sin liberar los recursos. Si  |\n"
    "|          | no se especifica un nombre, se ejecuta para todas las VM.    |\n"
    "| destroy  | Libera el escenario y elimina los ficheros creados.          |\n"
    "| machines | Te enseña el estado de todas las máquinas virtuales.         |\n"
    "|  stats   | Muestra estadísticas detalladas de las VM como CPU y memoria |\n"
    "|  info    | Para ver información detallada de las máquinas.              |\n"
    "+---------+-------------------------------------------------------------+"
)

# Validamos el número de argumentos para que sea el correcto
if len(argv) == 2:

    # Main
    read_json()
    init_log()

    # Guardamos la orden introducida en una variable
    orden = argv[1]

    # Mostramos ayuda si es solicitado
    if orden == "-help":
        print(table)

    # Ejecutamos la orden introducida si es válida
    elif orden == "create":
        print("Creando el entorno...")
        create()
        
    elif orden == "start":
        print("Iniciando el entorno...")
        start("")
            
    elif orden == "stop":
        print("Deteniendo el entorno...")
        stop("")
            
    elif orden == "destroy":
        print("Destruyendo el entorno...")
        destroy()

    elif orden == "machines":
        #log.debug("Monitorizacion de TODAS las máquinas virtuales")
        call(["xterm -title MACHINES -e watch sudo virsh list --all &"] , shell=True)


    elif orden == "stats":
        for vm in vmNames:
            call([f"xterm -title STATS-{vm} -e watch sudo virsh domstats {vm} &"], shell=True) 

    elif orden == "info":
        for vm in vmNames:
            call([f"xterm -title INFO-{vm} -e watch sudo virsh dominfo {vm} &"], shell=True)  
        
    else:
        print(f"Error: '{orden}' no es una orden válida. Escribe '-help' para más información.")

elif len(argv) == 3:
    orden = argv[1]
    orden2 = argv[2]
    if orden == "start":
        print("Iniciando el entorno...")
        start(orden2)
            
    elif orden == "stop":
        print("Deteniendo el entorno...")
        stop(orden2)

else:
    print("Error: número incorrecto de parámetros. Escribe '-help' para más información.")
    exit(1)