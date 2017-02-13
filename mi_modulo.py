# -*- coding: utf-8 -*-
from random import randint, random
import urllib ### Necesario para conectarse a URLs
from openerp import models, api, fields ### Necesario para usar campos, modelos y clases en ODOO
import openerp.addons.decimal_precision as dp ### Necesarios para calculos de ODOO
from datetime import datetime, timedelta ### Librerias para la fecha y hora, comparar horas
import os, subprocess, re  ### os y subprocess son necesarios para usar comandos del sistema, re es para expresiones regulares con python
from lxml import etree ### Necesario para leer el arbol  XML
import csv, operator ### Libreria necesaria para usar csv y tratar los campos como listas
from zipfile import ZipFile ### Importar para descomprimir los archivos que nos llegan al FTP


### Dependiendo del usuario del sistema donde queremos colocar las carpetas para mover y hacer mas facil de llevar el sistema debemos tener en cuenta esta ruta
#ruta_de_usuario =  '/home/odoo/archivos_kiu/'   ### Es muy importante esta ruta en el README.pdf tienen como modificarlo
ruta_de_usuario =  '/home/odoo/archivos_kiu/'
### En el archivo carpetas_a_crear.sh tambien debemos colocar esta ruta, tambien debemos configurar bien el FTP paraque lleguen los archivos y poder moverlos a las carpetas correspondientes
### esta deberia ser la carpeta compartida /home/odoo/archivos_kiu/ o la carpeta donde llegan los archivos por el ftp


### creamos la clase KIU para los archivos CMAS
class kiu(models.Model):
    _name = "kiu"
    ### como vamos a extraer datos de los archivos BOX necesitamos especificar una tarea que luego pondremos en el planificador de tareas
    ### Esto se hace creando un metodo o funcion create_CMAS
    def create_CMAS(self, cr, uid, context=None):
                    ### aqui va la ruta de los archivos descomprimidos, enviamos los nombres a el txt para luego ser leidos
                    ruta = "ls " +ruta_de_usuario +'CRS_descomprimidos'+ ' > ' + ruta_de_usuario +'CMAS_descomprimidos.txt' ### ruta a ejecutar como si de la shell se trata
                    ps = subprocess.Popen(ruta,shell=True) ### Ejecutar la linea anterior
                    
                    #os.system("ls /home/odoo/archivos_kiu/CRS_descomprimidos  > /home/odoo/archivos_kiu/CMAS_descomprimidos.txt")
                    archivo_CMAS =ruta_de_usuario+'/CMAS_descomprimidos.txt' ### Archivo txt con la lista de CMAS a ser leidos
                    archi_CMAS = open(archivo_CMAS,'r')  ### lo hacemos legible
                    class_cmas_obj = self.pool.get('kiu')  ### creamos la clase a mapear para agregar datos y buscar en la base de datos de ODOO
                    iterador = 0 ## un iterador para hacer pruebas

                    for archivo_cmas_a_extraer in archi_CMAS: ### Leemos los archivos de la lista de CMAS_descomprimidos.txt
                               #if iterador < 5: ### Descomentar esta linea para pruebas solo veras 5 archivos a la vez
                                    arch_a_extraerle_datos = ruta_de_usuario+'/CRS_descomprimidos/'+archivo_cmas_a_extraer ### Aqui pasamos el archivo_cmas_a_extraer de la lista que pasamos por el for
                                    arch_a_extraerle_datos = arch_a_extraerle_datos.strip() ### Borramos los espacios
                                    iterador +=1 ### sumamos unos para pruebas
                
                                    if "formatear_CRS_CMAS.py" == archivo_cmas_a_extraer or archivo_cmas_a_extraer =="lista_CRS_CMAS": # Aqui puedes agrega archivos que existen en esa carpeta pero no deberian, por ejemplo algun py con nombre cmas
                                              continue ## No hacer nada
                                    else:  #Aqui comenzamos a hacer algo
                                                                    archivo = arch_a_extraerle_datos ### Leemos el archivo, podemos usar reader= open(arch_a_extraerle_datos, 'r')
                                                                    reader= open(archivo, 'r')
                                                                    concuerdan_lineas = 0  ### dato para saber cuantos archivos hacemos
                                                                    ### Creamos algunas listas, hacer ctrl+f y buscar para saber para que son
                                                                    list_total_real = [] 
                                                                    list_total_calculado = [] 
                                                                    list_equivfare= [] 
                                                                    total_calculado2 = False
                                                                    total_real = False
                                                                    cantidad_archivos  =  0  ### dato para saber cuantos archivos hacemos
                                                                    list_total_calculado_REAL = []
                                                                    list_total_real_REAL = []
                                                                    lista_tuplas_pnrs = []
                                                                    numeros_K = 0 ### dato para saber cuantos archivos hacemos
                                                                    for line in reader:  ### Leemos cada linea
                                                                                  
                                                                                  if line[0] == '1':
                                                                                                 ### si la linea comienza en 1 nos interesa solo la fecha del archivo
                                                                                                 fecha_archivo = line[1:8]
                                                                                  if line[0] == '2':
                                                                                                  ### Si la linea comienza por 2
                                                                                                               ### Creamos algunas listas para los impuestos dentro de los archivos
                                                                                                               ### Si se quiere agregar nuevos impuestos deben agregarse aqui
                                                                                                               ### Algo importante crear el impuesto aqui para no hacer 0 o vacio a los otros impuestos 
                                                                                                                lista_monto_6A = []
                                                                                                                lista_monto_AJ = []
                                                                                                                lista_monto_AK = []
                                                                                                                lista_monto_AY = []
                                                                                                                lista_monto_US = []
                                                                                                                lista_monto_EU = []
                                                                                                                lista_monto_VJ = []
                                                                                                                lista_monto_XA = []
                                                                                                                lista_monto_XY = []
                                                                                                                lista_monto_YC = []
                                                                                                                lista_monto_XF = []
                                                                                                                lista_monto_YQ = []
                                                                                                                lista_monto_YN = []
                                                                                                                lista_monto_QC = []
                                                                                                                ### Extraccion de algunos datos importantes en el archivo
                                                                                                                tipo_pasajero = line[28:30]
                                                                                                                numero_boleto = line[32:45]
                                                                                                                motivo_facturacion_codigo = line[46:52]
                                                                                                                pasajero_principal = line[74:123]
                                                                                                                code_emisor = line[66:71]
                                                                                                                numero_motivos = line[45:46]
                                                                                  if line[0] == '4':
                                                                                                  ### Si la linea comienza por 4
                                                                                                  ### Cree 2 if por que una cosa es los montos para VEF ya que los montos son muy grandes y no se adaptan como en cualquier otro monto
                                                                                                  if "VE" not in archivo :  ### Si VE no esta en archivo
                                                                                                                monto_en_moneda = line[100:108]
                                                                                                                monto_en_moneda = float(monto_en_moneda)
                                                                                                                moneda = line[97:100]
                                                                                                                record_locator = line[7:14]
                                                                                                                ruta = line[20:27]
                                                                                                                impuesto_principal_1 = line[117:119]
                                                                                                                monto_tax_1 = line[110:117]
                                                                                                                monto_tax_1 = monto_tax_1.strip()
                                                                                                                ### las variables descritas no necesitan comentario
                                                                                                                if monto_tax_1 == "": ### si no ay monto es 0
                                                                                                                                monto_tax_1 = 0.00
                                                                                                                monto_tax_1 = float(monto_tax_1) ### pasamos a float
                                                                                                                impuesto_principal_2 = line[128:130] ### al principio lo llame impuesto principal pero ya leugo lo arregle
                                                                                                                monto_tax_2 = line[121:128]
                                                                                                                monto_tax_2 = monto_tax_2.strip()
                                                                                                                if monto_tax_2 == "":  ### si no ay monto es 0
                                                                                                                                monto_tax_2 = 0.00
                                                                                                                monto_tax_2 = float(monto_tax_2)   ### pasamos a float
                                                                                                                monto_de_otros_TAX = line[131:139]  ### estos son los impuestos totales sin los principales
                                                                                                                total_CMAS =  line[144:152]  ### total segun el archivo
                                                                                                                total_CMAS =  total_CMAS.strip() ### total segun el archivo sin espacios
                                                                                                                if "NO ADC" in total_CMAS: ### este tipo de condicionales es por los errores de foramteo en los archivos
                                                                                                                                total_CMAS = 0.00
                                                                                                                total_CMAS = float(total_CMAS)  ### pasamos a float
                                                                                                                monto_de_otros_TAX = monto_de_otros_TAX.strip()
                                                                                                                if monto_de_otros_TAX == "":   ### si no ay monto es 0
                                                                                                                                monto_de_otros_TAX = 0.00
                                                                                                                elif monto_de_otros_TAX[0] == "D": ### este tipo de condicionales es por los errores de foramteo en los archivos
                                                                                                                                monto_de_otros_TAX = monto_de_otros_TAX[1:]
                                                                                                                                monto_de_otros_TAX = monto_de_otros_TAX.strip()
                                                                                                                monto_de_otros_TAX = float(monto_de_otros_TAX)
                                                                                                                if '6A'  in impuesto_principal_1: ### aqui comenzamos a agregar el impuesto extraido segun sea el que corresponda igual para los elif
                                                                                                                                monto_6A = monto_tax_1
                                                                                                                                lista_monto_6A.append(monto_6A) ### lo metemos en una lsita para saltarnos posibles errores y sumar al final, recuerda que este es el impuesto toal sin los principales
                                                                                                                elif 'AJ'  in impuesto_principal_1:
                                                                                                                                monto_AJ = monto_tax_1
                                                                                                                                lista_monto_AJ.append(monto_AJ)
                                                                                                                elif impuesto_principal_1 == 'AK':
                                                                                                                                monto_AJ = monto_tax_1
                                                                                                                                lista_monto_AK.append(monto_AJ)
                                                                                                                elif impuesto_principal_1 == 'AY':
                                                                                                                                monto_AY = monto_tax_1
                                                                                                                                lista_monto_AY.append(monto_AY)
                                                                                                                elif impuesto_principal_1 == 'US':
                                                                                                                                monto_US = monto_tax_1
                                                                                                                                lista_monto_US.append(monto_US)
                                                                                                                elif 'EU'  in impuesto_principal_1:
                                                                                                                                monto_EU = monto_tax_1
                                                                                                                                lista_monto_EU.append(monto_EU)
                                                                                                                elif impuesto_principal_1 == 'VJ':
                                                                                                                                monto_VJ = monto_tax_1
                                                                                                                                lista_monto_VJ.append(monto_VJ)                
                                                                                                                elif impuesto_principal_1 == 'XA':
                                                                                                                                monto_XA = monto_tax_1
                                                                                                                                lista_monto_XA.append(monto_XA)
                                                                                                                elif impuesto_principal_1 == 'XY':
                                                                                                                                monto_XY = monto_tax_1
                                                                                                                                lista_monto_XY.append(monto_XY)
                                                                                                                elif impuesto_principal_1 == 'YC':
                                                                                                                                monto_YC = monto_tax_1
                                                                                                                                lista_monto_YC.append(monto_YC)
                                                                                                                elif impuesto_principal_1 == 'XF':
                                                                                                                                monto_XF = monto_tax_1
                                                                                                                                lista_monto_XF.append(monto_XF)
                                                                                                                elif 'YQ'  in impuesto_principal_1:
                                                                                                                                monto_YQ = monto_tax_1
                                                                                                                                lista_monto_YQ.append(monto_YQ)
                                                                                                                elif impuesto_principal_1 == 'YN':
                                                                                                                                monto_YN = monto_tax_1
                                                                                                                                lista_monto_YN.append(monto_YN)
                                                                                                                elif impuesto_principal_1 == 'QC':
                                                                                                                                monto_QC = monto_tax_1
                                                                                                                                lista_monto_QC.append(monto_QC)
                                                                                                                elif impuesto_principal_1 == 'Y1C':
                                                                                                                                monto_Y1C = monto_tax_1
                                                                                                                                lista_monto_YC.append(monto_Y1C)
                                                                                                                elif impuesto_principal_1 == 'X1Y':
                                                                                                                                monto_X1Y = monto_tax_1
                                                                                                                                lista_monto_XY.append(monto_X1Y)



                                                                                                                if '6A'  in impuesto_principal_2: ### aqui comenzamos a agregar el impuesto extraido segun sea el que corresponda igual para los elif
                                                                                                                                monto_6A = monto_tax_2
                                                                                                                                lista_monto_6A.append(monto_6A) ### lo metemos en una lsita para saltarnos posibles errores y sumar al final, recuerda que este es el impuesto toal sin los principales
                                                                                                                elif 'AJ'  in impuesto_principal_2:
                                                                                                                                monto_AJ = monto_tax_2
                                                                                                                                lista_monto_AJ.append(monto_AJ)
                                                                                                                elif impuesto_principal_2 == 'AK':
                                                                                                                                monto_AJ = monto_tax_2
                                                                                                                                lista_monto_AK.append(monto_AJ)
                                                                                                                elif impuesto_principal_2 == 'AY':
                                                                                                                                monto_AY = monto_tax_2
                                                                                                                                lista_monto_AY.append(monto_AY)
                                                                                                                elif impuesto_principal_2 == 'US':
                                                                                                                                monto_US = monto_tax_2
                                                                                                                                lista_monto_US.append(monto_US)
                                                                                                                elif 'EU'  in impuesto_principal_2:
                                                                                                                                monto_EU = monto_tax_2
                                                                                                                                lista_monto_EU.append(monto_EU)
                                                                                                                elif impuesto_principal_2 == 'VJ':
                                                                                                                                monto_VJ = monto_tax_2
                                                                                                                                lista_monto_VJ.append(monto_VJ)                
                                                                                                                elif impuesto_principal_2 == 'XA':
                                                                                                                                monto_XA = monto_tax_2
                                                                                                                                lista_monto_XA.append(monto_XA)
                                                                                                                elif impuesto_principal_2 == 'XY':
                                                                                                                                monto_XY = monto_tax_2
                                                                                                                                lista_monto_XY.append(monto_XY)
                                                                                                                elif impuesto_principal_2 == 'YC':
                                                                                                                                monto_YC = monto_tax_2
                                                                                                                                lista_monto_YC.append(monto_YC)
                                                                                                                elif impuesto_principal_2 == 'XF':
                                                                                                                                monto_XF = monto_tax_2
                                                                                                                                lista_monto_XF.append(monto_XF)
                                                                                                                elif 'YQ'  in impuesto_principal_2:
                                                                                                                                monto_YQ = monto_tax_2
                                                                                                                                lista_monto_YQ.append(monto_YQ)
                                                                                                                elif impuesto_principal_2 == 'YN':
                                                                                                                                monto_YN = monto_tax_2
                                                                                                                                lista_monto_YN.append(monto_YN)
                                                                                                                elif impuesto_principal_2 == 'QC':
                                                                                                                                monto_QC = monto_tax_2
                                                                                                                                lista_monto_QC.append(monto_QC)
                                                                                                                elif impuesto_principal_2 == 'Y1C':
                                                                                                                                monto_Y1C = monto_tax_2
                                                                                                                                lista_monto_YC.append(monto_Y1C)
                                                                                                                elif impuesto_principal_2 == 'X1Y':
                                                                                                                                monto_X1Y = monto_tax_2
                                                                                                                                lista_monto_XY.append(monto_X1Y)
                                                                                                                concuerdan_lineas += 1
                                                                                                                
                                                                                                  elif "VE" == archivo_cmas_a_extraer[0:2] : ### antes hicimos para los que no eran de Venezuela aqui agregamos los de venezuela y sus cambios
                                                                                                                RUTA = line[20:29]
                                                                                                                moneda = line[86:89]
                                                                                                                monto_total_dolares = line[89:97]
                                                                                                                monto_equivfare_BS = line[100:108]
                                                                                                                monto_equivfare_BS = monto_equivfare_BS.strip()
                                                                                                                monto_en_moneda = line[100:106]
                                                                                                                monto_en_moneda = float(monto_en_moneda)
                                                                                                                total_VEF = line[141:156]
                                                                                                                total_CMAS = line[144:152]
                                                                                                                ### las variables igual que antes
                                                                                                                if "NO ADC" in total_CMAS: ### esto para evitar errores por mal formateo
                                                                                                                                total_CMAS = 0.00
                                                                                                                impuesto_principal_1 = line[109:120]
                                                                                                                impuesto_principal_2 = line[119:130]
                                                                                                                record_locator = line[7:14]
                                                                                                                monto_tax_1 = line[109:117]
                                                                                                                monto_tax_1 = monto_tax_1.strip()
                                                                                                                if monto_tax_1 == "": ### si no existe lo hacemos 0
                                                                                                                                monto_tax_1 = 0.00
                                                                                                                elif  "D" in monto_tax_1: ### esto para evitar errores por mal formateo lo hacemos 0
                                                                                                                                monto_tax_1 = 0.00
                                                                                                                elif  "PD" in monto_tax_1: ### esto para evitar errores por mal formateo lo hacemos 0
                                                                                                                                monto_tax_1 = 0.00        
                                                                                                                monto_tax_1 = float(monto_tax_1)
                                                                                                                monto_tax_2 = line[119:128]
                                                                                                                monto_tax_2 = monto_tax_2.strip()
                                                                                                                if monto_tax_2 == "": 
                                                                                                                                monto_tax_2 = 0.00
                                                                                                                elif  "D" in monto_tax_2:
                                                                                                                                monto_tax_2 = 0.00
                                                                                                                        
                                                                                                                elif  "PD" in monto_tax_2:
                                                                                                                                monto_tax_2 = 0.00  
                                                                                                                monto_tax_2 = float(monto_tax_2)
                                                                                                                
                                                                                                                if '6A'  in impuesto_principal_1:        ### aqui comenzamos a agregar el impuesto extraido segun sea el que corresponda igual para los elif
                                                                                                                                monto_6A = monto_tax_1
                                                                                                                                lista_monto_6A.append(monto_6A)          ### lo metemos en una lsita para saltarnos posibles errores y sumar al final, recuerda que este es el impuesto toal sin los principales
                                                                                                                elif 'AJ'  in impuesto_principal_1:
                                                                                                                                monto_AJ = monto_tax_1
                                                                                                                                lista_monto_AJ.append(monto_AJ)
                                                                                                                elif impuesto_principal_1 == 'AK':
                                                                                                                                monto_AJ = monto_tax_1
                                                                                                                                lista_monto_AK.append(monto_AJ)
                                                                                                                elif impuesto_principal_1 == 'AY':
                                                                                                                                monto_AY = monto_tax_1
                                                                                                                                lista_monto_AY.append(monto_AY)
                                                                                                                elif impuesto_principal_1 == 'US':
                                                                                                                                monto_US = monto_tax_1
                                                                                                                                lista_monto_US.append(monto_US)
                                                                                                                elif 'EU'  in impuesto_principal_1:
                                                                                                                                monto_EU = monto_tax_1
                                                                                                                                lista_monto_EU.append(monto_EU)
                                                                                                                elif impuesto_principal_1 == 'VJ':
                                                                                                                                monto_VJ = monto_tax_1
                                                                                                                                lista_monto_VJ.append(monto_VJ)                
                                                                                                                elif impuesto_principal_1 == 'XA':
                                                                                                                                monto_XA = monto_tax_1
                                                                                                                                lista_monto_XA.append(monto_XA)
                                                                                                                elif impuesto_principal_1 == 'XY':
                                                                                                                                monto_XY = monto_tax_1
                                                                                                                                lista_monto_XY.append(monto_XY)
                                                                                                                elif impuesto_principal_1 == 'YC':
                                                                                                                                monto_YC = monto_tax_1
                                                                                                                                lista_monto_YC.append(monto_YC)
                                                                                                                elif impuesto_principal_1 == 'XF':
                                                                                                                                monto_XF = monto_tax_1
                                                                                                                                lista_monto_XF.append(monto_XF)
                                                                                                                elif 'YQ'  in impuesto_principal_1:
                                                                                                                                monto_YQ = monto_tax_1
                                                                                                                                lista_monto_YQ.append(monto_YQ)
                                                                                                                elif impuesto_principal_1 == 'YN':
                                                                                                                                monto_YN = monto_tax_1
                                                                                                                                lista_monto_YN.append(monto_YN)
                                                                                                                elif impuesto_principal_1 == 'QC':
                                                                                                                                monto_QC = monto_tax_1
                                                                                                                                lista_monto_QC.append(monto_QC)
                                                                                                                elif impuesto_principal_1 == 'Y1C':
                                                                                                                                monto_Y1C = monto_tax_1
                                                                                                                                lista_monto_YC.append(monto_Y1C)
                                                                                                                elif impuesto_principal_1 == 'X1Y':
                                                                                                                                monto_X1Y = monto_tax_1
                                                                                                                                lista_monto_XY.append(monto_X1Y)
 
                                                                                                                if '6A'  in impuesto_principal_2:        ### aqui comenzamos a agregar el impuesto extraido segun sea el que corresponda igual para los elif
                                                                                                                                monto_6A = monto_tax_2
                                                                                                                                lista_monto_6A.append(monto_6A)          ### lo metemos en una lsita para saltarnos posibles errores y sumar al final, recuerda que este es el impuesto toal sin los principales
                                                                                                                elif 'AJ'  in impuesto_principal_2:
                                                                                                                                monto_AJ = monto_tax_2
                                                                                                                                lista_monto_AJ.append(monto_AJ)
                                                                                                                elif impuesto_principal_2 == 'AK':
                                                                                                                                monto_AJ = monto_tax_2
                                                                                                                                lista_monto_AK.append(monto_AJ)
                                                                                                                elif impuesto_principal_2 == 'AY':
                                                                                                                                monto_AY = monto_tax_2
                                                                                                                                lista_monto_AY.append(monto_AY)
                                                                                                                elif impuesto_principal_2 == 'US':
                                                                                                                                monto_US = monto_tax_2
                                                                                                                                lista_monto_US.append(monto_US)
                                                                                                                elif 'EU'  in impuesto_principal_2:
                                                                                                                                monto_EU = monto_tax_2
                                                                                                                                lista_monto_EU.append(monto_EU)
                                                                                                                elif impuesto_principal_2 == 'VJ':
                                                                                                                                monto_VJ = monto_tax_2
                                                                                                                                lista_monto_VJ.append(monto_VJ)                
                                                                                                                elif impuesto_principal_2 == 'XA':
                                                                                                                                monto_XA = monto_tax_2
                                                                                                                                lista_monto_XA.append(monto_XA)
                                                                                                                elif impuesto_principal_2 == 'XY':
                                                                                                                                monto_XY = monto_tax_2
                                                                                                                                lista_monto_XY.append(monto_XY)
                                                                                                                elif impuesto_principal_2 == 'YC':
                                                                                                                                monto_YC = monto_tax_2
                                                                                                                                lista_monto_YC.append(monto_YC)
                                                                                                                elif impuesto_principal_2 == 'XF':
                                                                                                                                monto_XF = monto_tax_2
                                                                                                                                lista_monto_XF.append(monto_XF)
                                                                                                                elif 'YQ'  in impuesto_principal_2:
                                                                                                                                monto_YQ = monto_tax_2
                                                                                                                                lista_monto_YQ.append(monto_YQ)
                                                                                                                elif impuesto_principal_2 == 'YN':
                                                                                                                                monto_YN = monto_tax_2
                                                                                                                                lista_monto_YN.append(monto_YN)
                                                                                                                elif impuesto_principal_2 == 'QC':
                                                                                                                                monto_QC = monto_tax_2
                                                                                                                                lista_monto_QC.append(monto_QC)
                                                                                                                elif impuesto_principal_2 == 'Y1C':
                                                                                                                                monto_Y1C = monto_tax_2
                                                                                                                                lista_monto_YC.append(monto_Y1C)
                                                                                                                elif impuesto_principal_2 == 'X1Y':
                                                                                                                                monto_X1Y = monto_tax_2
                                                                                                                                lista_monto_XY.append(monto_X1Y)
                                                                                                                monto_de_otros_TAX = line[130:139]
                                                                                                                monto_de_otros_TAX = monto_de_otros_TAX.strip()
                                                                                                                if monto_de_otros_TAX == "": ### si no existe es 0
                                                                                                                                monto_de_otros_TAX = 0.00
                                                                                                                elif  "D" in monto_de_otros_TAX: ### si hay errores lo hacemos 0
                                                                                                                                monto_de_otros_TAX = 0.00
                                                                                                                elif  "PD" in monto_de_otros_TAX:
                                                                                                                                monto_de_otros_TAX = 0.00        
                                                                                                                monto_de_otros_TAX = float(monto_de_otros_TAX)
                                                                                                                otros_tax_sumados = line[139:141]
                                                                                                                concuerdan_lineas += 1
                                                                                                                ###hasta aqui los datos de los impuestos de la linea que comeinza por 4
                                                                                  otros_tax = [] 
                                                                                  if line[0] == '7': ### aqui comienzan los impuestos de la linea que comienza por 4
                                                                                                  if line[94]== "1": ### esto es un problema del archivo recurrente este 1 siempre esta mal puesto en esta posicion
                                                                                                                  line = line[0:94]+line[95:]
                                                                                                  lista_impuestos = ['6A','AJ', 'AK', "AY", "US","EU", "VJ" , "XA","XY","YC","XF","YQ","YN", "QC" , "Y1C", "X1Y"]
                                                                                                  for impuestos_2 in lista_impuestos:  ### revisamos si cada impuesto esta en el archivo, si se necesitan impuestos nuevos hay que agregarlos en la lista y agregar un condicional con el impuesto
                                                                                                              if (impuestos_2 == impuesto_principal_1) or (impuestos_2 == impuesto_principal_2):  ### normalmente en condicones idelaes el impuesto principal no se repite, llamo principal a el de la linea 4
                                                                                                                                   print impuestos_2 
                                                                                                              else:
                                                                                                                  impuesto_sec = line.find(impuestos_2)  ### buscamos el  impuestos_2 en la linea
                                                                                                                  revisar = line[impuesto_sec+2]
                                                                                                                  if impuesto_sec !=-1:
                                                                                                                            if revisar == "D": ### Revisamos que sea la linea buscada un numero
                                                                                                                                 pass
                                                                                                                            else:
                                                                                                                                 impuesto = line[impuesto_sec:impuesto_sec+2]### Revisamos el tipo de impuesto encontrado
                                                                                                                                 ### Los siguientes if anidados pueden ser mejorados, los coloque para evitar algunos problemas en el largo de los montos
                                                                                                                                 if (line[impuesto_sec - 5]) == " ":
                                                                                                                                                  monto_tax = line[impuesto_sec-5:impuesto_sec]
                                                                                                                                 elif (line[impuesto_sec  - 6]) == " " :
                                                                                                                                                  monto_tax = line[impuesto_sec-6:impuesto_sec]
                                                                                                                                 elif (line[impuesto_sec  - 7]) == " ":
                                                                                                                                                  monto_tax = line[impuesto_sec-7:impuesto_sec]
                                                                                                                                 elif (line[impuesto_sec  - 8] ) == " ":
                                                                                                                                                  monto_tax =  line[impuesto_sec-8:impuesto_sec]
                                                                                                                                 elif (line[impuesto_sec  - 9]) == " ":
                                                                                                                                                  monto_tax = line[impuesto_sec-9:impuesto_sec]
                                                                                                                                 monto_tax = str(monto_tax) ## pasamos a string para poder usar strip
                                                                                                                                 monto_tax = monto_tax.strip()
                                                                                                                                 if monto_tax == "": ### si monto no tiene nada es 0
                                                                                                                                                 monto_tax = 0.00
                                                                                                                                 elif len(monto_tax)< 4:
                                                                                                                                                 pass
                                                                                                                                 elif monto_tax[-4] == ".":
                                                                                                                                                 if monto_tax[-3] == '1':  ### Eliminamos el molesto 1 del archivo mal formateado
                                                                                                                                                                 monto_tax =  monto_tax[0:-3]+monto_tax[-2:]
                                                                                                                                                 elif monto_tax[-2] == '1' and  monto_tax[-3] != '.' :
                                                                                                                                                                 monto_tax =  monto_tax[0:-2]+monto_tax[-1:]
                                                                                                                                 monto_tax = str(monto_tax)
                                                                                                                                 ### Los siguientes son if anidados para sortear una serie de errores o mal formateo de los archivos desde el codigo
                                                                                                                                 if monto_tax[0:2]== "PD":
                                                                                                                                               monto_tax= monto_tax[2:]  
                                                                                                                                 elif monto_tax[0:2]== "XT":
                                                                                                                                               monto_tax= monto_tax[2:]                                                                                                 
                                                                                                                                 elif monto_tax[0:3]== "1PD":
                                                                                                                                               monto_tax= monto_tax[3:]  
                                                                                                                                 elif monto_tax[0:3]== "P1D":
                                                                                                                                               monto_tax= monto_tax[3:]       
                                                                                                                                 elif monto_tax[0:3]== "P3D":
                                                                                                                                               monto_tax= monto_tax[3:]       
                                                                                                                                 elif monto_tax[0:3]== "3PD":
                                                                                                                                               monto_tax= monto_tax[3:]       
                                                                                                                                 elif "EQUIP" == monto_tax:
                                                                                                                                                 monto_tax = 0.00                       
                                                                                                                                 elif "KG\C" in monto_tax:
                                                                                                                                                 monto_tax = 0.00
                                                                                                                                 elif "X/AUA N" == monto_tax:
                                                                                                                                                 monto_tax = 0.00
                                                                                                                                 elif "KG\EQUIP" == monto_tax:
                                                                                                                                                 monto_tax = 0.00
                                                                                                                                 elif "KG\EUIQP" == monto_tax:
                                                                                                                                                 monto_tax = 0.00
                                                                                                                                 elif "PER KG" in monto_tax:
                                                                                                                                                 monto_tax = 0.00
                                                                                                                                 elif "KG" in monto_tax:
                                                                                                                                                 monto_tax = 0.00
                                                                                                                                 elif "N" == monto_tax[-1]:
                                                                                                                                                 monto_tax =monto_tax[0:-1]
                                                                                                                                 monto_tax = float(monto_tax)
                                                                                                                                 monto_tax = round(monto_tax,2)
                                                                                                                                 
                                                                                                                                 ### Aqui pasamos el monto a el impuesto relacionado y lo metemos en la lista
                                                                                                                                 if impuestos_2 == '6A':
                                                                                                                                                      monto_6A = monto_tax
                                                                                                                                                      lista_monto_6A.append(monto_6A)
                                                                                                                                 elif impuestos_2 == 'AJ':
                                                                                                                                                 monto_AJ = monto_tax
                                                                                                                                                 lista_monto_AJ.append(monto_tax)
                                                                                                                                 elif impuestos_2 == 'AK':
                                                                                                                                                 monto_AK = monto_tax
                                                                                                                                                 lista_monto_AK.append(monto_tax)
                                                                                                                                 elif impuestos_2 == 'AY':
                                                                                                                                                 monto_AY = monto_tax
                                                                                                                                                 lista_monto_AY.append(monto_tax)
                                                                                                                                 elif impuestos_2 == 'US':
                                                                                                                                                 monto_US = monto_tax
                                                                                                                                                 lista_monto_US.append(monto_tax)
                                                                                                                                 elif impuestos_2 == 'EU':
                                                                                                                                                 monto_EU = monto_tax
                                                                                                                                                 lista_monto_EU.append(monto_tax)
                                                                                                                                 elif impuestos_2 == 'VJ':
                                                                                                                                                 monto_VJ = monto_tax
                                                                                                                                                 lista_monto_VJ.append(monto_tax)
                                                                                                                                 elif impuestos_2 == 'XA':
                                                                                                                                                 monto_XA = monto_tax
                                                                                                                                                 lista_monto_XA.append(monto_tax)
                                                                                                                                 elif impuestos_2 == 'XY':
                                                                                                                                                 monto_XY = monto_tax
                                                                                                                                                 lista_monto_XY.append(monto_tax)
                                                                                                                                 elif impuestos_2 == 'YC':
                                                                                                                                                 monto_YC = monto_tax
                                                                                                                                                 lista_monto_YC.append(monto_tax)
                                                                                                                                 elif impuestos_2 == 'XF':
                                                                                                                                                 monto_XF = monto_tax
                                                                                                                                                 lista_monto_XF.append(monto_tax)
                                                                                                                                 elif impuestos_2 == 'YQ':
                                                                                                                                                 monto_YQ = monto_tax
                                                                                                                                                 lista_monto_YQ.append(monto_tax)
                                                                                                                                 elif impuestos_2 == 'YN':
                                                                                                                                                 monto_YN = monto_tax
                                                                                                                                                 lista_monto_YN.append(monto_tax)
                                                                                                                                 elif impuestos_2 == 'QC':
                                                                                                                                                 monto_QC = monto_tax
                                                                                                                                                 lista_monto_QC.append(monto_tax)
                                                                                                                                 elif 'Y1C' in impuestos_2:
                                                                                                                                                 monto_YC = monto_tax
                                                                                                                                                 lista_monto_YC.append(monto_tax)
                                                                                                                                 elif 'X1Y' in impuestos_2:
                                                                                                                                                 monto_XY = monto_tax
                                                                                                                                                 lista_monto_XY.append(monto_tax)
                                                                                                                                 otros_tax.append(monto_tax) ### Esta linea es importante para el total
                                                                                                  
                                                                                                  total_real =  monto_en_moneda + monto_tax_1 + monto_tax_2 + monto_de_otros_TAX ### Aqui sumamos para comparar y ver si estan bien los valores
                                                                                                  sumatoria_desglosados = sum(otros_tax) ### sumamos los otros impuestos
                                                                                                  if sumatoria_desglosados == 0:
                                                                                                                  sumatoria_desglosados = monto_de_otros_TAX ### ay pnrs que no tienen otros impuestos
                                                                                                  total_calculado =  monto_en_moneda + monto_tax_1 + monto_tax_2 + sumatoria_desglosados ### Aqui sumamos para comparar y ver si estan bien los valores
                                                                                                  total_real = round(total_real,2)
                                                                                                  total_calculado = round(total_calculado,2)
                                                                                                  if total_real != total_calculado:
                                                                                                                                  total_calculado2 =  monto_en_moneda + monto_tax_1 + monto_tax_2 + sumatoria_desglosados
                                                                                                                                  if cantidad_archivos != 0:
                                                                                                                                                        print cantidad_archivos
                                                                                                                                  cantidad_archivos  +=  1
                                                                                                                                  total_calculado = total_calculado2
                                                                                      
                                                                                  if line[0] == '5': ### EStas lineas no las computamos
                                                                                                 pass
                                                                                                 
                                                                                  if line[0] == '6': ### EStas lineas no las computamos
                                                                                                 pass
                                                                                                 
                                                                                  if line[0] == '8':### EStas lineas no las computamos
                                                                                                 pass
                                                                
                                                                                  if line[0] == '9':### EStas lineas no las computamos
                                                                                                 fecha_archivo = line[1:8]
                                                                                                 
                                                                                  if line[0] == 'K': ### AQui aprovechamos y sumamos todo, es como el final de cada pnr en la cinta
                                                                                                                pnr_localizador = line[100:]
                                                                                                                IssueCode = line[7:20]
                                                                                                                k_in_cmas = line[0:7]
                                                                                                                list_total_calculado_REAL.append(total_calculado)
                                                                                                                list_total_real_REAL.append(total_real)
                                                                                                                total_CMAS = float(total_CMAS)
                                                                                                                if (total_calculado > total_real) and (total_calculado - total_real < 1):
                                                                                                                                total_calculado = total_calculado - (total_calculado - total_real)
                                                                                                                if (total_calculado < total_real) and (total_real - total_calculado < 1):
                                                                                                                                total_calculado = total_calculado + (total_real - total_calculado)
                                                                                                                list_total_calculado_REAL.append(total_calculado)
                                                                                                                list_total_real_REAL.append(total_real)
                                                                                                                ### con este diccionario hacemos toda la magia
                                                                                                                dict__datos_pnr = {
                                
                                                                                                                                   'name': pnr_localizador,
                                                                                                                                  'sumatoria_desglosados': sumatoria_desglosados,
                                                                                                                                  'monto_de_otros_TAX': monto_de_otros_TAX,
                                                                                                                                  'monto_tax_2': monto_tax_2,
                                                                                                                                 'monto_tax_1': monto_tax_1,
                                                                                                                                  'monto_en_moneda': monto_en_moneda,
                                                                                                                                  'total_calculado': total_calculado,
                                                                                                                                  'total_real': total_real,
                                                                                                                                  'total_CMAS': total_CMAS,
                                                                                                                                  'tipo_pasajero': tipo_pasajero,
                                                                                                                                  'pasajero_principal': pasajero_principal,
                                                                                                                                  'monto_6A': sum(lista_monto_6A),
                                                                                                                                  'monto_AJ': sum(lista_monto_AJ),
                                                                                                                                  'monto_AK': sum(lista_monto_AK),
                                                                                                                                  'monto_AY': sum(lista_monto_AY),
                                                                                                                                  'monto_US': sum(lista_monto_US),
                                                                                                                                  'monto_EU': sum(lista_monto_EU),
                                                                                                                                  'monto_VJ': sum(lista_monto_VJ),
                                                                                                                                  'monto_XA': sum(lista_monto_XA),
                                                                                                                                  'monto_XY': sum(lista_monto_XY),
                                                                                                                                  'monto_YC': sum(lista_monto_YC),
                                                                                                                                  'monto_XF': sum(lista_monto_XF),
                                                                                                                                  'monto_YQ': sum(lista_monto_YQ),
                                                                                                                                  'monto_YN': sum(lista_monto_YN),
                                                                                                                                  'monto_QC': sum(lista_monto_QC),
                                                                                                                               }
                                                                                                                tupla_datos_pnr = (0, id, dict__datos_pnr) ### creamos una tupla para odoo
                                                                                                                lista_tuplas_pnrs.append(tupla_datos_pnr) ### la agregamos a una lsita de tuplas es un one2many
                                                                                                                numeros_K += 1
                                                               
                                                                                  if line[0] == 'Z':
                                                                                            ### aqui ya vaciamos los datos en ODOO
                                                                                            ### numeros_K se refiere a los archivos pnr en la cinta si no ay no hacemos nada
                                                                                            if numeros_K > 0:
                                                                                                            ### Buscamos por nombre
                                                                                                  buscar_cmas = self.pool.get('kiu').search(cr,uid,[('name', '=', archivo_cmas_a_extraer),],context=context)
                                                                                                            ### si existe lo movemos
                                                                                                  if buscar_cmas:
                                                                                                                  #subprocess.call(['mv', arch_a_extraerle_datos, '/home/odoo/archivos_kiu/archivos_procesados/'])
                                                                                                                  ruta = 'mv '+ arch_a_extraerle_datos + ' '+ ruta_de_usuario +'archivos_procesados/'
                                                                                                                  ps = subprocess.Popen(ruta,shell=True) ### Ejecutar la linea anterior
                                                                                                 ### si no existe lo creamos
                                                                                                  else:                                                                                                                  
                                                                                                                  total_real_REAL = sum(list_total_real_REAL)
                                                                                                                  total_calculado_REAL = sum(list_total_calculado_REAL)
                                                                                                                  total_real_REAL = float(total_real_REAL)
                                                                                                                  total_calculado_REAL = float(total_calculado_REAL)
                                                                                                                  class_cmas_obj.create(cr,uid, {
                                                                                                                                         'name': archivo_cmas_a_extraer,
                                                                                                                                          'nombres': archivo_cmas_a_extraer,
                                                                                                                                          'fecha_archivo': fecha_archivo,
                                                                                                                                           'pnr_ids': lista_tuplas_pnrs,
                                                                                                                                            'total_calculado_REAL': total_calculado_REAL,
                                                                                                                                             'total_real_REAL': total_real_REAL,
                                                                                                                              }) 
                                                                                                                  ### lo movemos a el directorio de procesados
                                                                                                                  #subprocess.call(['mv', arch_a_extraerle_datos, '/home/odoo/archivos_kiu/CRS_correctamente_procesado'])
                                                                                                                  ruta = 'mv '+ arch_a_extraerle_datos + ' '+ ruta_de_usuario +'CRS_correctamente_procesado'
                                                                                                                  ps = subprocess.Popen(ruta,shell=True) ### Ejecutar la linea anterior
                                                                                                  continue
                                                                                            ###  si no ay movemos a archivos en 0
                                                                                            else:
                                                                                                            #subprocess.call(['mv', arch_a_extraerle_datos, '/home/odoo/archivos_kiu/archivos_en_0/'])
                                                                                                            ruta = 'mv '+ arch_a_extraerle_datos +  ' '+ ruta_de_usuario +'archivos_en_0'
                                                                                                            ps = subprocess.Popen(ruta,shell=True) ### Ejecutar la linea anterior
                                                                                                            
                    return True
### Informacion Importante Creando los campos ODOO
    name = fields.Char('Nombre de Archivo')
    fecha_archivo = fields.Char('Fecha del Archivo')
    numero_tkt = fields.Char('Numero de TKT')
    pnr_localizador = fields.Char('pnr_localizador')
    IssueCode = fields.Char('IssueCode')
    k_in_cmas = fields.Char('k_in_cmas')
    tipo_pasajero = fields.Char('tipo_pasajero')
    numero_pnr = fields.Char('numero_pnr')
    numero_Boleto = fields.Char('numero_Boleto')
    motivo_facturacion_codigo = fields.Char('motivo_facturacion_codigo')
    pasajero_principal = fields.Char('pasajero_principal')
    code_emisor = fields.Char('code_emisor')
    numero_motivos = fields.Char('numero_motivos')
    total_calculado_REAL  =  fields.Float('total_calculado', digits=(32, 2))
    total_real_REAL =  fields.Float('total_real', digits=(32, 2))
    pnr_ids = fields.One2many('info_kiu','asociar_pnr_id')

kiu()

class info_kiu(models.Model):
    _name = "info_kiu"
### Informacion Importante Creando los campos ODOO
    name = fields.Char('Nombre')
    nombres= fields.Char('Nombres',size=64 )
    numero_Boleto= fields.Char('numero_Boleto',size=64 )
    pasajero_principal = fields.Char('pasajero_principal',size=64 )
    tipo_pasajero = fields.Char('tipo_pasajero',size=64 )
    asociar_pnr_id = fields.Many2one('kiu', required=False)
    #Impuestos Desglosados
    tax_6A  =  fields.Char('tax_6A')
    monto_6A  =  fields.Float('monto_6A', digits=(32, 2))
    tax_AJ  =  fields.Char('tax_AJ')
    monto_AJ  =  fields.Float('monto_AJ', digits=(32, 2))
    tax_AK  =  fields.Char('tax_AK')
    monto_AK  =  fields.Float('monto_AK', digits=(32, 2))
    tax_AY  =  fields.Char('tax_AY')
    monto_AY  =  fields.Float('monto_AY', digits=(32, 2))
    tax_US  =  fields.Char('tax_US')
    monto_US  =  fields.Float('monto_US', digits=(32, 2))
    tax_EU  =  fields.Char('tax_EU')
    monto_EU  =  fields.Float('monto_EU', digits=(32, 2))
    tax_VJ  =  fields.Char('tax_VJ')
    monto_VJ  =  fields.Float('monto_VJ', digits=(32, 2))
    tax_XA  =  fields.Char('tax_XA')
    monto_XA  =  fields.Float('monto_XA', digits=(32, 2))
    tax_XY  =  fields.Char('tax_XY')
    monto_XY  =  fields.Float('monto_XY', digits=(32, 2))
    tax_YC  =  fields.Char('tax_YC')
    monto_YC  =  fields.Float('monto_YC', digits=(32, 2))
    tax_XF  =  fields.Char('tax_XF')
    monto_XF  =  fields.Float('monto_XF', digits=(32, 2))
    tax_YQ  =  fields.Char('tax_YQ')
    monto_YQ  =  fields.Float('monto_YQ', digits=(32, 2))
    tax_YN  =  fields.Char('tax_YN')
    monto_YN  =  fields.Float('monto_YN', digits=(32, 2))
    tax_QC  =  fields.Char('tax_QC')
    monto_QC  =  fields.Float('monto_QC', digits=(32, 2))
    tax_Y1C  =  fields.Char('tax_Y1C')
    monto_Y1C  =  fields.Float('monto_Y1C', digits=(32, 2))
    tax_X1Y  =  fields.Char('tax_X1Y')
    monto_X1Y  =  fields.Float('monto_X1Y', digits=(32, 2))
    #Montos
    sumatoria_desglosados  =  fields.Float('sumatoria_desglosados', digits=(32, 2))
    monto_de_otros_TAX  =  fields.Float('monto_de_otros_TAX', digits=(32, 2))
    total_calculado  =  fields.Float('total_calculado', digits=(32, 2))
    total_real  =  fields.Float('total_real', digits=(32, 2))
    total_CMAS  =  fields.Float('total_CMAS', digits=(32, 2))
    monto_tax_2  =  fields.Float('monto_tax_2', digits=(32, 2))
    monto_tax_1  =  fields.Float('monto_tax_1', digits=(32, 2))
    monto_en_moneda  =  fields.Float('monto_en_moneda', digits=(32, 2))
info_kiu()


class intermedio_kiu(models.Model):
    _name = "intermedio_kiu"
    
    ### creamos un intermedio antes de la PreFactura, para dejar que el usuario cambie los montos si no estan bien
    def create_intermedio_kiu(self, cr, uid, context=None):
        account_Boletos_search = self.pool.get('info_kiu').search(cr, uid, [])   
        account_Boletos_obj = self.pool.get('info_kiu') 
        nro_iteracion = 0
        ### mapeamos la Base de Datos en busca de todos los boletos que estan en ella account_Boletos_search es una lista
        for boleto_id in account_Boletos_search: 
                 #if nro_iteracion < 3: ### Esto es para pruebas
                 
                        boleto_id =account_Boletos_obj.browse(cr, uid,boleto_id ,context=context) #Buscamos en ID del Boleto, para pivotear en el registro
                        if (boleto_id.total_calculado == 0.00) and (boleto_id.total_real == 0.00): ### si son iguales a 0 no hacemos nada
                                        continue
                        if boleto_id.total_calculado == boleto_id.total_real: ### si no son iguales no hacemos la prefactura
                                        ### no ay mucho q explciar en estas variables que creamos
                                 class_factura = self.pool.get('account.invoice') 
                                 class_product = self.pool.get('product.template')
                                 class_tax = self.pool.get('account.tax')
                                 class_tax_ids = self.pool.get('account.invoice.tax_line_ids')
                                 valores_invoice = {}
                                 lista_tuplas_pasajes_inv = []
                                 nombre_producto = boleto_id.name
                                 monto_en_moneda = boleto_id.monto_en_moneda
                                 if class_product.search(cr,uid,[('name', '=', nombre_producto),],context=context): ### si existe no hacemos nada
                                                 continue
                                 else: ### si no existe  hacemos
                                        BB = boleto_id ### para hacerlo mas corto el nombre
                                        ### creamos la lista de los campos
                                        lista_taxes_nombres = [
                                                        'amount_YQ', 
                                                         'amount_YC',
                                                         'amount_US ', 
                                                         'amount_XA ',
                                                         'amount_XY',
                                                         'amount_VJ',
                                                         'amount_EU',
                                                         'amount_XF',
                                                         'amount_AY',
                                                         'amount_AJ',
                                                         'amount_YN',
                                                         'amount_AK',
                                                         'amount_QC '
                                                         'amount_6A '
                                                         ]
                                        iterar_taxes = 0
                                        tax_ids = []
                                        diccionario_tax = {}
                                        lista111 =[]
                                        lista_tuplas_itinerario =[]
                                        ### entramos en la lista para agregar los datos donde van
                                        for tax_name in lista_taxes_nombres:
                                                        ### no hay mucho que explicar
                                                        amount_YQ = BB.monto_YQ
                                                        amount_YC = BB.monto_YC
                                                        amount_US = BB.monto_US
                                                        amount_XA = BB.monto_XA
                                                        amount_XY = BB.monto_XY
                                                        amount_VJ = BB.monto_VJ
                                                        amount_EU = BB.monto_EU
                                                        amount_XF = BB.monto_XF
                                                        amount_AY = BB.monto_AY
                                                        amount_AJ = BB.monto_AJ
                                                        amount_YN = BB.monto_YN
                                                        amount_AK = BB.monto_AK
                                                        amount_QC = BB.monto_QC
                                                        amount_6A = BB.monto_6A
                                                        ### tomamos como pivote iterar_taxes para agregar los impuestos en la fctura
                                                        if iterar_taxes == 0:
                                                                  if amount_YQ == 0: ### si es 0 no hacemos nada, podiamos colocar passs pero prefiero los print
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                                  
                                                                                  ### datos para agregar al diccionario de tax que es de tipo many2many
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_YQ)
                                                                        name_tax = tax_name
                                                                        ### si la cuenta no existe se debe crear
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '251101'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount_YQ,
                                                                                      }
                                                                        #esta es la tupla y la lsita de tuplas las otras son exactamente iguales
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                        elif iterar_taxes == 1:
                                                                  if amount_YC == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_YC)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '251201'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                                   
                                                        elif iterar_taxes == 2:
                                                                  if amount_US == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_US)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '251301'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                        elif iterar_taxes == 3:
                                                                  if amount_XA == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_XA)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2514'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                        
                                                        elif iterar_taxes == 4:
                                                                  if amount_XY == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_XY)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2515'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                                         
                                                        elif iterar_taxes == 5:
                                                                  if amount_VJ == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_VJ)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2517'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                                       
                                                        elif iterar_taxes == 6:
                                                                  if amount_EU == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_EU)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2518'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                        
                                                        elif iterar_taxes == 7:
                                                                  if amount_XF == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_XF)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2520'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                        elif iterar_taxes == 8:
                                                                  if amount_AY == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_AY)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2521'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                        
                                                        elif iterar_taxes == 9:
                                                                  if amount_AJ == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_AJ)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2522'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                        elif iterar_taxes == 10:
                                                                  if amount_YN == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        print "iterar_taxes" , "amount_YN"
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_YN)
                                                                        name_tax = tax_name
                                                                        print name_tax
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2523'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                                     
                                                        elif iterar_taxes == 11:
                                                                  if amount_AK == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_AK)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2524'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                                                 
                                                        elif iterar_taxes == 12:
                                                                  if amount_QC == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000  #########       QQQQQCCCCCCCCCCCCCCCC  #########"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_QC)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2525'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                                                         
                                                        elif iterar_taxes == 13:
                                                                  if amount_6A == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000  #########       QQQQQCCCCCCCCCCCCCCCC  #########"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_6A)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2525'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                       ## Si el impuesto existe sobreescribimos el amount                 
                                                        class_tax = self.pool.get('account.tax')  
                                                        buscar_tax = self.pool.get('account.tax').search(cr,uid,[('name', '=', name_tax),],context=context)
                                                        if buscar_tax:
                                                                        id_tax_a_cambiar = buscar_tax[0]
                                                                        tax_idssss = class_tax.write(cr, 1, [id_tax_a_cambiar], {'amount': amount})
                                                       ## Si el impuesto no existe lo creamos                 
                                                        else:
                                                                        tax_idssss = class_tax.create(cr,uid, diccionario_tax)
                                                                        buscar_tax = self.pool.get('account.tax').search(cr,uid,[('name', '=', name_tax),],context=context)
                                                                        id_tax_a_cambiar = buscar_tax[0]
                                                        iterar_taxes += 1
                                         ### Creamos el producto                              
                                        class_product = self.pool.get('product.product')
                                        class_product.create(cr,uid, {'name': nombre_producto, 'list_price': monto_en_moneda , 'type':'service'  , 'taxes_id' : [(6, 0, lista111)], 'supplier_taxes_id' : [(6, 0, lista111)] })
                                        clase_producto = self.pool.get('product.product').search(cr,uid,[('name', '=', nombre_producto),],context=context)
                                        id_producto = clase_producto[0]
                                        ### PARTNER
                                        ### Agregamos el partner a la factura
                                        nombre_partner  =   boleto_id.pasajero_principal
                                        tipo_pasajero  =   boleto_id.tipo_pasajero                                    
                                        class_obj_partner = self.pool.get('res.partner')
                                        clase_res_partner = self.pool.get('res.partner').search(cr,uid,[('name', '=', nombre_partner),],context=context)
                                        data6 = {
                                                         'name' : nombre_partner
                                               }
                                        ### Si existe el partner sacamos el id
                                        if clase_res_partner:
                                                     id_cliente = clase_res_partner[0]
                                        ### Si no existe el partner lo creamos
                                        else:
                                                     class_obj_partner.create(cr,uid, data6)
                                                     clase_res_partner = self.pool.get('res.partner').search(cr,uid,[('name', '=', nombre_partner),],context=context)
                                                     id_cliente = clase_res_partner[0]
                                        ### Agregamos otros datos de la factura
                                        buscar_code = self.pool.get('account.account').search(cr,uid,[('code', '=', '101200'),],context=context)
                                        account_id = buscar_code[0]
                                        valores_invoice["partner_id"] = id_cliente
                                        valores_invoice["name"] = nombre_producto
                                        valores_invoice["journal_id"] = '1'
                                        valores_invoice["account_id"] = account_id
                                        nro_tax = len(lista_tuplas_itinerario)
                                        if nro_tax == 0:
                                                        pass
                                        elif nro_tax >= 1:
                                                        valores_invoice["tax_line_ids"] = lista_tuplas_itinerario
                                        ### Aqui ya creamos la Factura
                                        invoice_id = class_factura.create(cr,uid, valores_invoice)
                                        self.pool.get('account.invoice.line').create(cr, uid,{
                                                                   'invoice_id' : invoice_id,
                                                                   'name' : nombre_producto,
                                                                   'product_id' : id_producto,
                                                                   'price_unit':  monto_en_moneda,
                                                                   'account_id':  account_id,
                                                                    'invoice_line_tax_eds' : (6, id , lista_tuplas_itinerario ) ,
                                                                    })
                                        
                                        ### Le pasamos algunos metodos a la factura para validarla de ser necesario
                                        inv_obj = self.pool.get('account.invoice')
                                        inv_obj.action_date_assign(cr, uid, invoice_id, context=context)
                                        inv_obj.action_move_create(cr, uid, invoice_id, context=context)
                                        inv_obj.invoice_validate(cr, uid, invoice_id, context=context)
                                        invoice_ids = [(4,[invoice_id])]
                                        amount = BB.total_real
                                        journal_search = self.pool.get('account.journal').search(cr,uid,[('name', '=', 'Cash'),],context=context)
                                        journal_id = journal_search[0]
                                        nro_iteracion += 1
                                        
       ### Aqui agregamos los campos
    
    name = fields.Char('Nombre')
    nombres= fields.Char('Nombres',size=64 )                                                               
    tipo_pasajero= fields.Char('tipo_pasajero',size=64 )
    pasajero= fields.Char('pasajero',size=64 )
    #Impuestos Desglosados
    amount_YQ  =  fields.Float('amount_YQ', digits=(32, 2))
    amount_YC  =  fields.Float('amount_YC', digits=(32, 2))
    amount_US  =  fields.Float('amount_US', digits=(32, 2))
    amount_XA  =  fields.Float('amount_XA', digits=(32, 2))
    amount_XY  =  fields.Float('amount_XY', digits=(32, 2))
    amount_AW  =  fields.Float('amount_AW', digits=(32, 2))
    amount_VJ  =  fields.Float('amount_VJ', digits=(32, 2))
    amount_EU  =  fields.Float('amount_EU', digits=(32, 2))
    amount_YR  =  fields.Float('amount_YR', digits=(32, 2))
    amount_XF  =  fields.Float('amount_XF', digits=(32, 2))
    amount_AY  =  fields.Float('amount_AY', digits=(32, 2))
    amount_AJ  =  fields.Float('amount_AJ', digits=(32, 2))
    amount_YN  =  fields.Float('amount_YN', digits=(32, 2))
    amount_AK  =  fields.Float('amount_AK', digits=(32, 2))
    amount_QC  =  fields.Float('amount_QC', digits=(32, 2))
    numero_Boleto = fields.Char('numero_Boleto')
    #Montos
    sumatoria_desglosados  =  fields.Float('sumatoria_desglosados', digits=(32, 2))
    monto_de_otros_TAX  =  fields.Float('monto_de_otros_TAX', digits=(32, 2))
    total_calculado  =  fields.Float('total_calculado', digits=(32, 2))
    total_real  =  fields.Float('total_real', digits=(32, 2))
    total_CAT  =  fields.Float('total_CAT', digits=(32, 2))
    monto_tax_2  =  fields.Float('monto_tax_2', digits=(32, 2))
    monto_tax_1  =  fields.Float('monto_tax_1', digits=(32, 2))
    monto_en_moneda  =  fields.Float('monto_en_moneda', digits=(32, 2))

intermedio_kiu()


### REpetimos el Proceso para las cintas cat
class cintas_cat(models.Model):
    _name = "cintas_cat"
    ###  Este codigo para mi esta mejor seria bueno modificar el de arriba y hacerlo aprecido a este
    def create_cat(self, cr, uid, context=None):
                    ### creamos una lsita de los archivos en CAT_descomprimidos
                    #os.system("ls /home/odoo/archivos_kiu/CAT_descomprimidos  > /home/odoo/archivos_kiu/CAT_descomprimidos.txt")
                    
                    ruta = "ls " +ruta_de_usuario +'CAT_descomprimidos'+ ' > ' + ruta_de_usuario +'CAT_descomprimidos.txt' ### ruta a ejecutar como si de la shell se trata
                    ps = subprocess.Popen(ruta,shell=True) ### Ejecutar la linea anterior
                    
                    
                    
                    archivo_CAT =ruta_de_usuario+'/CAT_descomprimidos.txt' ### le damos un nombre a el archiv que hemos creado para odoo
                    archi_CAT = open(archivo_CAT,'r') ### lo abrimos
                    ### creamos variables
                    class_cat_obj = self.pool.get('cintas_cat') 
                    class_boletos_cat = self.pool.get('info_cintas_cat') 
                    class_PNR_en_CAT = self.pool.get('cintas_cat') 
                    ### leemos la lista archi_CAT 1 a 1
                    for archivo_cat_a_extraer in archi_CAT:
                                    arch_a_extraerle_datos = ruta_de_usuario+'/CAT_descomprimidos/'+archivo_cat_a_extraer ## nombramos el archivo a leer
                                    arch_a_extraerle_datos = arch_a_extraerle_datos.strip() ### le quitamos los espacios en blanco a ambos lados
                                    if archivo_cat_a_extraer: ## si existe
                                                                    archivo = arch_a_extraerle_datos ### lo abrimos y lo leemos
                                                                    reader= open(archivo, 'r')
                                                                    cantidad_archivos  =  0
                                                                    list_total_calculado_REAL = []
                                                                    list_total_real_REAL = []
                                                                    lista_tuplas_boleto = []
                                                                    numeros_K = 0
                                                                    for line in reader: 
                                                                                    ### lo leemos linea a linea
                                                                                  if line[0:3] == 'TTH': ### REcuerda que los inicios de cada linea tienen un tipo distinto para referirse a algo en especifico del archivo
                                                                                                  pass
                                                                                  if line[0:3] == 'TKT':
                                                                                                  ### Aqui creamos la lista ya que no se repite hasta que se entre en otro archivo
                                                                                                  lista_amount_taxes = []
                                                                                                  lista_amount_taxes_con_con = []
                                                                                                  lista_amount_sin_replace = []
                                                                                                  lista_taxes = []
                                                                                                  lista_total_real = []
                                                                                                  lista_amount_YQ = []
                                                                                                  lista_amount_YC = []
                                                                                                  lista_amount_US = []
                                                                                                  lista_amount_XA = []
                                                                                                  lista_amount_XY = []
                                                                                                  lista_amount_AW = []
                                                                                                  lista_amount_VJ = []
                                                                                                  lista_amount_EU = []
                                                                                                  lista_amount_YR = []
                                                                                                  lista_amount_XF = []
                                                                                                  lista_amount_AY = []
                                                                                                  lista_amount_AJ = []
                                                                                                  lista_amount_YN = []
                                                                                                  lista_amount_AK = []
                                                                                                  lista_amount_QC = []
                                                                                                  amount_amount = 0
                                                                                  if line[0:3] == 'TOH':
                                                                                                  ### si ay un pass no necesitamos esta linea por ahora
                                                                                                  pass
                                                                                  if line[0:3] == 'TKS':
                                                                                                  ### no hay mucho que comentar, la lectura de los archivos no es tan divertida ni logica
                                                                                                  if line[41:44] == "001":
                                                                                                                  pasajero = line[44:84]
                                                                                                                  pasajero = pasajero.strip() 
                                                                                                                  if pasajero[-3:] == "CHD":
                                                                                                                                  tipo_pasajero = "CHD"
                                                                                                                                  pasajero = pasajero.replace("CHD"," ")
                                                                                                                  else: 
                                                                                                                                  tipo_pasajero = 'NON'
                                                                                                                  pasajero = pasajero.strip()                
                                                                                                  lista_impuestos = ['YQ ', 'YC ',"US  ","XA ", "XY " , "AW ","VJ ","EU ","YR ","XF ","AY  ", "AJ " , "YN ", "AK ", "QC "] ### creamos la lista de impuestos
                                                                                                  for impuesto in lista_impuestos:
                                                                                                                  ### buscamos los impuestos en la linea, si necesitamos agregar nuevos impuestos debemos agregar el impuesto a la lista por eso hable de que este codigo es mas flexible :D
                                                                                                                  search_tax = line.find(impuesto)
                                                                                                                  search_tax_83 = line[83:85]
                                                                                                                  search_tax_83 = search_tax_83+" "
                                                                                                                  #Ya que US tambien es USD debemos hacer unos artificios logicos apra leer bien el archivo 
                                                                                                                  if  "US " == search_tax_83:
                                                                                                                                  search_tax_83 = "US "+" "
                                                                                                                  if  "AY " == search_tax_83:
                                                                                                                                  search_tax_83 = "AY "+" "
                                                                                                                  search_tax_64 = line[64:66]
                                                                                                                  search_tax_64 = search_tax_64+" "
                                                                                                                  if  "US " == search_tax_64:
                                                                                                                                  search_tax_64 = "US "+" "
                                                                                                                  if  "AY " == search_tax_64:
                                                                                                                                  search_tax_64 = "AY "+" "
                                                                                                                  ### Por experiencia el impuesto esta en [83:85] y [64:66] de la linea 
                                                                                                                  ### Si es diferente a -1 procedemos a extraer el amount
                                                                                                                  if search_tax_83 != -1 or search_tax_64 != -1:
                                                                                                                                  ### las variables no necesitan muchos comentarios
                                                                                                                                  tipo_tax = line[search_tax:search_tax+2]
                                                                                                                                  amount_tax = line[search_tax+2:search_tax+19]
                                                                                                                                  amount_tax_con_con =  line[search_tax+2:search_tax+19]
                                                                                                                                  ### EStos archivos tienen unas letras parecidas a HExadecimal por lo que hay que remplazar la letra por un numero para pasarlo a Float
                                                                                                                                  amount_tax = amount_tax.replace('E', '5')
                                                                                                                                  amount_tax = amount_tax.replace('F', '6')
                                                                                                                                  amount_tax = amount_tax.replace('{', '0') 
                                                                                                                                  ###PUEDE SER, quiere decir que no hay segurdidad se debe comparar con boletos que nunca me dieron si no 2 nada mas
                                                                                                                                  amount_tax = amount_tax.replace('D', '4') 
                                                                                                                                  amount_tax = amount_tax.replace('A', '1') 
                                                                                                                                  ### Corregir, lo mismo que arriba
                                                                                                                                  amount_tax = amount_tax.replace('I', '2') 
                                                                                                                                  amount_tax = amount_tax.replace('G', '8') 
                                                                                                                                  amount_tax = amount_tax.replace('C', '1') 
                                                                                                                                  amount_tax = amount_tax.replace('H', '3') 
                                                                                                                                  amount_tax = amount_tax[-5:-2]+'.'+amount_tax[-2:]
                                                                                                                                  if amount_tax[-1] == "A" or amount_tax[-1] == "B": ### Otro artificio
                                                                                                                                                  amount_tax = amount_tax[0:-1]
                                                                                                                                  amount_tax = float(amount_tax) * 1.0000
                                                                                                                  if search_tax_83 == impuesto: ### Aqui tenemos 2 escenarios el tax de line[83:85] y line[64:66], y procedemos a asignar segun el caso
                                                                                                                                  lista_amount_taxes_con_con.append(amount_tax_con_con) ### Comenzamos llenando la lista_amount_taxes_con_con
                                                                                                                                  lista_amount_taxes.append(amount_tax) ### Comenzamos llenando la lista_amount_taxes, usaremos esta la de arriba es para ver las letras que corregimos arriba
                                                                                                                                  ### Ahora simplemente verificams en que impuesto estamos y lo asignamos a la lista que pertenece
                                                                                                                                  if impuesto == 'YQ ':
                                                                                                                                                  amount_YQ = amount_tax
                                                                                                                                                  lista_amount_YQ.append(amount_tax)
                                                                                                                                  if impuesto == "QC ":
                                                                                                                                                  amount_QC = amount_tax
                                                                                                                                                  lista_amount_QC.append(amount_tax)
                                                                                                                                  elif impuesto == 'YC ':
                                                                                                                                                  amount_YC = amount_tax
                                                                                                                                                  lista_amount_YC.append(amount_tax)
                                                                                                                                  elif impuesto == 'US  ':
                                                                                                                                                  amount_US = amount_tax
                                                                                                                                                  lista_amount_US.append(amount_tax)
                                                                                                                                  elif impuesto == 'XA ':
                                                                                                                                                  amount_XA = amount_tax
                                                                                                                                                  lista_amount_XA.append(amount_tax)
                                                                                                                                  elif impuesto == 'XY ':
                                                                                                                                                  amount_XY = amount_tax
                                                                                                                                                  lista_amount_XY.append(amount_tax)
                                                                                                                                  elif impuesto == 'AW ':
                                                                                                                                                  amount_AW = amount_tax
                                                                                                                                                  lista_amount_AW.append(amount_tax)
                                                                                                                                  elif impuesto == 'VJ ':
                                                                                                                                                  amount_VJ = amount_tax
                                                                                                                                                  lista_amount_VJ.append(amount_tax)
                                                                                                                                  elif impuesto == 'EU ':
                                                                                                                                                  amount_EU = amount_tax
                                                                                                                                                  lista_amount_EU.append(amount_tax)
                                                                                                                                  elif impuesto == 'YR ':
                                                                                                                                                  amount_YR = amount_tax
                                                                                                                                                  lista_amount_YR.append(amount_tax)
                                                                                                                                  elif impuesto == 'XF ':
                                                                                                                                                  amount_XF = amount_tax
                                                                                                                                                  lista_amount_XF.append(amount_tax)
                                                                                                                                  elif impuesto == 'AY  ':
                                                                                                                                                  amount_AY = amount_tax
                                                                                                                                                  lista_amount_AY.append(amount_tax)
                                                                                                                                  elif impuesto == 'AJ ':
                                                                                                                                                  amount_AJ = amount_tax
                                                                                                                                                  lista_amount_AJ.append(amount_tax)
                                                                                                                                  elif impuesto == 'YN ':
                                                                                                                                                  amount_YN = amount_tax
                                                                                                                                                  lista_amount_YN.append(amount_tax)
                                                                                                                                  elif impuesto == 'AK ':
                                                                                                                                                  amount_AK = amount_tax
                                                                                                                                                  lista_amount_AK.append(amount_tax)
                                                                                                                                  elif impuesto == 'QC ':
                                                                                                                                                  amount_QC = amount_tax
                                                                                                                                                  lista_amount_QC.append(amount_tax)
                                                                                                                      ### Todo igual que arriba
                                                                                                                  if search_tax_64 == impuesto:
                                                                                                                                  lista_amount_taxes_con_con.append(amount_tax_con_con)
                                                                                                                                  lista_amount_taxes.append(amount_tax)
                                                                                                                                  lista_taxes.append(impuesto)
                                                                                                                                  if impuesto == 'YQ ':
                                                                                                                                                  amount_YQ = amount_tax
                                                                                                                                                  lista_amount_YQ.append(amount_tax)
                                                                                                                                  if impuesto == "QC ":
                                                                                                                                                  amount_QC = amount_tax
                                                                                                                                                  lista_amount_QC.append(amount_tax)
                                                                                                                                  elif impuesto == 'YC ':
                                                                                                                                                  amount_YC = amount_tax
                                                                                                                                                  lista_amount_YC.append(amount_tax)
                                                                                                                                  elif impuesto == 'US  ':
                                                                                                                                                  amount_US = amount_tax
                                                                                                                                                  lista_amount_US.append(amount_tax)
                                                                                                                                  elif impuesto == 'XA ':
                                                                                                                                                  amount_XA = amount_tax
                                                                                                                                                  lista_amount_XA.append(amount_tax)
                                                                                                                                  elif impuesto == 'XY ':
                                                                                                                                                  amount_XY = amount_tax
                                                                                                                                                  lista_amount_XY.append(amount_tax)
                                                                                                                                  elif impuesto == 'AW ':
                                                                                                                                                  amount_AW = amount_tax
                                                                                                                                                  lista_amount_AW.append(amount_tax)
                                                                                                                                  elif impuesto == 'VJ ':
                                                                                                                                                  amount_VJ = amount_tax
                                                                                                                                                  lista_amount_VJ.append(amount_tax)
                                                                                                                                  elif impuesto == 'EU ':
                                                                                                                                                  amount_EU = amount_tax
                                                                                                                                                  lista_amount_EU.append(amount_tax)
                                                                                                                                  elif impuesto == 'YR ':
                                                                                                                                                  amount_YR = amount_tax
                                                                                                                                                  lista_amount_YR.append(amount_tax)
                                                                                                                                  elif impuesto == 'XF ':
                                                                                                                                                  amount_XF = amount_tax
                                                                                                                                                  lista_amount_XF.append(amount_tax)
                                                                                                                                  elif impuesto == 'AY  ':
                                                                                                                                                  amount_AY = amount_tax
                                                                                                                                                  lista_amount_AY.append(amount_tax)
                                                                                                                                  elif impuesto == 'AJ ':
                                                                                                                                                  amount_AJ = amount_tax
                                                                                                                                                  lista_amount_AJ.append(amount_tax)
                                                                                                                                  elif impuesto == 'YN ':
                                                                                                                                                  amount_YN = amount_tax
                                                                                                                                                  lista_amount_YN.append(amount_tax)
                                                                                                                                  elif impuesto == 'AK ':
                                                                                                                                                  amount_AK = amount_tax
                                                                                                                                                  lista_amount_AK.append(amount_tax)
                                                                                                                                  elif impuesto == 'QC ':
                                                                                                                                                  amount_QC = amount_tax
                                                                                                                                                  lista_amount_QC.append(amount_tax)
                                                                                                                    ### Esta parte es importante por logica si no existe es 0.00
                                                                                                                  else:
                                                                                                                  
                                                                                                                                  if impuesto == 'YQ ':
                                                                                                                                                  amount_YQ = 0.00
                                                                                                                                  elif impuesto == 'YC ':
                                                                                                                                                  amount_YC = 0.00
                                                                                                                                  elif impuesto == 'US  ':
                                                                                                                                                  amount_US = 0.00
                                                                                                                                  elif impuesto == 'XA ':
                                                                                                                                                  amount_XA = 0.00
                                                                                                                                  elif impuesto == 'XY ':
                                                                                                                                                  amount_XY = 0.00
                                                                                                                                  elif impuesto == 'AW ':
                                                                                                                                                  amount_AW = 0.00
                                                                                                                                  elif impuesto == 'VJ ':
                                                                                                                                                  amount_VJ = 0.00
                                                                                                                                  elif impuesto == 'EU ':
                                                                                                                                                  amount_EU = 0.00
                                                                                                                                  elif impuesto == 'YR ':
                                                                                                                                                  amount_YR = 0.00
                                                                                                                                  elif impuesto == 'XF ':
                                                                                                                                                  amount_XF = 0.00
                                                                                                                                  elif impuesto == 'AY  ':
                                                                                                                                                  amount_AY = 0.00
                                                                                                                                  elif impuesto == 'AJ ':
                                                                                                                                                  amount_AJ = 0.00
                                                                                                                                  elif impuesto == 'YN ':
                                                                                                                                                  amount_YN = 0.00
                                                                                                                                  elif impuesto == 'AK ':
                                                                                                                                                  amount_AK = 0.00
                                                                                                                                  elif impuesto == 'QC ':
                                                                                                                                                  amount_QC = 0.00
                                                                                                                                                     
                                                                                  if line[0:3] == 'TCT':
                                                                                                  pass
                                                                                  if line[0:3] == 'TKI':
                                                                                                  pass
                                                                                  if line[0:3] == 'TKF':
                                                                                                  pass
                                                                                                  boleto = line[25:40]
                                                                                                  ### Aqui buscamos el TOTAL_EquivFare, segun vi cada archivo llegue a esta forma de hacerlo
                                                                                                  if line.find("END") != -1 and line.find("NUC") != -1:
                                                                                                                  s_NUC = line.find("NUC")
                                                                                                                  s_END = line.find("END")
                                                                                                                  TOTAL_EquivFare = line[s_NUC+3:s_END]
                                                                                                                  TOTAL_EquivFare = TOTAL_EquivFare.strip()
                                                                              
                                                                                                  elif line.find("END") != -1 and line.find("USD") != -1:
                                                                                                                  s_NUC = line.find("USD")
                                                                                                                  s_END = line.find("END")
                                                                                                                  TOTAL_EquivFare = line[s_NUC+3:s_END]
                                                                                                                  TOTAL_EquivFare = TOTAL_EquivFare.strip()
                                                                                  if line[0:3] == 'TKP':
                                                                                                  ### Igual que arriba ay que reemplaza letras por numeros
                                                                                                  TOTAL_REAL_1 =  line[33:46] 
                                                                                                  TOTAL_REAL =  line[33:46]
                                                                                                  TOTAL_REAL = TOTAL_REAL.replace('E', '5')
                                                                                                  TOTAL_REAL = TOTAL_REAL.replace('F', '6') 
                                                                                                  TOTAL_REAL = TOTAL_REAL.replace('{', '0')
                                                                                                  TOTAL_REAL = TOTAL_REAL.replace('D', '4')
                                                                                                  TOTAL_REAL = TOTAL_REAL.replace('C', '3')
                                                                                                  TOTAL_REAL = TOTAL_REAL.replace('G', '8')
                                                                                                  TOTAL_REAL = TOTAL_REAL.replace('H', '1')
                                                                                                  TOTAL_REAL = TOTAL_REAL.replace('B', '7')
                                                                                                  TOTAL_REAL = TOTAL_REAL.replace('I', '2') 
                                                                                                  TOTAL_REAL = TOTAL_REAL.replace('A', '1') 
                                                                                                  TOTAL_REAL = TOTAL_REAL[0:-2] + "." + TOTAL_REAL[-2:]
                                                                                                  TOTAL_REAL_real = float(TOTAL_REAL)
                                                                                                  TOTAL_EquivFare = float(TOTAL_EquivFare)
                                                                                                  TOTAL_CALCULADO_TAX = sum(lista_amount_taxes)
                                                                                                  TOTAL_CALCULADO = TOTAL_CALCULADO_TAX + TOTAL_EquivFare
                                                                                                  TOTAL_CALCULADO = round(TOTAL_CALCULADO, 2)
                                                                                                  ### ahora si existe alguna lsita la pasamos como amount
                                                                                                  if lista_amount_YQ:
                                                                                                                  amount_YQ = lista_amount_YQ[0]
                                                                                                  else:
                                                                                                                  amount_YQ = 0.00
                                                                                                  if lista_amount_YC:
                                                                                                                  amount_YC = lista_amount_YC[0]
                                                                                                  else:
                                                                                                                  amount_YC = 0.00
                                                                                                  if lista_amount_US:
                                                                                                                  amount_US = lista_amount_US[0]
                                                                                                  else:
                                                                                                                  amount_US = 0.00
                                                                                                  if lista_amount_XA:
                                                                                                                  amount_XA = lista_amount_XA[0]
                                                                                                  else:
                                                                                                                  amount_XA = 0.00
                                                                                                  if lista_amount_XY:
                                                                                                                  amount_XY = lista_amount_XY[0]
                                                                                                  else:
                                                                                                                  amount_XY = 0.00
                                                                                                  if lista_amount_AW:
                                                                                                                  amount_AW = lista_amount_AW[0]
                                                                                                  else:
                                                                                                                  amount_AW = 0.00
                                                                                                  if lista_amount_VJ:
                                                                                                                  amount_VJ = lista_amount_VJ[0]
                                                                                                  else:
                                                                                                                  amount_VJ = 0.00
                                                                                                  if lista_amount_EU:
                                                                                                                  amount_EU = lista_amount_EU[0]
                                                                                                  else:
                                                                                                                  amount_EU = 0.00
                                                                                                  if lista_amount_YR:
                                                                                                                  amount_YR = lista_amount_YR[0]
                                                                                                  else:
                                                                                                                  amount_YR = 0.00
                                                                                                  if lista_amount_XF:
                                                                                                                  amount_XF = lista_amount_XF[0]
                                                                                                  else:
                                                                                                                  amount_XF = 0.00
                                                                                                  if lista_amount_AY:
                                                                                                                  amount_AY = lista_amount_AY[0]
                                                                                                  else:
                                                                                                                  amount_AY = 0.00
                                                                                                  if lista_amount_AJ:
                                                                                                                  amount_AJ = lista_amount_AJ[0]
                                                                                                  else:
                                                                                                                  amount_AJ = 0.00
                                                                                                  if lista_amount_YN:
                                                                                                                  amount_YN = lista_amount_YN[0]
                                                                                                  else:
                                                                                                                  amount_YN = 0.00
                                                                                                  if lista_amount_AK:
                                                                                                                  amount_AK = lista_amount_AK[0]
                                                                                                  else:
                                                                                                                  amount_AK = 0.00           
                                                                                                  if lista_amount_QC:
                                                                                                                  amount_QC = lista_amount_QC[0]
                                                                                                  else:
                                                                                                                  amount_QC = 0.00
                                                                                                  ### Buscamos a ver si el Boleto existe
                                                                                                  buscar_boleto = class_boletos_cat.search(cr,uid,[('name', '=', archivo_cat_a_extraer),],context=context)                             
                                                                                                  if buscar_boleto: ### Si existe no hacemos nada
                                                                                                                  print "YA EXSTE", boleto
                                                                                                                  
                                                                                                  else: ### Si no existe grabamos la informacion
                                                                                                      list_total_calculado_REAL.append(TOTAL_CALCULADO)
                                                                                                      list_total_real_REAL.append(TOTAL_REAL_real)
                                                                                                      dict__datos_tkt = {
                                
                                                                                                                         'name': boleto,
                                                                                                                         'total_real': TOTAL_REAL_real,
                                                                                                                         'total_calculado': TOTAL_CALCULADO,
                                                                                                                         'monto_en_moneda': TOTAL_EquivFare,
                                                                                                                         'pasajero': pasajero,
                                                                                                                         'tipo_pasajero': tipo_pasajero,
                                                                                                                         'amount_YQ': amount_YQ,
                                                                                                                         'amount_YC': amount_YC,
                                                                                                                         'amount_US': amount_US,
                                                                                                                         'amount_XA': amount_XA,
                                                                                                                         'amount_XY': amount_XY,
                                                                                                                         'amount_AW': amount_AW,
                                                                                                                         'amount_VJ': amount_VJ,
                                                                                                                         'amount_EU': amount_EU,
                                                                                                                         'amount_YR': amount_YR,
                                                                                                                         'amount_XF': amount_XF,
                                                                                                                         'amount_AY': amount_AY,
                                                                                                                         'amount_AJ': amount_AJ,
                                                                                                                         'amount_YN': amount_YN,
                                                                                                                         'amount_AK': amount_AK,
                                                                                                                         'amount_QC': amount_QC,
                                                                                                                               }
                                                                                                      ### Agregamos el diccionario como una tupla para agregarla a la lista recuerda es many2many
                                                                                                      tupla_datos_boleto = (0, id, dict__datos_tkt)
                                                                                                      lista_tuplas_boleto.append(tupla_datos_boleto)
                                                                                                      numeros_K += 1              
                                                                            
                                                                                  if line[0:3] == 'TTT':
                                                                                                  ### Si exisste no hacemos nada, si no existe lo agregamos
                                                                                                  class_cat_obj = self.pool.get('cintas_cat') 
                                                                                                  buscar_cat = self.pool.get('cintas_cat').search(cr,uid,[('name', '=', archivo_cat_a_extraer),],context=context)
                                                                                                  if buscar_cat:
                                                                                                                  print "EXISTE"
                                                                                                                  #subprocess.call(['mv', arch_a_extraerle_datos, '/home/odoo/archivos_kiu/archivos_procesados/'])
                                                                                                  else:
                                                                                                                  total_real_REAL = sum(list_total_real_REAL)
                                                                                                                  total_calculado_REAL = sum(list_total_calculado_REAL)
                                                                                                                  total_real_REAL = float(total_real_REAL)
                                                                                                                  total_calculado_REAL = float(total_calculado_REAL)
                                                                                                                  class_cat_obj.create(cr,uid, {
                                                                                                                         'name': archivo_cat_a_extraer,
                                                                                                                          'nombres': archivo_cat_a_extraer,
                                                                                                                           'boleto_ids': lista_tuplas_boleto,
                                                                                                                            'total_calculado_REAL': total_calculado_REAL,
                                                                                                                             'total_real_REAL': total_real_REAL,
                                                    
                                                                                                                                  }) 
                                                                                                                  ### Despues de crear el registro en la BD movemos el archivo
                                                                                                                  #subprocess.call(['mv', arch_a_extraerle_datos, '/home/odoo/archivos_kiu/CAT_correctamente_procesado'])
                                                                                                                  ruta = 'mv '+ arch_a_extraerle_datos +' '+ ruta_de_usuario +'CAT_correctamente_procesado'
                                                                                                                  ps = subprocess.Popen(ruta,shell=True) ### Ejecutar la linea anterior
                                                                                                            
                                                                                                  continue
                                                                                            
                    return True



### Informacion Importante campso de ODOO
    name = fields.Char('Nombre de Archivo')
    fecha_archivo = fields.Char('Fecha del Archivo')
    numero_tkt = fields.Char('Numero de TKT')
    pnr_localizador = fields.Char('pnr_localizador')
    IssueCode = fields.Char('IssueCode')
    k_in_cat = fields.Char('k_in_cat')
    tipo_pasajero = fields.Char('tipo_pasajero')
    numero_Boleto = fields.Char('numero_Boleto')
    motivo_facturacion_codigo = fields.Char('motivo_facturacion_codigo')
    pasajero_principal = fields.Char('pasajero_principal')
    code_emisor = fields.Char('code_emisor')
    numero_motivos = fields.Char('numero_motivos')
    total_calculado_REAL  =  fields.Float('total_calculado', digits=(32, 2))
    total_real_REAL =  fields.Float('total_real', digits=(32, 2))
    boleto_ids = fields.One2many('info_cintas_cat','asociar_pnr_id')

cintas_cat()


class info_cintas_cat(models.Model):
    _name = "info_cintas_cat"
### Informacion Importante campso de ODOO
    name = fields.Char('Nombre')
    nombres= fields.Char('Nombres',size=64 )
    asociar_pnr_id = fields.Many2one('cintas_cat', required=False)                                                                               
    tipo_pasajero= fields.Char('tipo_pasajero',size=64 )
    pasajero= fields.Char('pasajero',size=64 )
    #Impuestos Desglosados
    amount_YQ  =  fields.Float('amount_YQ', digits=(32, 2))
    amount_YC  =  fields.Float('amount_YC', digits=(32, 2))
    amount_US  =  fields.Float('amount_US', digits=(32, 2))
    amount_XA  =  fields.Float('amount_XA', digits=(32, 2))
    amount_XY  =  fields.Float('amount_XY', digits=(32, 2))
    amount_AW  =  fields.Float('amount_AW', digits=(32, 2))
    amount_VJ  =  fields.Float('amount_VJ', digits=(32, 2))
    amount_EU  =  fields.Float('amount_EU', digits=(32, 2))
    amount_YR  =  fields.Float('amount_YR', digits=(32, 2))
    amount_XF  =  fields.Float('amount_XF', digits=(32, 2))
    amount_AY  =  fields.Float('amount_AY', digits=(32, 2))
    amount_AJ  =  fields.Float('amount_AJ', digits=(32, 2))
    amount_YN  =  fields.Float('amount_YN', digits=(32, 2))
    amount_AK  =  fields.Float('amount_AK', digits=(32, 2))
    amount_QC  =  fields.Float('amount_QC', digits=(32, 2))
    numero_Boleto = fields.Char('numero_Boleto')
    #Montos
    sumatoria_desglosados  =  fields.Float('sumatoria_desglosados', digits=(32, 2))
    monto_de_otros_TAX  =  fields.Float('monto_de_otros_TAX', digits=(32, 2))
    total_calculado  =  fields.Float('total_calculado', digits=(32, 2))
    total_real  =  fields.Float('total_real', digits=(32, 2))
    total_CAT  =  fields.Float('total_CAT', digits=(32, 2))
    monto_tax_2  =  fields.Float('monto_tax_2', digits=(32, 2))
    monto_tax_1  =  fields.Float('monto_tax_1', digits=(32, 2))
    monto_en_moneda  =  fields.Float('monto_en_moneda', digits=(32, 2))

info_cintas_cat()



class intermedio_cintas_cat(models.Model):
    _name = "intermedio_cintas_cat"
    
    def create_intermedio(self, cr, uid, context=None): ###Este Metodo es identico a  create_intermedio_kiu, asi que no lo voy a comentar
        print " Pasar Boletos Con Saldos Correctos  "
        account_Boletos_search = self.pool.get('info_cintas_cat').search(cr, uid, [])   
        account_Boletos_obj = self.pool.get('info_cintas_cat') 
        nro_iteracion = 0
        for boleto_id in account_Boletos_search: 
                 if nro_iteracion < 3:
                        boleto_id =account_Boletos_obj.browse(cr, uid,boleto_id ,context=context)
                        if (boleto_id.total_calculado == 0.00) and (boleto_id.total_real == 0.00):
                                        continue
                        if boleto_id.total_calculado == boleto_id.total_real:
                                 class_factura = self.pool.get('account.invoice')
                                 class_product = self.pool.get('product.template')
                                 class_tax = self.pool.get('account.tax')
                                 class_tax_ids = self.pool.get('account.invoice.tax_line_ids')
                                 valores_invoice = {}
                                 lista_tuplas_pasajes_inv = []
                                 nombre_producto = boleto_id.name
                                 monto_en_moneda = boleto_id.monto_en_moneda
                                 if class_product.search(cr,uid,[('name', '=', nombre_producto),],context=context):
                                                 continue
                                 else:
                                        BB = boleto_id
                                        lista_taxes_nombres = [
                                                        'amount_YQ', 
                                                         'amount_YC',
                                                         'amount_US ', 
                                                         'amount_XA ',
                                                         'amount_XY',
                                                         'amount_AW',
                                                         'amount_VJ',
                                                         'amount_EU',
                                                         'amount_YR',
                                                         'amount_XF',
                                                         'amount_AY',
                                                         'amount_AJ',
                                                         'amount_YN',
                                                         'amount_AK',
                                                         'amount_QC '
                                                         ]
                                        iterar_taxes = 0
                                        tax_ids = []
                                        diccionario_tax = {}
                                        lista111 =[]
                                        lista_tuplas_itinerario =[]
                                        for tax_name in lista_taxes_nombres:
                                                        amount_YQ = BB.amount_YQ
                                                        amount_YC = BB.amount_YC
                                                        amount_US = BB.amount_US
                                                        amount_XA = BB.amount_XA
                                                        amount_XY = BB.amount_XY
                                                        amount_AW = BB.amount_AW
                                                        amount_VJ = BB.amount_VJ
                                                        amount_EU = BB.amount_EU
                                                        amount_YR = BB.amount_YR
                                                        amount_XF = BB.amount_XF
                                                        amount_AY = BB.amount_AY
                                                        amount_AJ = BB.amount_AJ
                                                        amount_YN = BB.amount_YN
                                                        amount_AK = BB.amount_AK
                                                        amount_QC = BB.amount_QC
                                                        if iterar_taxes == 0:
                                                                  if amount_YQ == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        print "iterar_taxes" , "amount_YQ"
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_YQ)
                                                                        name_tax = tax_name
                                                                        print name_tax
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '251101'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount_YQ,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                        
                                                        elif iterar_taxes == 1:
                                                                  if amount_YC == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        print "iterar_taxes" , "amount_YC"
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_YC)
                                                                        name_tax = tax_name
                                                                        print name_tax
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '251201'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                                                 
                                                        elif iterar_taxes == 2:
                                                                  if amount_US == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_US)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '251301'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                        
                                                        elif iterar_taxes == 3:
                                                                  if amount_XA == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_XA)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2514'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                        
                                                        elif iterar_taxes == 4:
                                                                  if amount_XY == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_XY)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2515'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                                                 
                                                        elif iterar_taxes == 5:
                                                                  if amount_AW == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_AW)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2516'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                                                 
                                                        elif iterar_taxes == 6:
                                                                  if amount_VJ == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_VJ)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2517'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                        
                                                        elif iterar_taxes == 7:
                                                                  if amount_EU == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_EU)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2518'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                                                 
                                                        elif iterar_taxes == 8:
                                                                  if amount_YR == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_YR)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2519'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                        
                                                        elif iterar_taxes == 9:
                                                                  if amount_XF == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_XF)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2520'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                                                                        
                                                        elif iterar_taxes == 10:
                                                                  if amount_AY == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_AY)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2521'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                        
                                                        elif iterar_taxes == 11:
                                                                  if amount_AJ == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_AJ)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2522'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                                                 
                                                        elif iterar_taxes == 12:
                                                                  if amount_YN == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_YN)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2523'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                        
                                                        elif iterar_taxes == 13:
                                                                  if amount_AK == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_AK)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2524'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                        
                                                        elif iterar_taxes == 14:
                                                                  if amount_QC == 0:
                                                                                  print "iterar_taxes" , "00000000000000000000000000000000000000000  #########       QQQQQCCCCCCCCCCCCCCCC  #########"
                                                                  else:
                                                                        amount_type = "fixed"
                                                                        amount = float(amount_QC)
                                                                        name_tax = tax_name
                                                                        buscar_tax = self.pool.get('account.account').search(cr,uid,[('code', '=', '2525'),],context=context)
                                                                        account_id = buscar_tax[0]
                                                                        diccionario_tax = {
                                                                                           'name' : name_tax,
                                                                                           'account_id' : account_id,
                                                                                           'type_tax_use' : 'sale',
                                                                                           'amount_type' : "fixed",
                                                                                           'amount':amount,
                                                                                      }
                                                                        TUPLA = (0,id,diccionario_tax) 
                                                                        lista_tuplas_itinerario.append(TUPLA)
                                                                        
                                                        class_tax = self.pool.get('account.tax')  
                                                        buscar_tax = self.pool.get('account.tax').search(cr,uid,[('name', '=', name_tax),],context=context)
                                                        if buscar_tax:
                                                                        id_tax_a_cambiar = buscar_tax[0]
                                                                        tax_idssss = class_tax.write(cr, 1, [id_tax_a_cambiar], {'amount': amount})
                                                        else:
                                                                        tax_idssss = class_tax.create(cr,uid, diccionario_tax)
                                                                        buscar_tax = self.pool.get('account.tax').search(cr,uid,[('name', '=', name_tax),],context=context)
                                                                        id_tax_a_cambiar = buscar_tax[0]
                                                        iterar_taxes += 1
                                        class_product = self.pool.get('product.product')
                                        class_product.create(cr,uid, {'name': nombre_producto, 'list_price': monto_en_moneda , 'type':'service'  , 'taxes_id' : [(6, 0, lista111)], 'supplier_taxes_id' : [(6, 0, lista111)] })
                                        clase_producto = self.pool.get('product.product').search(cr,uid,[('name', '=', nombre_producto),],context=context)
                                        id_producto = clase_producto[0]
                                        ### PARTNER
                                        nombre_partner  =   BB.pasajero
                                        class_obj_partner = self.pool.get('res.partner')
                                        clase_res_partner = self.pool.get('res.partner').search(cr,uid,[('name', '=', nombre_partner),],context=context)
                                        data6 = {
                                                         'name' : nombre_partner
                                               }
                                        if clase_res_partner:
                                                     id_cliente = clase_res_partner[0]
                                        else:
                                                     print nombre_partner
                                                     class_obj_partner.create(cr,uid, data6)
                                                     clase_res_partner = self.pool.get('res.partner').search(cr,uid,[('name', '=', nombre_partner),],context=context)
                                                     id_cliente = clase_res_partner[0]
                                        buscar_code = self.pool.get('account.account').search(cr,uid,[('code', '=', '101200'),],context=context)
                                        account_id = buscar_code[0]
                                        valores_invoice["partner_id"] = id_cliente
                                        valores_invoice["name"] = nombre_producto
                                        valores_invoice["journal_id"] = '1'
                                        valores_invoice["account_id"] = account_id
                                        nro_tax = len(lista_tuplas_itinerario)
                                        if nro_tax == 0:
                                                        pass
                                        elif nro_tax >= 1:
                                                        valores_invoice["tax_line_ids"] = lista_tuplas_itinerario
                                        invoice_id = class_factura.create(cr,uid, valores_invoice)
                                        self.pool.get('account.invoice.line').create(cr, uid,{
                                                                   'invoice_id' : invoice_id,
                                                                   'name' : nombre_producto,
                                                                   'product_id' : id_producto,
                                                                   'price_unit':  monto_en_moneda,
                                                                   'account_id':  account_id,
                                                                    'invoice_line_tax_eds' : (6, id , lista_tuplas_itinerario ) ,
                                                                    })
                                        inv_obj = self.pool.get('account.invoice')
                                        inv_obj.action_date_assign(cr, uid, invoice_id, context=context)
                                        inv_obj.action_move_create(cr, uid, invoice_id, context=context)
                                        inv_obj.invoice_validate(cr, uid, invoice_id, context=context)
                                        invoice_ids = [(4,[invoice_id])]
                                        amount = BB.total_real
                                        journal_search = self.pool.get('account.journal').search(cr,uid,[('name', '=', 'Cash'),],context=context)
                                        journal_id = journal_search[0]
                                        nro_iteracion += 1
                                        
                                        
                                        
     ### CAmpos de ODOO                                   
    name = fields.Char('Nombre')
    nombres= fields.Char('Nombres',size=64 )
    tipo_pasajero= fields.Char('tipo_pasajero',size=64 )
    pasajero= fields.Char('pasajero',size=64 )
    #Impuestos Desglosados
    amount_YQ  =  fields.Float('amount_YQ', digits=(32, 2))
    amount_YC  =  fields.Float('amount_YC', digits=(32, 2))
    amount_US  =  fields.Float('amount_US', digits=(32, 2))
    amount_XA  =  fields.Float('amount_XA', digits=(32, 2))
    amount_XY  =  fields.Float('amount_XY', digits=(32, 2))
    amount_AW  =  fields.Float('amount_AW', digits=(32, 2))
    amount_VJ  =  fields.Float('amount_VJ', digits=(32, 2))
    amount_EU  =  fields.Float('amount_EU', digits=(32, 2))
    amount_YR  =  fields.Float('amount_YR', digits=(32, 2))
    amount_XF  =  fields.Float('amount_XF', digits=(32, 2))
    amount_AY  =  fields.Float('amount_AY', digits=(32, 2))
    amount_AJ  =  fields.Float('amount_AJ', digits=(32, 2))
    amount_YN  =  fields.Float('amount_YN', digits=(32, 2))
    amount_AK  =  fields.Float('amount_AK', digits=(32, 2))
    amount_QC  =  fields.Float('amount_QC', digits=(32, 2))
    numero_Boleto = fields.Char('numero_Boleto')
    #Montos
    sumatoria_desglosados  =  fields.Float('sumatoria_desglosados', digits=(32, 2))
    monto_de_otros_TAX  =  fields.Float('monto_de_otros_TAX', digits=(32, 2))
    total_calculado  =  fields.Float('total_calculado', digits=(32, 2))
    total_real  =  fields.Float('total_real', digits=(32, 2))
    total_CAT  =  fields.Float('total_CAT', digits=(32, 2))
    monto_tax_2  =  fields.Float('monto_tax_2', digits=(32, 2))
    monto_tax_1  =  fields.Float('monto_tax_1', digits=(32, 2))
    monto_en_moneda  =  fields.Float('monto_en_moneda', digits=(32, 2))

intermedio_cintas_cat()

########## VOLADOS
class volados(models.Model):
    _name = "volados"
    ### Crear los volados consiste en mover el monto de una cuenta a otra segun los archivos FLT
    def create_volados(self, cr, uid, context=None):
                    ### Leer el directorio de los Volados FLT_descomprimidos
                    #os.system("ls /home/odoo/archivos_kiu/FLT_descomprimidos   > /home/odoo/archivos_kiu/FLT_descomprimidos.txt")
                    ruta = "ls " +ruta_de_usuario +'FLT_descomprimidos'+ ' > ' + ruta_de_usuario +'FLT_descomprimidos.txt' ### ruta a ejecutar como si de la shell se trata
                    ps = subprocess.Popen(ruta,shell=True) ### Ejecutar la linea anterior
                    
                    archivo_CAT =ruta_de_usuario+'/FLT_descomprimidos.txt' ### Agregar el nombre a la lista
                    archi_CAT = open(archivo_CAT,'r')  ### Leemos el archivo
                    ### creamos las variables para ODOO
                    class_flt_obj = self.pool.get('volados') 
                    class_boletos_flt = self.pool.get('info_volados') 
                    class_PNR_en_flt = self.pool.get('volados') 
                    ### LEEMOS la lista
                    for archivo_flt_a_extraer in archi_CAT:
                                    ### no hay mucho que comentar
                                    arch_a_extraerle_datos = ruta_de_usuario+'/FLT_descomprimidos/'+archivo_flt_a_extraer
                                    arch_a_extraerle_datos = arch_a_extraerle_datos.strip()
                                    lista_ticket_numbers = []
                                    agregados = 0
                                    repetidos = 0
                                    Amount_of_Flight_Coupon_total = 0
                                    if archivo_flt_a_extraer:
                                                                    ### Luego de entrar al archivo debemos leerlo linea a linea
                                                                    archivo = arch_a_extraerle_datos
                                                                    reader= open(archivo, 'r')
                                                                    cantidad_archivos  =  0
                                                                    list_total_calculado_REAL = []
                                                                    list_total_real_REAL = []
                                                                    lista_tuplas_boleto = []
                                                                    numeros_K = 0
                                                                    ### como es un CSV lo leemos asi
                                                                    with open(archivo, 'r') as f:
                                                                                    for row in csv.reader(f.read().splitlines()):
                                                                                                    if row[0] == '1':
                                                                                                                    ### Igual que antes los archivos comienzan de una manera y usamos esta linea y caracter para hacer algo con ellos
                                                                                                                    Record_Indicator = row[0]
                                                                                                                    Version = row[1]
                                                                                                                    Date_of_Processing = row[2]
                                                                                                                    Time_of_Processing = row[3]
                                                                                                    if row[0] == '5':
                                                                                                                    ### LAs variables estan como en el archivo de la documentacion
                                                                                                                    Record_Indicator = row[0]
                                                                                                                    Flight_Number = row[1]
                                                                                                                    Flight_Date = row[2]
                                                                                                                    Origin = row[3]
                                                                                                                    Destination = row[4]
                                                                                                                    Type_of_Ticket = row[5]
                                                                                                                    Ticket_Number = row[6]
                                                                                                                    Coupon_Number = row[7]
                                                                                                                    Type_of_Passenger = row[8]
                                                                                                                    Name_of_Passenger = row[9]
                                                                                                                    Passenger_Identification_FOID = row[10]
                                                                                                                    Passenger_Frequent_Flyer_Number = row[11]
                                                                                                                    Reservation_Booking_Designator = row[12]
                                                                                                                    Fare_Basis = row[13]
                                                                                                                    Currency = row[14]
                                                                                                                    Amount_of_Flight_Coupon = row[15]
                                                                                                                    Record_Locator = row[16]
                                                                                                                    Marketing_Flight_Number_2 = row[17]
                                                                                                                    Number_of_Checked_in_Baggage = row[18]
                                                                                                                    Weight_of_Checked_in_Baggage = row[19]
                                                                                                                    Detail_of_Bag_Tag_3 = row[20]
                                                                                                                    Ticket_Number_vuelo = Ticket_Number + Flight_Number
                                                                                                                    
                                                                                                                    if Ticket_Number_vuelo in lista_ticket_numbers:
                                                                                                                                    repetidos += 1
                                                                                                                                    pass
                                                                                                                    else:
                                                                                                                                    ### CREAMOS el diccionario dict_datos_tkt
                                                                                                                           dict_datos_tkt = {
                                
                                                                                                                                'Record_Indicator': Record_Indicator,
                                                                                                                                'Flight_Number': Flight_Number,
                                                                                                                                'Flight_Date': Flight_Date,
                                                                                                                                'Origin': Origin,
                                                                                                                                'Destination': Destination,
                                                                                                                                'Type_of_Ticket': Type_of_Ticket,
                                                                                                                                'Ticket_Number': Ticket_Number,
                                                                                                                                'Coupon_Number': Coupon_Number,
                                                                                                                                'Type_of_Passenger': Type_of_Passenger,
                                                                                                                                'Name_of_Passenger': Name_of_Passenger,
                                                                                                                                'Passenger_Identification_FOID': Passenger_Identification_FOID,
                                                                                                                                'Passenger_Frequent_Flyer_Number': Passenger_Frequent_Flyer_Number,
                                                                                                                                'Reservation_Booking_Designator': Reservation_Booking_Designator,
                                                                                                                                'Fare_Basis': Fare_Basis,
                                                                                                                                'Currency': Currency,
                                                                                                                                'Amount_of_Flight_Coupon': Amount_of_Flight_Coupon,
                                                                                                                                'Record_Locator': Record_Locator,
                                                                                                                                'Marketing_Flight_Number_2': Marketing_Flight_Number_2,
                                                                                                                                'Number_of_Checked_in_Baggage': Number_of_Checked_in_Baggage,
                                                                                                                                'Weight_of_Checked_in_Baggage': Weight_of_Checked_in_Baggage,
                                                                                                                                'Detail_of_Bag_Tag_3': Detail_of_Bag_Tag_3,
                                                                                                                                
                                                                                                                               }
                                                                                                                           agregados += 1
                                                                                                                           ### Agregamos el Diccionario a la Tupla y luego a la Lista
                                                                                                                           lista_Amount_of_Flight_Coupon_total = []
                                                                                                                           Amount_of_Flight_Coupon = float(Amount_of_Flight_Coupon)
                                                                                                                           Amount_of_Flight_Coupon_total += Amount_of_Flight_Coupon
                                                                                                                           lista_Amount_of_Flight_Coupon_total.append(Amount_of_Flight_Coupon_total)
                                                                                                                           lista_ticket_numbers.append(Ticket_Number_vuelo)
                                                                                                                           tupla_datos_boleto = (0, id, dict_datos_tkt)
                                                                                                                           lista_tuplas_boleto.append(tupla_datos_boleto)
                                                                                                    elif row[0] == '2':
                                                                                                                    pass


                                                                                                    elif row[0] == '3':
                                                                                                                    pass

                                                                                                    elif row[0] == '4':
                                                                                                                    pass

                                                                                                    elif row[0] == '6':
                                                                                                                    pass

                                                                                                    elif row[0] == '1':
                                                                                                                    pass
                                                                                                    
                                                                     ### Buscamos el archivo en la clase volados, si existe no hacemos nada o deberiamos moverlo a repetidos
                                                                    buscar_volados = self.pool.get('volados').search(cr,uid,[('name', '=', archivo_flt_a_extraer),],context=context)
                                                                    if buscar_volados:
                                                                                      continue
                                                                    else:
                                                                                    ## Si no existe creamos todos los items, aqui no hay nada raro asi q no voy a comentar mucho
                                                                                      class_obj_partner = self.pool.get('res.partner')
                                                                                      Amount_of_Flight_Coupon_total = lista_Amount_of_Flight_Coupon_total[0]
                                                                                      ### Creamos el registro de volado
                                                                                      class_flt_obj.create(cr,uid, {
                                                                                                                         'name': archivo_flt_a_extraer,
                                                                                                                          'Date_of_Processing': Date_of_Processing,
                                                                                                                          'Record_Indicator': Record_Indicator,
                                                                                                                           'Version': Version,
                                                                                                                            'Time_of_Processing': Time_of_Processing,
                                                                                                                            'boleto_ids': lista_tuplas_boleto,
                                                                                                                            'Amount_of_Flight_Coupon_total': Amount_of_Flight_Coupon_total,
                                                                                                                              }) 
                                                                                      ### Creamo el movimiento
                                                                                      class_journal_object =  self.pool.get('account.move') 
                                                                                      buscar_journal = self.pool.get('account.journal').search(cr,uid,[('name', '=', 'Miscellaneous Operations'),],context=context) 
                                                                                      clase_res_partner = self.pool.get('res.partner').search(cr,uid,[('name', '=', "Vuelos Aruba"),],context=context)
                                                                                      data6 = {
                                                                                                       'name' : "Vuelos Aruba"
                                                                                             }
                                                                                      if clase_res_partner:
                                                                                                   id_cliente = clase_res_partner[0]
                                                                                      else:
                                                                                                  
                                                                                                   class_obj_partner.create(cr,uid, data6)
                                                                                                   nombre_partner = "Vuelos Aruba"
                          
                                                                                                   clase_res_partner = self.pool.get('res.partner').search(cr,uid,[('name', '=', nombre_partner),],context=context)
                                                                                                   id_cliente = clase_res_partner[0]
                                                                                      
                                                                                      account_id = self.pool.get('account.account').search(cr,uid,[('code', '=', '283'),],context=context) 
                                                                                      dict_datos_diferidos = {
                                                                                                                                'credit': Amount_of_Flight_Coupon_total,
                                                                                                                                'debit': 0.00,
                                                                                                                                'name': 'Miscellaneous Operations',
                                                                                                                                'partner_id': id_cliente,
                                                                                                                                'account_id': account_id[0],
                                                                                                                               }
                                                                                      lista_tuplas_journal = []
                                                                                      tupla_datos_journal = (0, 0, dict_datos_diferidos)
                                                                                      lista_tuplas_journal.append(tupla_datos_journal)
                                                                                      account_id = self.pool.get('account.account').search(cr,uid,[('code', '=', '51'),],context=context) 
                                                                                      dict_datos_ingresos = {
                                                                                                                                'credit': 0.00,
                                                                                                                                'debit': Amount_of_Flight_Coupon_total,
                                                                                                                                'name': 'Miscellaneous Operations',
                                                                                                                                'partner_id': id_cliente,
                                                                                                                                'account_id': account_id[0],
                                                                                                                               }
                                                                                      tupla_datos_journal = (0, 0, dict_datos_ingresos)
                                                                                      lista_tuplas_journal.append(tupla_datos_journal)
                                                                                      ### Agregamos al Journal el movimiento
                                                                                      class_journal_object.create(cr,uid, {
                                                                                                                          'journal_id': buscar_journal[0],
                                                                                                                          'partner_id': id_cliente,
                                                                                                                          'line_ids': lista_tuplas_journal,
                                                                                                                              }) 
                                                                                      #subprocess.call(['mv', arch_a_extraerle_datos, '/home/odoo/archivos_kiu/FLT_correctamente_procesado'])
                                                                                      ruta = 'mv '+ arch_a_extraerle_datos + ' '+ ruta_de_usuario +'FLT_correctamente_procesado'
                                                                                      ps = subprocess.Popen(ruta,shell=True) ### Ejecutar la linea anterior
                                                                                      
                                                                                      
                                                                                      
                    return True
    
    ### ESta clase se peude crear de otra manera pero yo preferi agregarla aqui, es simple mueve los archivos 
    ### segun algunos rasgos de la carpeta FTP a donde van a ser leidos por los metodo de arriba, Tambien los descomprime
    def move_items_cmas_flt_cat(self, cr, uid, context=None):
                    #os.system("ls /home/odoo/archivos_kiu/ | grep 'CMAS.zip'| grep 'CRS'  >  /home/odoo/archivos_kiu/CMAS_a_Extraer.txt")
                    
                    ruta = "ls " +ruta_de_usuario + " | grep 'CMAS.zip'| grep 'CRS'  > " + ruta_de_usuario +"CMAS_a_Extraer.txt" ### ruta a ejecutar como si de la shell se trata
                    ps = subprocess.Popen(ruta,shell=True) ### Ejecutar la linea anterior
                    
                    
                    archivo=ruta_de_usuario+'/CMAS_a_Extraer.txt'
                    archi=open(archivo,'r')
                    lineas=archi.read().splitlines()
                    if len(lineas)> 0:
                                    iteracion = 0
                                    for archivo_cmas_a_extraer in lineas:
                                                    arch_a_extraer = ruta_de_usuario+'/'+archivo_cmas_a_extraer
                                                    cmas_a_extraer_descomprimido = archivo_cmas_a_extraer[0:-4]
                                                    subprocess.call(['unzip', arch_a_extraer])
                                                    
                                                    #subprocess.call(['mv', arch_a_extraer, '/home/odoo/archivos_kiu/CRS_comprimidos'])
                                                    ruta = 'mv '+ arch_a_extraer+ " "+  ruta_de_usuario+'CMAS_comprimidos'
                                                    ps = subprocess.Popen(ruta,shell=True) ### Ejecutar la linea anterior
                                                    
                                                    #subprocess.call(['mv', cmas_a_extraer_descomprimido, '/home/odoo/archivos_kiu/CRS_descomprimidos'])
                                                    ruta = 'mv '+ cmas_a_extraer_descomprimido+ " "+  ruta_de_usuario+'CMAS_descomprimidos'
                                                    ps = subprocess.Popen(ruta,shell=True) ### Ejecutar la linea anterior
                                                    
                                                    iteracion += 1
                                                

                    os.system("ls /home/odoo/archivos_kiu/ | grep 'CMAS.zip'| grep 'FLT'  >  /home/odoo/archivos_kiu/FLT_a_Extraer.txt")
                    
                    ruta = "ls " +ruta_de_usuario  +"  | grep 'CMAS.zip'| grep 'FLT'  >  " + ruta_de_usuario +'FLT_a_Extraer.txt' ### ruta a ejecutar como si de la shell se trata
                    ps = subprocess.Popen(ruta,shell=True) ### Ejecutar la linea anterior
                    
                    archivo=ruta_de_usuario+'/FLT_a_Extraer.txt'
                    archi=open(archivo,'r')
                    lineas=archi.read().splitlines()
                    if len(lineas)> 0:
                                    
                                    iteracion = 0
                                    for archivo_cmas_a_extraer in lineas:
                                                    arch_a_extraer = ruta_de_usuario+'/'+archivo_cmas_a_extraer
                                                    cmas_a_extraer_descomprimido = archivo_cmas_a_extraer[0:-4]
                                                    subprocess.call(['unzip', arch_a_extraer])
                                                    #subprocess.call(['mv', arch_a_extraer, '/home/odoo/archivos_kiu/FLT_comprimidos'])
                                                    ruta = 'mv '+ arch_a_extraer+ " "+  ruta_de_usuario+'FLT_comprimidos'
                                                    ps = subprocess.Popen(ruta,shell=True) ### Ejecutar la linea anterior
                                                    
                                                    #subprocess.call(['mv', cmas_a_extraer_descomprimido, '/home/odoo/archivos_kiu/FLT_descomprimidos'])
                                                    ruta = 'mv '+ cmas_a_extraer_descomprimido+ " "+  ruta_de_usuario+'FLT_descomprimidos'
                                                    ps = subprocess.Popen(ruta,shell=True) ### Ejecutar la linea anterior
                                                    
                                                    iteracion += 1
                                                    
                    #os.system("ls /home/odoo/archivos_kiu/ | grep 'CMAS.zip'| grep 'TID'  >  /home/odoo/archivos_kiu/TID_a_Extraer.txt")
                    ruta = "ls " +ruta_de_usuario  +"  | grep 'CMAS.zip'| grep 'TID'  >  " + ruta_de_usuario +'TID_a_Extraer.txt' ### ruta a ejecutar como si de la shell se trata
                    ps = subprocess.Popen(ruta,shell=True) ### Ejecutar la linea anterior
                    
                    archivo=ruta_de_usuario+'/TID_a_Extraer.txt'
                    archi=open(archivo,'r')
                    lineas=archi.read().splitlines()
                    if len(lineas)> 0:
                                    iteracion = 0
                                    for archivo_cmas_a_extraer in lineas:
                                                    arch_a_extraer = ruta_de_usuario+'/'+archivo_cmas_a_extraer
                                                    cmas_a_extraer_descomprimido = archivo_cmas_a_extraer[0:-4]
                                                    
                                                    #subprocess.call(['mv', arch_a_extraer, '/home/odoo/archivos_kiu/archivos_comprimidos_TID'])
                                                    ruta = 'mv '+ arch_a_extraer+ " "+  ruta_de_usuario+'archivos_comprimidos_TID'
                                                    ps = subprocess.Popen(ruta,shell=True) ### Ejecutar la linea anterior
                                                    
                                                    
                                                    #subprocess.call(['mv', cmas_a_extraer_descomprimido, '/home/odoo/archivos_kiu/archivos_descomprimidos_TID'])
                                                    ruta = 'mv '+ cmas_a_extraer_descomprimido+ " "+  ruta_de_usuario+'archivos_descomprimidos_TID'
                                                    ps = subprocess.Popen(ruta,shell=True) ### Ejecutar la linea anterior
                                                    
                                                    
                                                    iteracion += 1
                                                                            

                    #os.system("ls /home/odoo/archivos_kiu/ | grep 'CAT.zip'| grep 'CRS'  >  /home/odoo/archivos_kiu/CAT_a_Extraer.txt")
                    ruta = "ls " +ruta_de_usuario  +"  | grep 'CAT.zip'| grep 'CRS'  >  " + ruta_de_usuario +'CAT_a_Extraer.txt' ### ruta a ejecutar como si de la shell se trata
                    ps = subprocess.Popen(ruta,shell=True) ### Ejecutar la linea anterior
                    
                    archivo=ruta_de_usuario+'/CAT_a_Extraer.txt'
                    archi=open(archivo,'r')
                    lineas=archi.read().splitlines()
                    if len(lineas)> 0:
                                    iteracion = 0
                                    for archivo_cmas_a_extraer in lineas:
                                                    arch_a_extraer = ruta_de_usuario+'/'+archivo_cmas_a_extraer
                                                    cmas_a_extraer_descomprimido = archivo_cmas_a_extraer[0:-4]
                                                    subprocess.call(['unzip', arch_a_extraer])
                                                    
                                                    #subprocess.call(['mv', cmas_a_extraer_descomprimido, '/home/odoo/archivos_kiu/FLT_comprimidos'])
                                                    ruta = 'mv '+ cmas_a_extraer_descomprimido+ " "+  ruta_de_usuario+'CAT_comprimidos'
                                                    ps = subprocess.Popen(ruta,shell=True) ### Ejecutar la linea anterior
                                                    
                                                    #subprocess.call(['mv', arch_a_extraer, '/home/odoo/archivos_kiu/FLT_descomprimidos'])
                                                    ruta = 'mv '+ arch_a_extraer+ " "+  ruta_de_usuario+'CAT_descomprimidos'
                                                    ps = subprocess.Popen(ruta,shell=True) ### Ejecutar la linea anterior
                                                    iteracion += 1
                                                    
### Informacion Importante
    Amount_of_Flight_Coupon_total = fields.Float('Amount_of_Flight_Coupon_total')
    name = fields.Char('Nombre de Archivo')
    Date_of_Processing = fields.Char('Date_of_Processing')
    Record_Indicator = fields.Char('Record_Indicator')
    Version = fields.Char('Version')
    boleto_ids = fields.One2many('info_volados','asociar_pnr_id')
volados()


class info_volados(models.Model):
    _name = "info_volados"
    name = fields.Char('Nombre')
    nombres= fields.Char('Nombres',size=64 )
    Record_Indicator= fields.Char('Record_Indicator',size=64 )
    Flight_Number= fields.Char('Flight_Number',size=64 )
    Origin= fields.Char('Origin',size=64 )
    Destination= fields.Char('Destination',size=64 )
    Type_of_Ticket= fields.Char('Type_of_Ticket',size=64 )
    Ticket_Number= fields.Char('Ticket_Number',size=64 )
    Coupon_Number= fields.Char('Coupon_Number',size=64 )
    Type_of_Passenger= fields.Char('Type_of_Passenger',size=64 )
    Name_of_Passenger= fields.Char('Name_of_Passenger',size=64 )
    Passenger_Identification_FOID= fields.Char('Passenger_Identification_FOID',size=64 )
    Passenger_Frequent_Flyer_Number= fields.Char('Passenger_Frequent_Flyer_Number',size=64 )
    Reservation_Booking_Designator= fields.Char('Reservation_Booking_Designator',size=64 )
    Fare_Basis= fields.Char('Fare_Basis',size=64 )
    Currency= fields.Char('Currency',size=64 )
    Record_Locator= fields.Char('Record_Locator',size=64 )
    Marketing_Flight_Number_2= fields.Char('Marketing_Flight_Number_2',size=64 )
    Number_of_Checked_in_Baggage= fields.Char('Number_of_Checked_in_Baggage',size=64 )
    Weight_of_Checked_in_Baggage= fields.Char('Weight_of_Checked_in_Baggage',size=64 )
    Detail_of_Bag_Tag_3= fields.Char('Detail_of_Bag_Tag_3',size=64 )
    Flight_Date= fields.Char('Flight_Date',size=64 )
    Amount_of_Flight_Coupon= fields.Float('Amount_of_Flight_Coupon',digits=(32, 2) )
    asociar_pnr_id = fields.Many2one('volados', required=False)
info_volados()
