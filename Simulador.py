from Clases import Particion,Planificador,Proceso,CPU,Memoria,SUSPENDIDO,LISTO,EJECUCION,NUEVO,TERMINADO
from tabulate import tabulate 

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

        # 📦 Tabla de particiones
        data = []
        for p in self.memoria.particiones:
            if isinstance(p.proceso, Proceso):
                data.append([p.id, f"{p.tamaño}K", f"P{p.proceso.id}", p.proceso.estado, f"{p.fragmentacion}K"])
            else:
                data.append([p.id, f"{p.tamaño}K", "-", "-", f"{p.fragmentacion}K"])
        
        print("\n📦 Tabla de particiones:")
        print(tabulate(data, headers=["ID", "Tamaño", "Proceso", "Estado", "Fragmentación"], tablefmt="fancy_grid"))

        # 🟢 Cola de listos
        if self.planificador.cola_de_listos:
            listos = [[p.id, p.estado, p.t_irrupcion_faltante] for p in self.planificador.cola_de_listos]
            print("\n🟢 Cola de listos:")
            print(tabulate(listos, headers=["ID", "Estado", "Tiempo Restante"], tablefmt="fancy_grid"))
        else:
            print("\n🟢 Cola de listos: vacía")

        # 😴 Cola suspendidos
        if self.planificador.cola_de_suspendidos:
            susp = [[p.id, p.estado, p.tamaño] for p in self.planificador.cola_de_suspendidos]
            print("\n💤 Cola suspendidos:")
            print(tabulate(susp, headers=["ID", "Estado", "Tamaño"], tablefmt="fancy_grid"))
        else:
            print("\n💤 Cola suspendidos: vacía")

        # 🔴 Terminados
        if self.procesos_terminados:
            term = [[p.id, p.estado, p.t_final] for p in self.procesos_terminados]
            print("\n🔴 Terminados:")
            print(tabulate(term, headers=["ID", "Estado", "Tiempo Fin"], tablefmt="fancy_grid"))
        else:
            print("\n🔴 Terminados: ninguno")

def leer_procesos(archivo):
    procesos = []
    with open(archivo, 'r') as f:
        for linea in f:
            id, tam, ta, ti = linea.strip().split(',')
            procesos.append(Proceso(int(id), int(tam), int(ti), int(ta)))
    return procesos