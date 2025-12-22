LISTO = 'Ready'
SUSPENDIDO = 'Ready/Suspended'
EJECUCION = 'Running'
NUEVO = 'New'
TERMINADO = 'Exit'

# Clase para las particiones
class Particion:
    def __init__(self,id,tam,dir,proc = None):
        self.id = id 
        self.tamaño = tam 
        self.direccion = dir 
        self.proceso = proc
        self.fragmentacion = tam 

# Clase para los procesos
class Proceso:
    def __init__(self,id,tam,ti,ta):
        self.id = id 
        self.tamaño = tam 
        self.estado = NUEVO
        self.t_arribo = ta # Tiempo de arribo al sistema 
        self.t_arribo_efectivo = 0 # Tiempo de arribo a la cola de listos
        self.t_irrupcion = ti
        self.t_irrupcion_faltante = ti 
        self.t_retorno = 0
        self.t_espera = 0
        self.t_final = 0

# Clase para la CPU       
class CPU:
    def __init__(self):
        self.proceso = None 

# Clase para la memoria
class Memoria: 
    def __init__(self):
        self.particiones = [ 
            Particion(0,100,0,"SO"),        # Particion para el sistema operativo
            Particion(1,250,100,None),
            Particion(2,150,350,None),
            Particion(3,50,500,None)
        ]

    def asignarProceso(self, proceso):
        mejor = None

        # Asignacion Best-fit
        for p in self.particiones:
            if p.proceso is None and proceso.tamaño <= p.tamaño:    
                if mejor is None or (p.tamaño - proceso.tamaño) < (mejor.tamaño - proceso.tamaño):  # Se compara la fragmentacion interna
                    mejor = p

        # Si encontro particion, asignar proceso
        if mejor:
            mejor.proceso = proceso
            mejor.fragmentacion = mejor.tamaño - proceso.tamaño
            proceso.estado = LISTO
            return True
        else:
            return False
    
    def liberarParticion(self, proceso):
        for p in self.particiones:
            if p.proceso == proceso:
                p.proceso = None
                p.fragmentacion = p.tamaño
                break

# Clase para el Planificador SRTF, se encuentra el metodo para agregar un proceso a la cola de listos
class Planificador:    
    def __init__(self):
        self.cola_de_listos = []
        self.cola_de_suspendidos = []
    
    def agregarProceso(self,proceso):
        self.cola_de_listos.append(proceso)
        self.cola_de_listos.sort(key=lambda p: p.t_irrupcion_faltante)  # Ordena la cola de listos segun el tiempo de irrupcion faltante
