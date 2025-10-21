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



