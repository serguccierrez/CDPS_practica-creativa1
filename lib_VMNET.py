import logging
import os
from subprocess import call
from lxml import etree

# Configuración del logger para Registramos eventos e información
log = logging.getLogger('manage-p2')

# Clase que representa una máquina virtual (VM)
class VM:

    def __init__(self, vmName):
        # Inicializa la VM con un nombre y configura sus archivos base
        self.vmName = vmName
        
    def crear_y_cargar_archivos(self):
        
        # Creamos los ficheros necesarios para la VM
        ruta_actual = os.path.dirname(os.path.abspath(__file__))  # Cargamos la ruta actual del script
        

        log.info(f'Creando archivos para la VM "{self.vmName}"...')
        call([f"qemu-img create -F qcow2 -f qcow2 -b {ruta_actual}/cdps-vm-base-pc1.qcow2 ./{self.vmName}.qcow2"], shell=True)
        call([f"cp {ruta_actual}/plantilla-vm-pc1.xml ./{self.vmName}.xml"], shell=True)
        log.debug(f'Archivos {self.vmName}.qcow2 y {self.vmName}.xml creados correctamente en la ruta: ' + ruta_actual)
        
        # Cargamos el archivo XML de configuración de la VM y obtenemos la raíz del documento XML (elemento <domain>)
        self.tree = etree.parse(f'{self.vmName}.xml')
        self.root = self.tree.getroot()
        log.debug(f'Archivo XML "{self.vmName}.xml" cargado y procesado correctamente: \n' + etree.tounicode(self.tree, pretty_print=True))

        # Inicializamos 'content' como una cadena vacía para almacenar el contenido del archivo de configuración de las interfaces de red
        self.content = ""

        log.info('Se han creado los archivos necesarios para la VM ' + self.vmName + ' correctamente \n')


    def change_name(self):

        log.info('Cambiando el nombre de la VM ' + self.vmName + '...')
        # Cambiamos el nombre de la VM en el archivo XML
        name = self.root.find("name")  # Buscar el nodo <name>
        log.debug('Este es el nombre viejo: ' + name.text)
        name.text = self.vmName       # Asignar el nuevo nombre
        log.debug('Este es el nombre nuevo: ' + name.text)
        log.info('Nombre cambiado correctamente a: ' + self.vmName + '\n')
        

    def set_route(self):

        log.info('Configurando la ruta del disco de la VM ' + self.vmName + '...')

        # Configuramos la ruta del disco de la VM
        ruta_actual = os.path.dirname(os.path.abspath(__file__))  # Cargamos la ruta actual del script
        ruta_padre = os.path.dirname(ruta_actual)                # Cargamos la ruta del directorio padre

        # Buscar el atributo "file" del elemento <source> en <disk>
        source_disk = self.root.find("./devices/disk/source")
        file = source_disk.get("file")
        log.debug("Esta es la ruta antigua: " + file)
        source_disk.set("file", f'{ruta_actual}/{self.vmName}.qcow2')  # Asignamos una nueva ruta
        log.debug("Esta es la ruta nueva: " + source_disk.get("file"))

        log.info('Se ha configurado la ruta del disco para la máquina virtual ' + self.vmName + '\n')

    def add_virtualport(self):

        log.info('Añadiendo un virtualport a la VM ' + self.vmName + '...')

        # Agregamos un virtualport con tipo "openvswitch" en la configuración de la VM
        interface = self.root.find("./devices/interface")  # Buscamos el nodo <interface>
        virtualport = etree.Element("virtualport")        # Creamos elemento <virtualport>
        virtualport.set("type", "openvswitch")            # Configuramos el atributo "type" como 
        interface.append(virtualport)                     # Añadimos el elemento <virtualport> a <interface>
        log.debug("Etiqueta <virtualport> añadida con éxito: " + virtualport.get("type"))
        log.info('Se ha añadido el virtualport para la máquina virtual ' + self.vmName + '\n')

    def change_bridge(self):

        log.info('Cambiando el bridge de la interfaz de red ' + self.vmName + '...')

        # Cambiamos el bridge de la interfaz de red
        source_interface = self.root.find("./devices/interface/source")  # Buscar <source> en <interface>
        file = source_interface.get("bridge") # Obtenemos el valor del atributo "bridge"   
        log.debug("Este es el bridge antiguo: " + file)

        # Configurar bridge según el nombre de la VM
        if self.vmName != "c1" and self.vmName != "lb":
            source_interface.set("bridge", "LAN2")
        elif self.vmName == "lb":
            source_interface.set("bridge", "LAN1")
        else:
            source_interface.set("bridge", "LAN1")

        # Si la VM es "lb", añadir una interfaz de red con bridge "LAN1" adicional a la configuración de la VM 
        if self.vmName == "lb":
            interface = self.root.find("./devices/interface")             # Buscamos el nodo <interface>
            new_interface = etree.fromstring(etree.tostring(interface))  # Creamos una copia del nodo
            new_interface.find("./source").set("bridge", "LAN2")         # Cambiamos el bridge de la copia
            devices = self.root.find("./devices")                        # Buscamos el nodo padre <devices> del que tiene que colgar la nueva interfaz
            devices.append(new_interface)                                # Añadimos la nueva interfaz
        log.debug("Este es el bridge nuevo: " + source_interface.get("bridge"))

       
        log.info('Se ha configurado el nuevo bridge para la máquina virtual ' + self.vmName + '\n')

    def save_xml(self):

        log.info('Guardando la configuración de la VM en el archivo XML ' + self.vmName + '...')

        # GUardamos los cambios en el archivo XML
        log.debug('Este es el resultado del xml completo' + etree.tounicode(self.tree, pretty_print=True))  
        self.tree.write(f'{self.vmName}.xml', pretty_print=True, xml_declaration=True, encoding='utf-8')
        log.debug(f"Los cambios han sido guardados en el archivo {self.vmName}.xml")

        log.info('Se ha guardado la configuración para la máquina virtual ' + self.vmName + '\n')

    def define_vm(self):
        # Definimos la máquina virtual a partir del archivo XML
        
        log.info('Definiendo la instancia para la VM ' + self.vmName + '...')

        call([f"sudo virsh define {self.vmName}.xml"], shell=True)

       
        log.info('Se ha definido la instancia para la maquina virtual ' + self.vmName + '\n')

    def change_hostName(self):

        log.info('Editando el archivo /etc/hosts de la VM ' + self.vmName + '...')

        # Cambiamos el nombre de host de las VM y asignamos el propio de cada una
        call([f"sudo virt-edit -a {self.vmName}.qcow2 /etc/hosts -e 's/127.0.1.1.*/127.0.1.1 {self.vmName}/'"], shell=True)

        # Creamos el fichero hostname y lo copiamos en la VM
        call([f"echo {self.vmName} > hostname"], shell=True)
        call([f"sudo virt-copy-in -a {self.vmName}.qcow2 hostname /etc/"], shell=True)
        call(["rm -f hostname"], shell=True)
        
        log.info('Archivo /etc/hosts editado correctamente \n')

    def create_interfaces_file_aux(self,ifs):
        for name, config in ifs:
            if name == "lb1":
                # Obtenemos los valores de la configuración
                addr = config.get("addr")
                mask = config.get("mask")
                #Creamos la estructura del archivo de configuración de /etc/network/interfaces
                self.content += f"""auto lo
        iface lo inet loopback
        auto eth1
        iface eth1 inet static
        address {addr}
        netmask {mask}
        """
                break
        # Guardamos el contenido en el archivo ya creado        
        call([f"echo '{self.content}' >> interfaces"], shell=True)



    def create_interfaces_file(self,ifs):

        log.info('Creando el archivo de configuración de las interfaces de red de la VM ' + self.vmName + '...')

        # Creamos el archivo de configuración de las interfaces de red
        for name, config in ifs:
            if name == self.vmName:
                addr = config.get("addr")
                mask = config.get("mask")
                gateway = config.get("gateway", None)

                #Creamos la estructura del archivo de configuración de /etc/network/interfaces
                self.content += f"""auto lo
                    iface lo inet loopback
                    auto eth0
                    iface eth0 inet static
                    address {addr}
                    netmask {mask}
                    """
                # Solo agregamos el gateway si está presente (todos menos lb)
                if gateway:
                    self.content += f" gateway {gateway}\n"
                break

            elif name == "lb0" and self.vmName == "lb":
                addr = config.get("addr")
                mask = config.get("mask")

                #Creamos la estructura del archivo de configuración de /etc/network/interfaces
                self.content += f"""auto lo
                iface lo inet loopback
                auto eth0
                iface eth0 inet static
                address {addr}
                netmask {mask}
                """
                log.info("Llamando a la auxiliar")
                self.create_interfaces_file_aux(ifs)
                call(["sudo virt-edit -a lb.qcow2 /etc/sysctl.conf -e 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/'"], shell=True)
                break

        # Guardamos el contenido en un archivo 
        call([f"echo '{self.content}' > interfaces"], shell=True)
        log.debug('Este es el contenido del archivo /etc/network/interfaces' + self.content)
        call([f"sudo virt-copy-in -a {self.vmName}.qcow2 interfaces /etc/network/"], shell=True)
        call(["rm -f interfaces"], shell=True)
        log.info('Archivo de configuración de las interfaces de red creado correctamente para la VM ' + self.vmName + '\n')


    def start(self):

        log.info('Arrancando la máquina virtual ' + self.vmName + '...') 

        # Arrancamos la máquina virtual en una nueva consola
        call([f"sudo virsh start {self.vmName}"] , shell=True)
        log.debug('Abriendo consola en un terminal nuevo para la máquina virtual ' + self.vmName)
        call([f"xterm -title {self.vmName} -e sudo virsh console {self.vmName} &"], shell=True)

        log.info('Se ha arrancado la máquina virtual '+ self.vmName + '\n')


    def stop(self):

        log.info('Deteniendo la máquina virtual ' + self.vmName + '...')

        # Paramos la máquina virtual
        call([f"sudo virsh shutdown {self.vmName}"], shell=True)
        
        log.info('Se ha detenido la máquina virtual '+ self.vmName + '\n')


    def destroy(self):

        log.info('Liberando la máquina virtual ' + self.vmName + '...')

        # Destruimos la máquina virtual y liberamos los recursos 
        call([f"sudo virsh destroy {self.vmName}"], shell=True)
        call([f"sudo virsh undefine {self.vmName}"], shell=True)
        log.debug('Se ha destruido la máquina virtual ' + self.vmName)
        call([f"rm -f {self.vmName}.qcow2"], shell=True)
        call([f"rm -f {self.vmName}.xml"], shell=True)
        log.debug('Se han eliminado los archivos de la máquina virtual ' + self.vmName)
        call([f"pkill xterm"], shell=True)
        log.info('Se ha liberado la máquina virtual ' + self.vmName + '\n')


class Red:
    def __init__(self,redName):
        self.redName = redName
        
    def create_network(self):
        call([f"sudo ovs-vsctl add-br {self.redName}"], shell=True)
        log.info(f"Red {self.redName} creada \n")

    def destroy_network(self):
        call([f"sudo ovs-vsctl del-br {self.redName}"], shell=True)
        log.info(f"Red {self.redName} destruida")