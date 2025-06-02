# ⚙️ CDPS_practica-creativa1

> **ES**: Proyecto desarrollado en la asignatura de **Centros de Datos y de Provisión de Servicios (CDPS)** durante el curso 2024-2025 en el **GITST** (Grado en Ingeniería de Tecnologías y Servicios de Telecomunicación), **ETSIT-UPM**.  
> **EN**: Project developed for the **CDPS** (Data Centers and Service Provision) course during the 2024-2025 academic year in the **GITST** degree at **ETSIT-UPM**.

---

## 📌 Descripción | Description

🟢 **ES:**  
Este proyecto consiste en el desarrollo de un script en **Python** que automatiza la creación del escenario virtual de pruebas de la práctica 2, basado en máquinas virtuales KVM y redes virtuales con **Open vSwitch (OVS)**. El script permite crear, iniciar, parar y destruir el entorno de forma automática, con configuración personalizada de red, número de servidores a crear y balanceo de tráfico.

🔵 **EN:**  
This project involves developing a **Python** script to automate the setup of the virtual test environment for Practice 2. The scenario is based on KVM virtual machines and virtual networks using **Open vSwitch (OVS)**. The script supports automatic creation, startup, shutdown, and destruction of the environment, including network and load balancing configuration.


📷 **ES/EN:**  
La siguiente imagen representa el escenario básico que será creado por el script:  
_The following image shows the basic environment that will be created by the script:_

<p align="center">
  <img src="https://github.com/user-attachments/assets/5c5d7c93-c524-42a8-960e-6442eff6b3b8" alt="Network architecture diagram" width="600">
</p>

---

## 🚀 Características | Features

✅ **ES:**  
✔️ Creación de máquinas virtuales desde imagen base mediante archivos `.qcow2`.  
✔️ Definición y conexión de interfaces de red virtual.  
✔️ Configuración de red (hostname, interfaces y hosts) automática.  
✔️ Balanceador configurado como router.  
✔️ Gestión de VMs con comandos `create`, `start`, `stop`, `destroy`.  
✔️ Soporte para entre 1 y 5 servidores web (configurable vía JSON).  
✔️ Soporte para trazas de depuración con el módulo `logging`.  
✔️ Biblioteca modular `lib_vm.py` para manejar VMs y redes virtuales.  
✔️ Opcional: comando `monitor` para observar el estado del escenario.

✅ **EN:**  
✔️ Creation of virtual machines from base image using `.qcow2` diffs.  
✔️ Definition and attachment of virtual network interfaces.  
✔️ Automatic network configuration (hostname, interfaces, hosts).  
✔️ Load balancer configured as router.  
✔️ VM management using `create`, `start`, `stop`, `destroy` commands.  
✔️ Support for 1 to 5 web servers (configured via JSON).  
✔️ Debugging enabled via Python's `logging` module.  
✔️ Modular library `lib_vm.py` for VM and network management.  
✔️ Optional: `monitor` command to check scenario status.

---

## 🛠️ Tecnologías | Technologies Used

- 🐍 **Python 3** → Lenguaje principal del script.  
- 💻 **KVM** → Virtualización de máquinas.  
- 🌐 **Open vSwitch (OVS)** → Gestión de redes virtuales.  
- 📄 **libvirt XML** → Descripción de VMs.  
- 📦 **virt-tools** → Herramientas como `virt-copy-in`, `virt-edit`, `virt-cat` para editar imágenes.  
- 🔧 **virsh** → Comandos de control de VMs.  
- 🧰 **lxml.etree** → Manipulación de ficheros XML.  
- 🧾 **JSON** → Fichero de configuración (`manage-p2.json`).  
- 📜 **logging** → Registro de eventos y depuración.

---

## 📦 Instalación y uso | Installation and Usage

🟢 ES:
Asegúrate de que el directorio de trabajo contenga los siguientes archivos:
```bash
- cdps-vm-base-pc1.qcow2
- plantilla-vm-pc1.xml
- manage-p2.py
- lib_vm.py
- manage-p2.json
```
Para ejecutar el script:
```bash
./manage-p2.py create   # Crea el escenario  
./manage-p2.py start    # Arranca las VMs y muestra la consola  
./manage-p2.py stop     # Para las VMs (sin eliminar imágenes)  
./manage-p2.py destroy  # Elimina VMs, redes y ficheros creados  
```
```bash
Puedes ver todos los comandos disponibles ejecutando:  
./manage-p2.py -help
```
Comandos disponibles:

| Orden    | Descripción                                                                                         |
|----------|---------------------------------------------------------------------------------------------------|
| create   | Inicializa las máquinas virtuales y crea el escenario.                                            |
| start    | Arranca las máquinas virtuales y muestra su consola. Si no se especifica un nombre, se ejecuta para todas las VM. |
| stop     | Detiene las máquinas virtuales sin liberar los recursos. Si no se especifica un nombre, se ejecuta para todas las VM. |
| destroy  | Libera el escenario y elimina los ficheros creados.                                               |
| machines | Te enseña el estado de todas las máquinas virtuales.                                              |
| stats    | Muestra estadísticas detalladas de las VM como CPU y memoria.                                     |
| info     | Para ver información detallada de las máquinas.                                                   |


🔵 EN:
Ensure the working directory contains the following files:

- cdps-vm-base-pc1.qcow2
- plantilla-vm-pc1.xml
- manage-p2.py
- lib_vm.py
- manage-p2.json

To run the script:
```bash
./manage-p2.py create   # Create the environment  
./manage-p2.py start    # Start VMs and show console  
./manage-p2.py stop     # Stop VMs (keep data)  
./manage-p2.py destroy  # Remove all created VMs, files and networks  
```
You can list all available commands by running:  
```bash
./manage-p2.py -help
```

Available commands:

| Command  | Description                                                                 |
|----------|-----------------------------------------------------------------------------|
| create   | Initializes virtual machines and creates the environment.                   |
| start    | Starts VMs and shows their console. Runs on all VMs by default.             |
| stop     | Stops VMs without deleting resources. Runs on all by default.               |
| destroy  | Frees the environment and deletes all generated files.                      |
| machines | Shows the current status of all virtual machines.                           |
| stats    | Displays detailed VM statistics (CPU, memory, etc.).                        |
| info     | Shows detailed information about each VM.                                   |



##📂 Estructura del Proyecto | Project Structure
CDPS_practica-creativa1/

├── cdps-vm-base-pc1.qcow2     
├── plantilla-vm-pc1.xml       
├── manage-p2.py              
├── lib_vm.py                 
├── manage-p2.json      
├── README.md       

---
##🧪 Configuración de Ejemplo | Sample Configuration
```bash
{
  "number_of_servers": 3,
  "debug": true
}
```
---
## 📬 Contacto | Contact

📩 **serguccierrez** → [GitHub Profile](https://github.com/serguccierrez)  
Si tienes preguntas o sugerencias, crea un **issue** en este repositorio.  

If you have any questions or suggestions, feel free to open an **issue** in this repository.  

---

💡 _Made with ❤️ by **Serguccierrez**._
