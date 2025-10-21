LISTO = 'Ready'
SUSPENDIDO = 'Suspended'
EJECUCION = 'Running'
NUEVO = 'New'
TERMINADO = 'Exit'

#Clase para las particiones
class Particion:
    def __init__(self,id,tam,dir,proc = None):
        self.id = id 
        self.tamaño = tam 
        self.direccion = dir 
        self.proceso = proc
        self.fragmentacion = tam 

#Clase para los procesos
class Proceso:
    def __init__(self,id,tam,ti,ta):
        self.id = id 
        self.tamaño = tam 
        self.estado = NUEVO
        self.t_arribo = ta
        self.t_irrupcion = ti
        self.t_irrupcion_faltante = ti 
        self.t_retorno = 0
        self.t_espera = 0
        self.t_final = 0

#Clase para la CPU       
class CPU:
    def __init__(self):
        self.proceso = None 

#Clase para la memoria
class Memoria: 
    def __init__(self):
        self.particiones = [ 
            Particion(1,100,0,"SO"),        #Particion para el sistema operativo
            Particion(1,250,100,None),
            Particion(2,150,350,None),
            Particion(3,50,500,None)
        ]

    #Asignacion Best-fit
    def asignarProceso(self,proceso):
        mejor = None        #Inicializamos la variable mejor para la mejor particion
        for p in self.particiones:       #Recorremos la lista de particiones
            if p.proceso is None and proceso.tamaño <= p.tamaño:         #Si la particion esta vacia y el tamaño del proceso es menor que la particion     
                if mejor is None or p.tamaño < mejor.tamaño:        #Si mejor esta vacio o el tamaño de la mejor particion actual es menor al tamaño de otra particion 
                    mejor = p       #Se asigna el proceso a la particion

                if mejor:       #Si mejor no esta vacio entonces se le asigna el proceso a la mejor particion
                    mejor.proceso = proceso 
                    mejor.fragmentacion = mejor.tamaño - proceso.tamaño 
                    proceso.estado = LISTO
                    return True 
                else: 
                    return False        #Devuelve falso en caso de no encontrarse una particion 
    
    def liberarParticion(self,proceso):         #Libera la particion 
        for p in self.particiones:
            if p.proceso == proceso:
                p.proceso = None 
                p.fragmentacion = p.tamaño 

#Clase para el Planificador SRTF
class Planificador:    
    def __init__(self):
        self.cola_de_listos = []
        self.cola_de_suspendidos = []
        self.tiempo = 0         #Tiempo global
    
    def agregarProceso(self,proceso):
        self.cola_de_listos.append(proceso)
        self.cola_de_listos.sort(key=lambda p: p.t_irrupcion_faltante)      #Ordena la cola de listos segun el tiempo de irrupcion faltante
        
    def siguienteProceso(self):
        if self.cola_de_listos:
            return self.cola_de_listos[0]        #Selecciona el primer proceso de la cola de listos
        return None

class Simulador:
    def __init__(self):
        self.memoria = Memoria()
        self.cpu = CPU()
        self.planificador = Planificador()
        self.procesos_terminados = []
        self.todos_los_procesos = []        #Lista auxiliar para guardar todos los procesos que entran

    def cargarProcesos(self, procesos):
        self.todos_los_procesos = procesos[:]        #Se copian todos los procesos que vayan arribando a la lista 
        for p in procesos:
            asignado = self.memoria.asignarProceso(p)
            if asignado:
                self.planificador.agregarProceso(p)      #Si hay un proceso en alguna particion entonces este es movido a la cola de listos
            else:
                p.estado = SUSPENDIDO        #En caso de que no haya una particion disponible, el procesos pasa a la cola de suspendidos
                self.planificador.cola_de_suspendidos.append(p)
                print(f"💤 Proceso {p.id} suspendido (sin memoria disponible)")

    def ejecutar(self):
        print("\n Inicio de la simulacion ")

        #Lista de procesos pendientes de arribo ordenados por tiempo de arribo
        pendientes = sorted(self.todos_los_procesos, key=lambda x: x.t_arribo)

        tiempo_actual = 0
        procesos_en_espera = pendientes.copy()

        while self.planificador.cola_de_listos or self.cpu.proceso or self.planificador.cola_de_suspendidos or procesos_en_espera:      #Mientas que haya procesos este bucle se va a ejecutar

            #Llegada de nuevos procesos
            while procesos_en_espera and procesos_en_espera[0].t_arribo == tiempo_actual:       #Verifica si el tiempo de arribo del proceso es igual al tiempo actual
                p = procesos_en_espera.pop(0)
                asignado = self.memoria.asignarProceso(p)
                if asignado:
                    self.planificador.agregarProceso(p)
                    print(f"\n🟢 Llega el proceso {p.id} en t={tiempo_actual}")
                    self.mostrar_estado()
                    input("Presione ENTER para continuar...")
                else:
                    print(f"\n❌ No hay memoria para el proceso {p.id} en t={tiempo_actual}")

            # Si no hay nada en CPU y hay procesos listos, tomamos el siguiente
            actual = self.planificador.siguienteProceso()
            if self.cpu.proceso is None and actual:
                self.cpu.proceso = self.planificador.cola_de_listos.pop(0)
                self.cpu.proceso.estado = EJECUCION

            # Ejecutar una unidad de tiempo si hay algo en CPU
            if self.cpu.proceso:
                self.cpu.proceso.t_irrupcion_faltante -= 1

                # Si termina el proceso
                if self.cpu.proceso.t_irrupcion_faltante == 0:
                    self.cpu.proceso.t_final = tiempo_actual + 1
                    self.cpu.proceso.estado = TERMINADO
                    self.procesos_terminados.append(self.cpu.proceso)
                    self.memoria.liberarParticion(self.cpu.proceso)

                    #Intentar reactivar procesos suspendidos
                    for ps in list(self.planificador.cola_de_suspendidos):  #hcemos copia de la lista
                        asignado = self.memoria.asignarProceso(ps)
                        if asignado:
                            ps.estado = LISTO
                            self.planificador.agregarProceso(ps)
                            self.planificador.cola_de_suspendidos.remove(ps)
                            print(f"🟢 Proceso {ps.id} reactivado (memoria liberada en t={tiempo_actual + 1})")

                    print(f"\n🔴 Proceso {self.cpu.proceso.id} terminó en t={tiempo_actual + 1}")
                    self.mostrar_estado()
                    input("Presione ENTER para continuar...")

                    self.cpu.proceso = None

            tiempo_actual += 1
            self.planificador.tiempo = tiempo_actual


    def mostrar_estado(self):
        print("\n=== ESTADO DEL SISTEMA ===")

        # CPU
        if self.cpu.proceso:
            print(f"🖥️ CPU ejecutando: Proceso {self.cpu.proceso.id} ({self.cpu.proceso.estado})")
        else:
            print("🖥️ CPU libre")

        # Particiones
        print("\n📦 Tabla de particiones:")
        for p in self.memoria.particiones:
            if isinstance(p.proceso, Proceso):
                print(f"Partición {p.id}: {p.tamaño}K | P{p.proceso.id} ({p.proceso.estado}) | Frag: {p.fragmentacion}K")
            else:
                print(f"Partición {p.id}: {p.tamaño}K | Libre | Frag: {p.fragmentacion}K")

        # Colas
        print("\n🟢 Cola de listos:", [f"P{p.id}({p.estado})" for p in self.planificador.cola_de_listos])
        print("💤 Cola suspendidos:", [f"P{p.id}({p.estado})" for p in self.planificador.cola_de_suspendidos])
        print("🔴 Terminados:", [f"P{p.id}" for p in self.procesos_terminados])

def leer_procesos(archivo):
    procesos = []
    with open(archivo, 'r') as f:
        for linea in f:
            id, tam, ta, ti = linea.strip().split(',')
            procesos.append(Proceso(int(id), int(tam), int(ti), int(ta)))
    return procesos

if __name__ == "__main__":
    procesos = leer_procesos("procesos.txt")
    sim = Simulador()
    sim.cargarProcesos(procesos)
    sim.ejecutar()
    sim.mostrar_estado()


