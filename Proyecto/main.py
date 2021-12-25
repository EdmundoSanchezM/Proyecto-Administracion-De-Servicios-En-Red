from flask import Flask
from flask_mail import Mail, Message
from flask import request, render_template, url_for, redirect, flash, session, jsonify
from scripts.scanner import *
from scripts.correos import *
from scripts.db import *
from scripts.ssh_handler import *
import os
import sys
import time
import scripts.down_protocols as down
import scripts.levanta_eigrp as eigrp
import scripts.levanta_ospf as ospf
import scripts.levanta_rip as rip
import scripts.levanta_snmp as snmp
import scripts.redes_operaciones as redes_operaciones
from scripts.dispositivos import *
from scripts.get_snmp import *
from scripts.set_snmp import *
import scripts.detectared as detectanred
import matplotlib.pyplot as plt
from os import path
import scripts.ownsnmp as snmpall
import threading  
import requests
lost = ""
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = 'qewqeeqq'

# configuracion de email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = 'XXXXXX'
app.config['MAIL_PASSWORD'] = "XXXXXX"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
mail2 = Mail(app)
conexiones_global = {}

def hilito(ip):
    while True:
        lost = snmpall.getPaquetes(ip)
        time.sleep(30)


@app.route('/send-email', methods=['POST'])
def send_email():
    if request.method == "POST":
        # json_data = flask.request.json
        # destinatario = json_data["destinatario"]
        # asunto = json_data["asunto"]
        print(session)
        cuerpo = request.form["cuerpo"]
        print(cuerpo)
        if 'email' in session:
            destinatario = session['email']
        else:
            destinatario = 'xxxxx@gmail.com'
        asunto = "Alerta"
        correo = crear_correo(app.config.get("MAIL_USERNAME"),
                              destinatario, asunto, cuerpo)
        mail.send(correo)
        print("correo enviado")
        return jsonify("sucess")


# ------------------------------ >   Menu publico  < ------------------------------

"""
    Ruta Inicial del proyecto, solo muetra nuestros nombres
"""


@app.route('/', methods=['POST', 'GET'])
def inicio():
    return render_template('index.html')


"""
    Ruta que carga el login del proyecto
"""


@app.route('/login', methods=['POST', 'GET'])
def login():
    session.clear()
    if request.method == 'POST':
        email = request.form['email']
        psw = request.form['clave']
        conexion = conecta_db("Proyecto.db")
        respuesta = valida_login(conexion, email, psw, 1)
        if respuesta == "Administrador":
            session["idTipoUsr"] = 0
            session["nom"] = regresa_nombre(conexion, email)
            session["email"] = email
            session["gateway"]= redes_operaciones.get_gateway()
            return respuesta
        if respuesta == "Cliente":
            session["idTipoUsr"] = 1
            session["nom"] = regresa_nombre(conexion, email)
            session["email"] = email
            #session["gateway"]= redes_operaciones.get_gateway()
            return respuesta
        if respuesta == "Invalido":
            return respuesta
        close_db(conexion)
    else:
        return render_template('login.html')


"""
    Ruta que sirve para dar de alta usuarios del tipo cliente
"""


@app.route('/registerUser', methods=['POST', 'GET'])
def registerUser():
    session.clear()
    if request.method == 'POST':
        nom = request.form['nombre']
        apep = request.form['appaterno']
        apem = request.form['apmaterno']
        telefono = request.form['cel']
        psw = request.form['contra']
        email = request.form['email']
        conexion = conecta_db("Proyecto.db")
        respuesta = alta_usur(conexion, email, nom, apep,
                              apem, telefono, psw, 1)
        close_db(conexion)
        return respuesta
    return render_template('registro.html')

# --------------------------------------------------------------------------------

# ------------------------------ >  Menu Administrador  < ------------------------------


"""
    Rescanear toda la red y configura protocolos
"""


@app.route('/topologia', methods=['POST', 'GET'])
def topologia():

    try:
        usr = session["idTipoUsr"]
        if(usr != 0):		
            return redirect(url_for("login"))
        else:
            if request.method == 'POST':
                opc = request.form['opc']
                gateway = '10.0.1.254'
                if(opc=='1'):
                    conexion = conecta_db("Proyecto.db")
                    inserta_bitacora(conexion,'Se empezo a scanear la red','xxxxx@gmail.com')
                    close_db(conexion)
                    uwut = request.form['timeER']
                    if len(uwut)<1:
                        uwut = 1
                    print(uwut)
                    while True:    
                        main_router = detectanred.Router('R1', gateway)
                        routers, topology = detectanred.get_topology(main_router)
                        for router in routers:
                            print(router)
                        if(path.exists('/home/edmundojsm/Escritorio/Proyecto/FLASKuwu/scripts/uwu.txt')): 
                            mensaje = detectanred.exits_changes(routers)
                            if(len(mensaje)>36):
                                conexion = conecta_db("Proyecto.db")
                                inserta_bitacora(conexion,mensaje,'xxxxx@gmail.com')
                                close_db(conexion)
                        else:
                            conexion = conecta_db("Proyecto.db")
                            print('Registrando routers')
                            registrarRouters(conexion, routers)
                            snmpall.saveDataR(conexion)
                            close_db(conexion)
                        with open('/home/edmundojsm/Escritorio/Proyecto/FLASKuwu/scripts/uwu.txt', "w") as myfile:
                            i = 0
                            for router in routers:
                                if i == len(routers)-1:
                                    myfile.write(router.destination_host.partition(".")[0]+":"+main_router.management_ip)
                                elif i!=0:
                                    myfile.write(router.destination_host.partition(".")[0]+":"+router.management_ip + "\n")
                                i=1+i
                        time.sleep(60 * uwut)
                    pass
                elif(opc == '2'):
                    # RIP
                    # mandar llamar limpiar protcocolos
                    print("RIP")
                    down.init_configure(gateway)
                    rip.init_configure(gateway)
                    pass
                elif(opc == '3'):
                    # OSPF
                    print("OSPF")
                    down.init_configure(gateway)
                    ospf.init_configure(gateway)
                    pass
                elif(opc == '4'):
                    # EIGRP
                    print("EIGRP")
                    down.init_configure(gateway)
                    eogrp.init_configure(gateway)
                    pass
                elif(opc == '5'):
                    # EIGRP
                    print("SNMP")
                    snmp.init_configure(gateway)
                    pass
                elif(opc == '6'):
                    # EIGRP
                    print("owo")
                    pass
            #conexion = conecta_db("Proyecto.db")
            #numalertas = cantidad_alertas_NoVistas(conexion,session["email"])
            return render_template('topologia.html', nombrecito=session["nom"], numAlertas=0)

    except Exception as e:
        print(e)
        return redirect(url_for("login"))


"""
    Gestiona Administradores - Menu
"""


@app.route('/gestionAdmin', methods=['POST', 'GET'])
def gestionAdmin():

    try:
        usr = session["idTipoUsr"]
        if(usr != 0):
            return redirect(url_for("login"))
        else:
            conexion = conecta_db("Proyecto.db")
            respuesta = consulta_usur(conexion, 0)
            #numalertas = cantidad_alertas_NoVistas(conexion,session["email"])
            close_db(conexion)
            return render_template('verAdm.html', filas=respuesta, nombrecito=session["nom"], numAlertas=0)

    except Exception as e:
        print(e)
        return redirect(url_for("login"))


"""
    Gestiona Administradores - Form Agregar
"""


@app.route('/adm11', methods=['POST', 'GET'])
def adm11():

    try:
        usr = session["idTipoUsr"]
        if(usr != 0):
            return redirect(url_for("login"))
        else:
            if request.method == 'POST':
                usr = request.form['usr']
                psw = request.form['psw']
                nom = request.form['nom']
                ap1 = request.form['ap1']
                ap2 = request.form['ap2']
                gen = request.form['gen']
                ema = request.form['ema']
                conexion = conecta_db("Proyecto.db")
                respuesta = alta_usur(conexion, ema, usr,
                                      psw, nom, ap1, ap2, gen, 1)
                print(inserta_bitacora(
                    conexion, 'Administrador Registrado', session["email"]))
                close_db(conexion)
                return respuesta

    except Exception as e:
        print(e)
        return redirect(url_for("login"))

    conexion = conecta_db("Proyecto.db")
    numalertas = cantidad_alertas_NoVistas(conexion, session["email"])
    return render_template('Adm11.html', nombrecito=session["nom"], numAlertas=numalertas[0])


"""
    Gestiona Administradores - Tabla Busca
"""


@app.route('/adm12', methods=['POST', 'GET'])
def adm12():

    try:
        usr = session["idTipoUsr"]
        if(usr != 0):
            return redirect(url_for("login"))
        else:
            conexion = conecta_db("Proyecto.db")
            respuesta = consulta_usur(conexion, 1)
            #numalertas = cantidad_alertas_NoVistas(conexion,session["email"])
            return render_template('Adm12.html', filas=respuesta, nombrecito=session["nom"], numAlertas=10)

    except Exception as e:
        print(e)
        return redirect(url_for("login"))


"""
    Gestiona Administradores - Form modifica
"""


@app.route('/modAdmin', methods=['POST', 'GET'])
def modAdmin():

    try:
        usr = session["idTipoUsr"]
        if(usr != 0):
            return redirect(url_for("login"))
        else:
            if request.method == 'POST':
                usr = request.form['usr']
                conexion = conecta_db("Proyecto.db")
                respuesta = consulta_usur_esp(conexion, usr)
                #numalertas = cantidad_alertas_NoVistas(conexion,session["email"])
                return render_template('modificarAdmin.html', filas=respuesta, nombrecito=session["nom"], numAlertas=0)

    except Exception as e:
        print(e)
        return redirect(url_for("login"))


"""
    Gestiona Administradores - Metodo modifica
"""


@app.route('/modificarAdmin', methods=['POST', 'GET'])
def modificarAdmin():

    try:
        usr = session["idTipoUsr"]
        if(usr != 0):
            return redirect(url_for("login"))
        else:
            if request.method == 'POST':
                psw = request.form['psw']
                cel = request.form['cel']
                ema = request.form['ema']
                conexion = conecta_db("Proyecto.db")
                respuesta = cambio_usur(conexion, psw, cel, ema)
                #print(inserta_bitacora(conexion,'Administrador Modificado',session["email"]))
                close_db(conexion)
                return respuesta

    except Exception as e:
        print(e)
        return redirect(url_for("login"))


"""
    Gestiona Administradores - Metodo eliminar
"""


@app.route('/borrarAdmin', methods=['POST', 'GET'])
def borrarAdmin():

    try:
        usr = session["idTipoUsr"]
        if(usr != 0):
            return redirect(url_for("login"))
        else:
            if request.method == 'POST':
                usr = request.form['ema']
                conexion = conecta_db("Proyecto.db")
                respuesta = elimina_usur(conexion, usr)
                #print(inserta_bitacora(conexion,'Persona Eliminada',session["email"]))
                close_db(conexion)
                return respuesta

    except Exception as e:
        return redirect(url_for("login"))


"""
    Gestiona Clientes - Menu
"""


@app.route('/gestionUsuarios', methods=['POST', 'GET'])
def gestionUsuarios():
    try:
        usr = session["idTipoUsr"]
        if(usr != 0):
            return redirect(url_for("login"))
        else:
            conexion = conecta_db("Proyecto.db")
            respuesta = consulta_usur(conexion, 1)
            #numalertas = cantidad_alertas_NoVistas(conexion, session["email"])
            return render_template('verUsuarios.html', filas=respuesta, nombrecito=session["nom"], numAlertas=0)

    except Exception as e:
        print(e)
        return redirect(url_for("login"))


"""
    Gestiona Clientes - Agrega Usuario
"""


@app.route('/gestionSSH', methods=['POST', 'GET'])
def gestionSSH():
    try:
        usr = session["idTipoUsr"]
        if(usr != 0):
            return redirect(url_for("login"))
        else:
            conexion = conecta_db("Proyecto.db")
            respuesta = consulta_SSH(conexion)
            #numalertas = cantidad_alertas_NoVistas(conexion, session["email"])
            return render_template('verSSH.html', filas=respuesta, nombrecito=session["nom"], numAlertas=0)

    except Exception as e:
        print(e)
        return redirect(url_for("login"))


"""
    Add SSH
"""


@app.route('/addSSH', methods=['POST', 'GET'])
def addSSH():

    try:
        usr = session["idTipoUsr"]
        if(usr != 0):
            return redirect(url_for("login"))
        else:
            conexion = conecta_db("Proyecto.db")
            respuesta = consulta_usur(conexion, 0)
            respuesta2 = consulta_usur(conexion, 1)
            #numalertas = cantidad_alertas_NoVistas(conexion, session["email"])
            return render_template('addSSH.html', filas=respuesta, filas2=respuesta2, nombrecito=session["nom"], numAlertas=0)

    except Exception as e:
        print(e)
        return redirect(url_for("login"))

@app.route('/borrarUsuarioSSH', methods=['POST', 'GET'])
def borrarUsuarioSSH():

    try:
        usr = session["idTipoUsr"]
        if(usr != 0):
            return redirect(url_for("login"))
        else:
            if request.method == 'POST':
                usr = request.form['ema']
                psw = request.form['psw']
                conexion = conecta_db("Proyecto.db")
                respuesta = elimina_ssh_user(conexion,usr)
                dispositivos = consulta_disp(conexion)
                if(respuesta != "La persona ya no existe en el sistema"):
                    deleteSSH(dispositivos,psw,usr)
                #print(inserta_bitacora(conexion,'Administrador Modificado',session["email"]))
                #print(inserta_bitacora(conexion,'Persona Eliminada',session["email"]))
                close_db(conexion)
                return respuesta

    except Exception as e:
        return redirect(url_for("login"))

"""
    Gestiona Clientes - Form modifica Clientes
"""


@app.route('/modUser', methods=['POST', 'GET'])
def modUser():
    try:
        usr = session["idTipoUsr"]
        if(usr != 0):
            return redirect(url_for("login"))
        else:
            if request.method == 'POST':
                usr = request.form['usr']
                conexion = conecta_db("Proyecto.db")
                respuesta = consulta_usur_esp(conexion, usr)
                # numalertas = cantidad_alertas_NoVistas(
                #    conexion, session["email"])
                return render_template('modificarUsr.html', filas=respuesta, nombrecito=session["nom"], numAlertas=0)

    except Exception as e:
        print(e)
        return redirect(url_for("login"))

@app.route('/modUserSSH', methods=['POST', 'GET'])
def modUserSSH():
    try:
        usr = session["idTipoUsr"]
        if(usr != 0):
            return redirect(url_for("login"))
        else:
            if request.method == 'POST':
                email = request.form['usr']
                usr = request.form['uwu']
                conexion = conecta_db("Proyecto.db")
                respuesta = consulta_usur_ssh(conexion, email, usr)
                # numalertas = cantidad_alertas_NoVistas(
                #    conexion, session["email"])
                return render_template('modificarSSH.html', filas=respuesta, nombrecito=session["nom"], numAlertas=0)

    except Exception as e:
        print(e)
        return redirect(url_for("login"))

"""
    Gestiona Clientes - Metodo modifica
"""


@app.route('/modificarUsuario', methods=['POST', 'GET'])
def modificarUsuario():

    try:
        usr = session["idTipoUsr"]
        if(usr != 0):
            return redirect(url_for("login"))
        else:
            if request.method == 'POST':
                psw = request.form['psw']
                cel = request.form['cel']
                ema = request.form['ema']
                conexion = conecta_db("Proyecto.db")
                respuesta = cambio_usur(conexion, psw, cel, ema)
                #print(inserta_bitacora(conexion,'Administrador Modificado',session["email"]))
                close_db(conexion)
                return respuesta

    except Exception as e:
        print(e)
        return redirect(url_for("login"))

@app.route('/modificarUsuarioSSH', methods=['POST', 'GET'])
def modificarUsuarioSSH():

    try:
        usr = session["idTipoUsr"]
        if(usr != 0):
            return redirect(url_for("login"))
        else:
            if request.method == 'POST':
                psw = request.form['psw']
                priv = request.form['priv']
                usr = request.form['usr']
                pswold = request.form['pswold']
                conexion = conecta_db("Proyecto.db")
                respuesta = cambio_usur_ssh(conexion, psw, priv, usr)
                dispositivos = consulta_disp(conexion)
                actaulizarSSH(dispositivos,psw,priv,usr,pswold)
                #print(inserta_bitacora(conexion,'Administrador Modificado',session["email"]))
                close_db(conexion)
                return respuesta

    except Exception as e:
        print(e)
        return redirect(url_for("login"))
@app.route('/addUsuarioSSH', methods=['POST', 'GET'])
def addUsuarioSSH():

    try:
        usr = session["idTipoUsr"]
        if(usr != 0):
            return redirect(url_for("login"))
        else:
            if request.method == 'POST':
                psw = request.form['psw']
                privilegio = request.form['privilegio']
                sshusr = request.form['nombre']
                responsable = request.form['responsable']
                conexion = conecta_db("Proyecto.db")
                respuesta = alta_ssh_user(conexion,responsable,psw,privilegio,sshusr)
                dispositivos = consulta_disp(conexion)
                if(respuesta == "Usuario ssh registrado"):
                    levantaSSH(dispositivos,responsable,psw,privilegio,sshusr)
                #print(inserta_bitacora(conexion,'Administrador Modificado',session["email"]))
                close_db(conexion)
                return respuesta
    except Exception as e:
        print(e)
        return redirect(url_for("login"))


"""
    Gestiona Clientes - Form elimina Clientes
"""


@app.route('/borrarUsuarios', methods=['POST', 'GET'])
def borrarUsuarios():

    try:
        usr = session["idTipoUsr"]
        if(usr != 0):
            return redirect(url_for("login"))
        else:
            usr = request.form['ema']
            conexion = conecta_db("Proyecto.db")
            respuesta = elimina_usur(conexion, usr)
            return respuesta

    except Exception as e:
        print(e)
        return redirect(url_for("login"))


@app.route('/admin_usr_admin', methods=['POST'])
def admin_usr_admin():
    try:
        usr = session["idTipoUsr"]
        if(usr != 0):
            return redirect(url_for("login"))
        else:
            usr = request.form['ema']
            tipo = request.form['tipo']
            conexion = conecta_db("Proyecto.db")
            respuesta = bdadmin_usr_admin(conexion, usr, tipo)
            return respuesta
    except Exception as e:
        print(e)
        return redirect(url_for("login"))

#  ------------------------------ Topologia ----------------------------


@app.route('/adm3', methods=['POST', 'GET'])
def adm3():
    try:
        #conexion = conecta_db("Proyecto.db")
        #respuesta = consulta_usur(conexion, 2)
        #numalertas = cantidad_alertas_NoVistas(conexion, session["email"])
        #print(inserta_bitacora(
        #    conexion, 'Consulto Topologia', session["email"]))
        return render_template('network.html', nombrecito=session["nom"], numAlertas=0)
    except Exception as e:
        print(e)
        return redirect(url_for("login"))


"""
    Dispositivos - Muestra dispositivos
"""


@app.route('/verDispositivos', methods=['POST', 'GET'])
def verDispositivos():

    try:
        usr = session["idTipoUsr"]
        if(usr != 0):
            return redirect(url_for("login"))
        else:
            conexion = conecta_db("Proyecto.db")
            respuesta = consulta_disp(conexion)
            #numalertas = cantidad_alertas_NoVistas(conexion, session["email"])
            # print(inserta_bitacora(
            #   conexion, 'Consulto Dispositivos', session["email"]))
            return render_template('verDispositivos.html', filas=respuesta, nombrecito=session["nom"], numAlertas=0)

    except Exception as e:
        print(e)
        return redirect(url_for("login"))


"""
    Dispositivos - Dispositivos especifico
"""


@app.route('/adm41', methods=['POST', 'GET'])
def adm41():
    try:
        usr = session["idTipoUsr"]
        if(usr != 0):
            return redirect(url_for("login"))
        else:
            if request.method == 'POST':
                if request.method == 'POST':
                    datos = list()
                    interfaces = list()
                    idDisp=request.form['idDisp']
                    conexion = conecta_db("Proyecto.db")
                    respuesta = consulta_disp_esp(conexion,idDisp)
                    inter = getInterfaz(conexion, idDisp)
                    for elemento in inter:
                        interfaces.append(elemento)
                    for elemento in respuesta:
                        datos.append(elemento[0]) #idDisp
                        datos.append(elemento[1])
                        datos.append(elemento[2]) #sistem
                        datos.append(elemento[3]) #locali
                        datos.append(elemento[4]) #encarg
                    
                    inserta_bitacora(conexion,'Obteniendo datos del router con id ' + str(elemento[0]),'xxxxx@gmail.com')
                    #respuesta = alertas_activas(conexion,elemento[0],session["email"])
                #datos.append(respuesta[0]) #datos[8] = edo_alertas     
                return render_template('Adm41.html', filas=datos, allInterfaces = interfaces, nombrecito=session["nom"], email=session["email"], numAlertas=0)

    except Exception as e:
        print(e)
        return redirect(url_for("login"))



"""
    Interfaz
"""


@app.route('/interfazES', methods=['POST', 'GET'])
def interfazES():
    try:
        usr = session["idTipoUsr"]
        if(usr != 0):
            return redirect(url_for("login"))
        else:
            if request.method == 'POST':
                datos = list()
                paquetes = list()
                idDisp=request.form['ip']
                porcentaje=request.form['paq']
                conexion = conecta_db("Proyecto.db")
                respuesta = getInfoInterfaz(conexion,idDisp)
                    
                for elemento in respuesta:
                    datos.append(elemento[0]) 
                    datos.append(elemento[1]) 
                    datos.append(elemento[2]) 
                    datos.append(elemento[3]) 
                    datos.append(elemento[4]) 
                    datos.append(elemento[5]) 
                    datos.append(elemento[6]) 
                    datos.append(elemento[7]) 
                    datos.append(elemento[8])
                    datos.append(elemento[9])
                    datos.append(elemento[10])
                if len(porcentaje)<1:
                    porcentaje = 50
                print(porcentaje)
                inserta_bitacora(conexion,'Obteniendo datos de la interfaz con id ' + str(elemento[0]),'xxxxx@gmail.com')
                print(paquetes)  
                paquetitos = getPaq(conexion,idDisp)
                for infor in paquetitos:
                    paquetes.append(infor)
                close_db(conexion)
                download_thread = threading.Thread(target=hilito, name="Downloader", args=[datos[2]])
                download_thread.start()
                return render_template('verIntData.html', filas=datos, uwup = paquetes,nombrecito=session["nom"], email=session["email"], numAlertas=0, lostp = lost)       
                    #respuesta = alertas_activas(conexion,elemento[0],session["email"])
                #datos.append(respuesta[0]) #datos[8] = edo_alertas     
                return render_template('verIntData.html', filas=datos, nombrecito=session["nom"], email=session["email"], numAlertas=0)
    except Exception as e:
        print(e)
        return redirect(url_for("login"))


"""
    Dispositivos - Gestiona alertas
"""


@app.route('/adm411', methods=['POST', 'GET'])
def adm411():

    try:
        usr = session["idTipoUsr"]
        if(usr != 1):
            return redirect(url_for("login"))
        else:
            if request.method == 'POST':
                idDisp = request.form['idDisp']
                email = request.form['email']
                conexion = conecta_db("Proyecto.db")
                respuesta = config_alertas(conexion, idDisp, email)
                if(respuesta == "Alertas Desactivadas"):
                    # Desactiva notificaciones
                    pass
                elif(respuesta == "Alertas Activadas"):
                    # activa notificaciones
                    pass
                elif(respuesta == "Persona registrada para recibir notificaciones"):
                    # activa notificaciones
                    pass
                # print(respuesta)
                return respuesta

    except Exception as e:
        print(e)
        return redirect(url_for("login"))


"""
    Dispositivos - Form Modifica Routers
"""


@app.route('/modRouters', methods=['POST', 'GET'])
def modRouters():

    try:
        usr = session["idTipoUsr"]
        if(usr != 0):
            return redirect(url_for("login"))
        else:
            if request.method == 'POST':
                datos = list()
                idDisp = request.form['idDisp']
                nombre = request.form['nombre']
                locali = request.form['loca']
                encarg = request.form['resp']
                datos.append(idDisp)
                datos.append(nombre)
                datos.append(locali)
                datos.append(encarg)
                print(datos)
                conexion = conecta_db("Proyecto.db")
                inserta_bitacora(conexion,'Modificando datos del router con id ' + str(idDisp),'xxxxx@gmail.com')
                detectanred.enviaemail('Modificando datos del router con id ' + str(idDisp))
                return snmpall.actaulizarRSNMP(conexion,datos)

    except Exception as e:
        print(e)
        return redirect(url_for("login"))


"""
    Dispositivos - Metodo Modifica Routers
"""


@app.route('/adm413', methods=['POST', 'GET'])
def adm413():
    try:
        usr = session["idTipoUsr"]
        if(usr != 1):
            return redirect(url_for("login"))
        else:
            if request.method == 'POST':
                datos = list()
                # Este parametro no se modifica
                nombre = request.form['nombre']
                sistem = request.form['sistem']
                locali = request.form['locali']
                encarg = request.form['encarg']
                contac = request.form['contac']
                idDisp = request.form['idDisp']
                datos.append(sistem)
                datos.append(locali)
                datos.append(contac)
                datos.append(idDisp)  # El id va al final
                # conexion a snmp
                conexion = conecta_db("Proyecto.db")
                respuesta = modifica_disp(conexion, datos)
                print("conexion exitosa")

                try:
                    # global conexiones_global
                    # print(conexiones_global)
                    conexiones_dispositivos = None
                    with open('data.json') as json_file:
                        conexiones_dispositivos = json.load(json_file)

                    # Print the type of data variable
                    print(conexiones_dispositivos[nombre])

                    actualizar_datos_dispositivo(
                        conexiones_dispositivos[nombre], nombre, locali, contac, sistem)
                    print("actualizar datos snmp")
                    # Area de alertas
                    pregunta_alertas = consult_edo_alertas(
                        conexion, idDisp, session["email"]).fetchone()
                    if (pregunta_alertas != None):
                        if(pregunta_alertas[0] == 1):
                            print(regis_alerta(
                                conexion, idDisp, session["email"], 'Informacion del router {} ha sido actualizada'.format(idDisp)))
                    print(inserta_bitacora(
                        conexion, 'Modificacion SNMP a un Router', session["email"]))
                    close_db(conexion)
                    return respuesta
                except Exception as e:
                    print("413:", e)
                    pass

                # Poner Funcion que modifique estos parametros en el router 'nombre'
                return respuesta

    except Exception as e:
        print(e)
        return redirect(url_for("login"))


"""
    Dispositivos - Historial notificaciones
"""


@app.route('/adm5', methods=['POST', 'GET'])
def adm5():

    try:
        usr = session["idTipoUsr"]
        if(usr != 1):
            return redirect(url_for("login"))
        else:
            dato = list()
            conexion = conecta_db("Proyecto.db")
            respuesta = (cantidad_alertas_NoVistas(
                conexion, session["email"]))[0]
            numalertas = (cantidad_alertas(conexion, session["email"]))[0]
            if(numalertas != 0):
                alertas = consul_alertas(conexion, session["email"])
                for i in alertas:
                    dato.append(i)
            else:
                alertas = None

            print(inserta_bitacora(
                conexion, 'El Usuario Vio Sus Alertas', session["email"]))
            print(set_alertas_visto(conexion, session["email"]))
            return render_template('Adm5.html', nombrecito=session["nom"], Alertas=numalertas, numAlertas=respuesta, datitos=dato)

    except Exception as e:
        print(e)
        return redirect(url_for("login"))


"""
    Dispositivos - Historial bitacoras
"""


@app.route('/adm6', methods=['POST', 'GET'])
def adm6():

    try:
        usr = session["idTipoUsr"]
        if(usr != 0):
            return redirect(url_for("login"))
        else:
            dato = list()
            conexion = conecta_db("Proyecto.db")
            

            bitacoras = consulta_bitacora(conexion)

            return render_template('Bitacora.html', nombrecito=session["nom"], numAlertas=0,  tablita=bitacoras)

    except Exception as e:
        print(e)
        return redirect(url_for("login"))

# --------------------------------------------------------------------------------


# ------------------------------ >  Menu Cliente  < ------------------------------


@app.route('/usr0', methods=['POST', 'GET'])
def usr0():

    try:
        usr = session["idTipoUsr"]
        if(usr != 1):
            return redirect(url_for("login"))
        else:
            pass

    except Exception as e:
        return redirect(url_for("login"))

    return render_template('Usr0.html')


@app.route('/usr1', methods=['POST', 'GET'])
def usr1():

    try:
        usr = session["idTipoUsr"]
        if(usr != 2):
            return redirect(url_for("login"))
        else:
            pass

        try:
            conexion = conecta_db("Proyecto.db")
            respuesta = consulta_usur(conexion, 2)
            numalertas = cantidad_alertas_NoVistas(conexion, session["email"])
            return render_template('network2.html', nombrecito=session["nom"], numAlertas=numalertas[0])
        except Exception as e:
            print(e)
            return redirect(url_for("login"))
    except Exception as e:
        return redirect(url_for("login"))


@app.route('/usr2', methods=['POST', 'GET'])
def usr2():

    try:
        usr = session["idTipoUsr"]
        if(usr != 2):
            return redirect(url_for("login"))
        else:
            pass

    except Exception as e:
        return redirect(url_for("login"))

    return render_template('Usr2.html')


@app.route('/usr21', methods=['POST', 'GET'])
def usr21():

    try:
        usr = session["idTipoUsr"]
        if(usr != 2):
            return redirect(url_for("login"))
        else:
            pass

    except Exception as e:
        return redirect(url_for("login"))

    return render_template('Usr21.html')


@app.route('/usr3', methods=['POST', 'GET'])
def usr3():

    try:
        usr = session["idTipoUsr"]
        if(usr != 2):
            return redirect(url_for("login"))
        else:
            pass

    except Exception as e:
        return redirect(url_for("login"))

    return render_template('Usr3.html')


# --------------------------------------------------------------------------------


@app.errorhandler(404)
def error404(error):
    return render_template("404.html")


if __name__ == '__main__':
    conexion = conecta_db("Proyecto.db")
    crea_tbs(conexion)
    close_db(conexion)
    # llamamos al snpm
    # Guardamops los dispositovos en la BD
    app.run(host='0.0.0.0',port=7777, debug=True)
