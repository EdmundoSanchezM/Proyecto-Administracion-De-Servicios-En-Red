from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
from collections import namedtuple
import networkx as nx
import matplotlib.pyplot as plt
import time
from os import path
import requests
from scripts.db import *
import scripts.ownsnmp as snmpall

Router = namedtuple('Router', ['destination_host', 'management_ip'])

def show_cdp(ip):
    device = {
        'device_type': 'cisco_ios_telnet',
        'host': ip,
        'password': 'admin',
        'username': 'admin'
    }
    try:
        with ConnectHandler(**device) as telnet:
            return telnet.send_command('show cdp neighbors detail', use_textfsm=True)
    except NetmikoAuthenticationException:
        print('Authentication error')
        print(router.management_ip)
    except NetmikoTimeoutException:
        print('Timeout error')
    except Exception:
        return ip
        print('Network error')
    return []

def get_topology(main_router):
    routers = []
    next_router = [main_router]
    visited_routers = [main_router.destination_host]
    network = nx.Graph()
    fig = plt.figure(figsize=(15,15))
    ax = plt.subplot(111)

    while next_router:
        router = next_router.pop(0)
        if(show_cdp(router.management_ip) != router.management_ip):
            routers.append(router)
            nombre_ip  = router.destination_host.partition(".")[0]+":"+router.management_ip
            if router.destination_host.partition(".")[0] == main_router.destination_host:
                nombre_ip  = router.destination_host.partition(".")[0]+":"+main_router.management_ip
            for neighbor in show_cdp(router.management_ip):
                network.add_node(nombre_ip)
                nombre_ip2  = neighbor['destination_host'].partition(".")[0]+":"+neighbor['management_ip']
                if neighbor['destination_host'].partition(".")[0] == main_router.destination_host:
                    nombre_ip2  = neighbor['destination_host'].partition(".")[0]+":"+main_router.management_ip
                if neighbor['destination_host'] not in visited_routers:
                    network.add_edge(nombre_ip, nombre_ip2)
                    visited_routers.append(neighbor['destination_host'])
                    next_router.append(Router(neighbor['destination_host'], neighbor['management_ip']))
    pos = nx.spring_layout(network)
    nx.draw(network, pos, node_size=2500, node_color='yellow', font_size=15, font_weight='bold', with_labels = True)
    plt.tight_layout()
    plt.savefig("/home/edmundojsm/Escritorio/Proyecto/FLASKuwu/static/img/topologia.png", format="PNG")
    return routers, network

def exits_changes(n_routers):
    mensaje ="Detectamos los siguientes cambios: \n"
    i = 0
    uwu = False
    with open('/home/edmundojsm/Escritorio/Proyecto/FLASKuwu/scripts/uwu.txt') as f:
        lines = f.read().splitlines()
    for router in n_routers:
        if( i != len(n_routers)-1):
            existo = False
            for orouter in lines:
                if(router.management_ip == orouter.partition(":")[2]):
                    existo = True
                    if(router.destination_host.partition(".")[0] != orouter.partition(":")[0]):
                        mensaje=mensaje+"El router con ip de administracion: "+router.management_ip+" cambio de nombre a "+router.destination_host.partition(".")[0]+"\n"
                        uwu = True
            if not existo:
                mensaje=mensaje+"El router con ip de administracion: "+router.management_ip+" y nombre "+router.destination_host.partition(".")[0]+" fue agregado recientemente "+"\n"
        i=1+i
    for orouter in lines:
        existo = False
        for router in n_routers:
            if(router.management_ip == orouter.partition(":")[2]):
                existo = True
        if not existo:
            mensaje=mensaje+"El router con ip de administracion: "+orouter.partition(":")[2]+" y nombre "+orouter.partition(":")[0]+" fue eliminado recientemente o la interface de conexion fue dada de baja"+"\n"
    if(len(mensaje)>36):
        if(uwu):
            print(mensaje)
            enviaemail(mensaje)
        else:
            print(mensaje)
            enviaemail(mensaje)
            actualizaRouters(n_routers)
            snmpall.actuDataR()
    return mensaje

def enviaemail(contenido):
    ploads = {'cuerpo':contenido}
    r = requests.post('http://0.0.0.0:7777/send-email',data=ploads)

#if __name__ == '__main__':
#    main_router = Router('R1', '10.0.1.254')
#    routers, topology = get_topology(main_router)
#    for router in routers:
#        print(router)
#    if(path.exists('/home/edmundojsm/Escritorio/Proyecto/FLASKuwu/uwu.txt')): 
#        exits_changes(routers)
#    with open('/home/edmundojsm/Escritorio/Proyecto/FLASKuwu/uwu.txt', "w") as myfile:
#        i = 0
#        for router in routers:
#            if i == len(routers)-1:
#                myfile.write(router.destination_host.partition(".")[0]+":"+main_router.management_ip)
#            elif i!=0:
#                myfile.write(router.destination_host.partition(".")[0]+":"+router.management_ip + "\n")
#            i=1+i

