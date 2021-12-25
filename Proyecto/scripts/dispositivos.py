import scripts.get_snmp as g_snmp 
import scripts.levanta_snmp as lev_snmp
import scripts.set_snmp as s_snmp
import json, re



def actualizar_datos_dispositivo(conexiones, nombre, localizacion, contacto, os): #nombre, locali, contac, sistem
    host = ""
    for c in conexiones:
        print(c)
        host = c
        break
    print("cambiando informacion de nombre...")
    s_snmp.set_information(0,host, nombre)
    print("cambiando informacion de os...")
    #s_snmp.set_information(1,host, os)
    print("cambiando informacion de contacto...")
    s_snmp.set_information(2,host, contacto)
    print("cambiando informacion de localizacion...")
    s_snmp.set_information(3,host, localizacion)
    print("informacion cambiada...")

def obtener_datos_inciales_dispositivos(datos):
	res = []
	for dispositivo in datos:
		hostname = dispositivo["hostname"]
		ip_int = dispositivo["interfaces"][0]["ip"]
		res.append([hostname, ip_int])
	return res

def obtener_conexiones_dispositivo(nombre_disp, conexiones_dic):
    conexiones = {}

    for con in conexiones_dic:
        if con['host_1'] == nombre_disp:
            conexiones[con['ip_1']] = con['ip_2']
        elif con['host_2'] == nombre_disp:
            conexiones[con['ip_2']] = con['ip_1']
    return conexiones

#Retorna:
# - ID Dispositivo 
# - Nombre 
# - Sistema operativo 
# - localización 
# - encargado 
# - contacto 
def obtener_datos_dispositivo(ip_dispositivo):
    id_dispositivo = ""
    nombre_disp = ""
    nombre_os = ""
    contacto = ""
    lugar = ""

    res = g_snmp.obtain_router_data(ip_dispositivo)
    #res =  {'sysDescr': 'Cisco IOS Software, 7200 Software (C7200-A3JK9S-M), Version 12.4(25g), RELEASE SOFTWARE (fc1)\r\nTechnical Support: http://www.cisco.com/techsupport\r\nCopyright (c) 1986-2012 by Cisco Systems, Inc.\r\nCompiled Wed 22-Aug-12 11:45 by prod_rel_team', 'sysContact': '', 'sysName': 'R3.la-pandilla-mantequilla', 'sysLocation': '', 'hostname': 'R3'}

    nombre_disp = res['hostname']
    #nombre_disp = res['sysName']
    id_dispositivo = res["hostname"][1:]
    nombre_os = re.sub(' +', ' ', res["sysDescr"])
    nombre_os = re.sub('\r+', ' ', nombre_os)
    nombre_os = re.sub('\n+', ' ', nombre_os)
    contacto = res["sysContact"]
    lugar = res["sysLocation"]

    return [id_dispositivo, nombre_disp, nombre_os, contacto, lugar]


#ip de alguna interfaz del dispositivo a obtener paquetes
#obtenemos la ip de la interfaz con la cual se conecta el router que queremos sacar sus paquetes perdidos.
#obtenemos el numero de paquetes enviados en las conexiones del dispositivo
#calculamos promedio de perdida, numero total de paquetes enviados y recibidos
    #numero total de paquetes enviados: suma de paquetes de salida de todas las interfaces del dispositivo a medir
    #numero total de paquetes recibidos: suma de paquetes de entrada en cada interfaz
def obtener_paquetes_dispositivo(origen,fin):
    #lev_snmp.init_configure("10.0.1.254")
    total_paquetes_enviados = 0
    total_paquetes_perdidos = 0
    snmp_res = g_snmp.check_lost_percentage(origen,fin, 0)
    return snmp_res
        

#lev_snmp.init_configure("10.0.1.254")
# print(obtener_datos_dispositivo("10.0.2.1"))
# print("conexions del router 3 con los demas routers", obtener_conexiones_dispositivo('R3', d4))

# datos_dispositivo = obtener_datos_dispositivo("10.0.2.1")
# nom_disp = datos_dispositivo[1]
# conexiones = obtener_conexiones_dispositivo(nom_disp, d4)
# paquetes,dos = obtener_paquetes_dispositivo(conexiones)

#5253 3608
