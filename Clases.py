ESTADO_EJECUCION = 'running'

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
        self.estado = '-'
        self.t_arribo = ta
        self.t_irrupcion = ti
        self.t_irrupcion_faltante = ti 
        self.t_retorno = 0
        self.t_espera = 0
        self.t_final = 0

#Clase para la CPU       
class CPU:
    def __init__(self,proceso):
        proceso.estado = ESTADO_EJECUCION
        self.proceso = proceso 