#!/usr/bin/env python3
from scripts.db import *
from scripts.get_snmp import *
from scripts.set_snmp import *
import json, re
from scripts.captura.networking import ssh, snmp
from scripts.captura.networking.ssh import tools
from scripts.captura.stpthread import StoppableThread
import scripts.dispositivos as paq

def saveDataR(conexion):
    print('Salvando datos del router')
    allR = verRoutersSNMP(conexion)
    for row in allR:
        res = obtain_router_data(row[2])
        nombre_disp = res['hostname']
        #nombre_disp = res['sysName']
        nombre_os = re.sub(' +', ' ', res["sysDescr"])
        nombre_os = re.sub('\r+', ' ', nombre_os)
        nombre_os = re.sub('\n+', ' ', nombre_os)
        contacto = res["sysContact"]
        lugar = res["sysLocation"]
        putDataRSNMP(conexion,row[2], nombre_disp, nombre_os, lugar, contacto)
    print('All ok')

def actuDataR():
    conexion = conecta_db("Proyecto.db")
    print('Salvando datos del router')
    allR = verRoutersSNMP(conexion)
    for row in allR:
        res = obtain_router_data(row[2])
        nombre_disp = res['hostname']
        #nombre_disp = res['sysName']
        nombre_os = re.sub(' +', ' ', res["sysDescr"])
        nombre_os = re.sub('\r+', ' ', nombre_os)
        nombre_os = re.sub('\n+', ' ', nombre_os)
        contacto = res["sysContact"]
        lugar = res["sysLocation"]
        putDataRSNMP(conexion,row[2], nombre_disp, nombre_os, lugar, contacto)
    print('All ok')
    close_db(conexion)

def actaulizarRSNMP(conexion,datos):
    print('Salvando datos del router')
    modifica_RSNMP(conexion,datos)
    set_information(0,datos[0], datos[1])
    set_information(1,datos[0], datos[3])
    set_information(2,datos[0], datos[2])
    mensaje = 'OK'
    return mensaje

def set_data_to_db(db, current, session):

    sys_info = snmp.information.get_sys_info(current)
    sys_info["accesible_ip"] = current

    interfaces = ssh.information.get_all_connections(session)

    for si in snmp.information.get_interfaces(interfaces[1]["ip"]):

        i = [
            index for (index, d) in enumerate(interfaces) if d["name"] == si["ifDescr"]
        ][0]
        interfaces[i]["ifMtu"] = si["ifMtu"]
        interfaces[i]["ifSpeed"] = si["ifSpeed"]
        interfaces[i]["ifPhysAddress"] = si["ifPhysAddress"]
        interfaces[i]["ifAdminStatus"] = si["ifAdminStatus"]
        interfaces[i]["ifOperStatus"] = si["ifOperStatus"]
        interfaces[i]["mibIndex"] = si["mibIndex"]

    #r = rt.add(db, sys_info, interfaces)
    new_interfaces = []
    for i in interfaces:
        new_interfaces.append(
            (
                current,
                i["name"],
                i["ip"],
                i["net"],
                i["mask"],
                i["ifMtu"],
                i["ifSpeed"],
                i["ifPhysAddress"],
                i["ifAdminStatus"],
                i["ifOperStatus"],
                i["mibIndex"],
            )
        )
    print(new_interfaces)
    saveInterfaz(new_interfaces)

def interfaces():
    with open('/home/edmundojsm/Escritorio/Proyecto/FLASKuwu/scripts/uwu.txt') as f:
            lines = f.read().splitlines()
    for router in lines:
        ip = router.partition(":")[2]
        session = ssh.connection.create(ip, 'admin')
        set_data_to_db('s', ip, session)

def getInfoDest(interfazO):
    ipdest = interfazO.split(".")
    if(ipdest[3] == '254' ):
        ipdest[3] = '253'
    else:
        ipdest[3] = '254'
    ipdest = '.'.join(ipdest)
    res = getMIB(ipdest)
    MIB = 0    
    for i in res:
        MIB = i[0]
    return {"ip": ipdest,  "mibIndex": MIB,}


def getMIBO(interfazO):
    res = getMIB(interfazO)
    MIB = 0    
    for i in res:
        MIB = i[0]
    return {"ip": interfazO,  "mibIndex": MIB,}

def getPaquetes(interface):
    conexion = conecta_db("Proyecto.db")
    interface_dest = getInfoDest(interface)
    print(interface_dest)
    interface_origen = getMIBO(interface)
    print(interface_origen)
    info = paq.obtener_paquetes_dispositivo(interface_origen,interface_dest)
    print(info)
    insertPaq(conexion,info)
    close_db(conexion)
    return info[7]
