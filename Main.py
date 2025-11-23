from Simulador import Simulador, leer_procesos

if __name__ == "__main__":
    procesos = leer_procesos("procesos.csv")

    if not procesos:
        print("No hay procesos para simular.")
    else:
        sim = Simulador()
        sim.cargarProcesos(procesos)
        sim.ejecutar()

