#!/usr/bin/env python3
from pyvis.network import Network
from scripts.module_scan import *
from scripts.dibujo import *

def mapearRed(interface):
    res = scan_by_interface(interface,"admin","admin","1234")
    print("\n\nDatos obtenidos al mapear Red:\n\n")
    for element in res:
        print(element)
    return res

def dibujarRed(data):
    general = data[0]
    interconexiones = data[1]
    routers = data[2]
    devices = data[3]
    print("construyendo topologia...")
    net = construirDibujoTopologia(routers, interconexiones, devices, general)
    print("guardando topologia en html")
    net.save_graph("temp.html")
    print("corrigiendo enlaces css y js a forma local...")
    cambiarEnlaces("temp.html", "templates/network.html", 0)
    cambiarEnlaces("temp.html", "templates/network2.html", 1)
    print("eliminando archivo temporal de topologia")
    eliminarTemporal("temp.html")
    print("fin de dibujo")
