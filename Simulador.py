from Clases import *
from tabulate import tabulate
import csv

class Simulador:
    def __init__(self):
        self.memoria = Memoria()
        self.cpu = CPU()
        self.planificador = Planificador()
        self.procesos_terminados = []
        self.cola_nuevos = []
        self.todos_los_procesos = []
        self.multiprogramacion = 0
        self.limiteProcesos = 10

    
    # -----------------------------------------------------
    # Carga inicial de procesos desde lista o archivo
    # -----------------------------------------------------
    def cargarProcesos(self, procesos):
        self.todos_los_procesos = sorted(procesos, key=lambda p: p.t_arribo)
        print(f"\n✅ {len(procesos)} procesos cargados correctamente.")

    # -----------------------------------------------------
    # Ejecución principal del simulador (ciclo de reloj)
    # -----------------------------------------------------
    def ejecutar(self):
        tiempo_actual = 0

        # Con este bucle verificamos que solo entren hasta 10 procesos como maximo y que tambien 
        # solamente entren aquellos procesos que tengan un tamaño menor o igual al de la particion mas grande
        procesos_en_espera = []
        for pn in self.todos_los_procesos:
            if self.limiteProcesos > 0 and pn.tamaño <= 250:
                procesos_en_espera.append(pn)
                self.limiteProcesos -= 1

        print("\n🚀 INICIO DE LA SIMULACIÓN\n")

        while True:
            # 1️⃣ Arribo de nuevos procesos
            print(f"\n __________________________ t = {tiempo_actual} ___________________________")
            nuevos = [p for p in procesos_en_espera if p.t_arribo == tiempo_actual]
            for p in nuevos:
                self.limiteProcesos -= 1
                procesos_en_espera.remove(p)
                print(f"\n🕐 t={tiempo_actual}: Proceso {p.id} arriba (tamaño={p.tamaño}K, irrupción={p.t_irrupcion})")

                # Si hay espacio en el grado de multiprogramación
                if self.multiprogramacion < 5:
                    asignado = self.memoria.asignarProceso(p)
                    if asignado:
                        self.planificador.agregarProceso(p)
                        print(f"🟢 Proceso {p.id} cargado en memoria y listo para ejecutar.")
                    else:
                        p.estado = SUSPENDIDO
                        self.planificador.cola_de_suspendidos.append(p)
                        print(f"💤 Proceso {p.id} suspendido (sin espacio en memoria).")

                    self.multiprogramacion += 1
                else:
                    # MULTIPROGRAMACIÓN LLENA → pasa a COLA DE NUEVOS
                    p.estado = "NUEVO"
                    self.cola_nuevos.append(p)
                    print(f"⏳ P{p.id} enviado a COLA NUEVOS (multiprogramación llena).")

                self.mostrar_estado(tiempo_actual)
                input("\n Presione ENTER para continuar...\n")


            # 2️⃣ Reactivar suspendidos si hay memoria libre
            for ps in list(self.planificador.cola_de_suspendidos):
                if ps.t_arribo <= tiempo_actual:
                    asignado = self.memoria.asignarProceso(ps)
                    if asignado:
                        ps.estado = LISTO
                        self.planificador.agregarProceso(ps)
                        self.planificador.cola_de_suspendidos.remove(ps)
                        print(f"🟢 Proceso {ps.id} reactivado (memoria disponible en t={tiempo_actual}).")

            # 🔄 Admitir solo UN proceso desde COLA NUEVOS si hay espacio
            if self.multiprogramacion < 5 and self.cola_nuevos:

                candidato = self.cola_nuevos[0]  # solo mirar el primero

                asignado = self.memoria.asignarProceso(candidato)

                if asignado:
                    candidato.estado = LISTO
                    self.planificador.agregarProceso(candidato)
                    self.cola_nuevos.pop(0)
                    self.multiprogramacion += 1
                    print(f"🟢 P{candidato.id} admitido desde COLA NUEVOS")
                else:
                    # No intentamos con otros nuevos hasta que cambie la memoria
                    pass

            # 3️⃣ Seleccionar proceso según SRTF
            if self.cpu.proceso is None and self.planificador.cola_de_listos:
                self.cpu.proceso = self.planificador.cola_de_listos.pop(0)
                self.cpu.proceso.estado = EJECUCION
                print(f"⚙️ t={tiempo_actual}: CPU toma P{self.cpu.proceso.id} para ejecutar.")

            # Revision 
            # 4️⃣ Expropiación SRTF
            if self.cpu.proceso and self.planificador.cola_de_listos:
                candidato = self.planificador.cola_de_listos[0]
                if candidato.t_irrupcion_faltante < self.cpu.proceso.t_irrupcion_faltante:
                    print(f"⚠️ Expropiación: P{candidato.id} tiene menor tiempo restante que P{self.cpu.proceso.id}")
                    self.cpu.proceso.estado = LISTO
                    self.planificador.agregarProceso(self.cpu.proceso)
                    self.cpu.proceso = self.planificador.cola_de_listos.pop(0)
                    self.cpu.proceso.estado = EJECUCION

            # 5️⃣ Ejecutar una unidad de CPU
            if self.cpu.proceso:
                self.cpu.proceso.t_irrupcion_faltante -= 1

                # Proceso termina
                if self.cpu.proceso.t_irrupcion_faltante <= 0:
                    self.cpu.proceso.estado = TERMINADO
                    self.cpu.proceso.t_final = tiempo_actual + 1
                    self.procesos_terminados.append(self.cpu.proceso)
                    print(f"\n🔴 t={tiempo_actual + 1}: P{self.cpu.proceso.id} terminó ejecución.")
                    self.memoria.liberarParticion(self.cpu.proceso)
                #    self.mostrar_estado(tiempo_actual + 1)
                    self.multiprogramacion -= 1
                    print("Se decremento por P terminado")
                    self.mostrar_estado(tiempo_actual + 1)
                    input("\n⏸️ Presione ENTER para continuar...\n")
                    self.cpu.proceso = None

            # 6️⃣ Condición de fin (no quedan procesos activos)
            if (not procesos_en_espera and not self.planificador.cola_de_listos and not self.planificador.cola_de_suspendidos and not self.cpu.proceso):
                print("\n✅ SIMULACIÓN FINALIZADA.")
                self.mostrar_informe_final(tiempo_actual)
                break

            tiempo_actual += 1

    # -----------------------------------------------------
    # Muestra el estado actual del sistema
    # -----------------------------------------------------
    def mostrar_estado(self, tiempo):
    #    print(f"\n __________________________ t = {tiempo} ___________________________")
        print(f"\n📋 ESTADO DEL SISTEMA")

        if self.cpu.proceso:
            if self.cpu.proceso.t_irrupcion_faltante > 0:
                print(f"🖥️ CPU: ejecutando P{self.cpu.proceso.id} (restante={self.cpu.proceso.t_irrupcion_faltante})")
            else: 
                print("🖥️ CPU: libre")
        else:
            print("🖥️ CPU: libre")

        # Tabla de memoria
        data = []
        for p in self.memoria.particiones:
            if isinstance(p.proceso, Proceso):
                data.append([p.id, f"{p.tamaño}K", f"P{p.proceso.id}", p.proceso.estado, f"{p.fragmentacion}K"])
            else:
                data.append([p.id, f"{p.tamaño}K", "-", "-", f"{p.fragmentacion}K"])
        print("\n Tabla de memoria:")
        print(tabulate(data, headers=["ID", "Tamaño", "Proceso", "Estado", "Fragmentación"], tablefmt="fancy_grid"))

        # Cola de listos
        tabla_listos = [[p.id, p.t_irrupcion_faltante, p.estado] for p in self.planificador.cola_de_listos]
        print("\n Cola de listos:")
        print(tabulate(tabla_listos, headers=["ID", "Tiempo restante", "Estado"], tablefmt="fancy_grid"))

        # Cola de nuevos
        tabla_nuevos = [[p.id, p.t_arribo, p.estado] for p in self.cola_nuevos]
        print("\n Cola de nuevos:")
        print(tabulate(tabla_nuevos, headers=["ID", "Arribo", "Estado"], tablefmt="fancy_grid"))

        tabla_susp = [[p.id, p.tamaño, p.estado] for p in self.planificador.cola_de_suspendidos]
        print("\n Cola suspendidos:")
        print(tabulate(tabla_susp, headers=["ID", "Tamaño", "Estado"], tablefmt="fancy_grid"))

        print(f"El grado de multiprogramacion es: {self.multiprogramacion}\n")


    # -----------------------------------------------------
    # Informe final (tiempos promedios y rendimiento)
    # -----------------------------------------------------
    def mostrar_informe_final(self, tiempo_final):
        print("\n📊 INFORME FINAL DE LA SIMULACIÓN\n")

        data = []
        total_retorno = 0
        total_espera = 0

        for p in self.procesos_terminados:
            t_retorno = p.t_final - p.t_arribo
            t_espera = t_retorno - p.t_irrupcion
            total_retorno += t_retorno
            total_espera += t_espera
            data.append([p.id, p.t_arribo, p.t_irrupcion, p.t_final, t_retorno, t_espera])

        prom_retorno = total_retorno / len(self.procesos_terminados)
        prom_espera = total_espera / len(self.procesos_terminados)
        rendimiento = len(self.procesos_terminados) / tiempo_final

        print(tabulate(data, headers=["ID", "Arribo", "Irrupción", "Final", "Retorno", "Espera"], tablefmt="fancy_grid"))
        print(f"\n📈 Tiempo medio de retorno: {prom_retorno:.2f}")
        print(f"📉 Tiempo medio de espera: {prom_espera:.2f}")
        print(f"⚙️  Rendimiento del sistema: {rendimiento:.3f} procesos/unidad de tiempo")


def leer_procesos(ruta_archivo):

    procesos = []

    try:
        with open(ruta_archivo, "r", newline="", encoding="utf-8") as f:
            lector = csv.reader(f)

            for fila in lector:
                # Ignorar líneas vacías
                if not fila or all(campo.strip() == "" for campo in fila):
                    continue

                # Permitir comentarios estilo "# ..."
                linea_original = ",".join(fila)
                if linea_original.strip().startswith("#"):
                    continue

                # Validar cantidad correcta de columnas
                if len(fila) != 4:
                    print(f"⚠️  Línea ignorada (formato incorrecto): {fila}")
                    continue

                try:
                    id_p, tam, t_arribo, t_irrupcion = map(int, fila)
                except ValueError:
                    print(f"⚠️  Línea ignorada (valores no numéricos): {fila}")
                    continue

                procesos.append(Proceso(id_p, tam, t_irrupcion, t_arribo))

        procesos.sort(key=lambda p: p.t_arribo)
        print(f"\n📥 Se cargaron {len(procesos)} procesos desde '{ruta_archivo}' correctamente.\n")
        return procesos

    except FileNotFoundError:
        print(f"❌ No se encontró el archivo '{ruta_archivo}'.")
        return []
