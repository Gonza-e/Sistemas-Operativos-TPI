from Simulador import Simulador,leer_procesos

if __name__ == "__main__":
    procesos = leer_procesos("procesos.txt")
    sim = Simulador()
    sim.cargarProcesos(procesos)
    sim.ejecutar()
    sim.mostrar_estado()