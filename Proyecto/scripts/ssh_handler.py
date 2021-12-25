#!/usr/bin/env python3
import netmiko
import paramiko,getpass,time

username="admin"
password="admin"
max_buffer=65535
def clear_buffer(connection):
    if connection.recv_ready():
        return connection.recv(max_buffer)
"""
    @args:
        <cisco> Es el diccionario que contiene los datos para la conexion
        <cmd> Es la lista de comandos que va a ejecutar netmiko
"""
def conectar(ip,cmd,config):
    net_connect = netmiko.ConnectHandler(ip=ip,device_type="cisco_ios",username='admin',password='admin')
    output=[]
    if(config == 0):
        for i in range(len(cmd)):
            output.append(net_connect.send_command(cmd[i]))
    else:
        for i in range(len(cmd)):
            output.append(net_connect.send_config_set(cmd[i]))
    net_connect.disconnect()
    return output

def activarOSPF(dispositivos):
    pOcteto = []
    allip = []
    if dispositivos != None:
        for fila in dispositivos:
            ips = fila[2]
            ip = ips.split(sep=",")[0]
            p = ip.split(sep=".")[0]
            if p not in pOcteto:
                pOcteto.append(p)
            allip.append(ip)
        comandos = ['conf t','router ospf 1']
        for net in pOcteto:
            comandos.append('network '+ net +'.0.0.0 0.0.0.255 area 0')
        comandos.append('exit')
        comandos.append('exit')
        for ip in allip:
            connection=paramiko.SSHClient()
            connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            connection.connect(ip,username='admin',password='admin',look_for_keys=False,allow_agent=False)
            new_connection=connection.invoke_shell()
            output=clear_buffer(new_connection)
            time.sleep(2)
            for line in comandos:
                new_connection.send(line.rstrip()+"\n")
                time.sleep(2)
                output=new_connection.recv(max_buffer)
                output=clear_buffer(new_connection)
            new_connection.close()
        for ip in allip:
            connection=paramiko.SSHClient()
            connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            connection.connect(ip,username=username,password=password,look_for_keys=False,allow_agent=False)
            new_connection=connection.invoke_shell()
            output=clear_buffer(new_connection)
            time.sleep(2)
            for line in ['conf t','no router rip','no router eigrp 1','exit','exit']:
                print(line)
                new_connection.send(line.rstrip()+"\n")
                time.sleep(2)
                output=new_connection.recv(max_buffer)
                output=clear_buffer(new_connection)
            new_connection.close()

def activarRIP(dispositivos):
    pOcteto = []
    allip = []
    if dispositivos != None:
        for fila in dispositivos:
            ips = fila[2]
            ip = ips.split(sep=",")[0]
            p = ip.split(sep=".")[0]
            if p not in pOcteto:
                pOcteto.append(p)
            allip.append(ip)
        comandos = ['router rip','version 2','no auto-summary']
        for net in pOcteto:
            comandos.append('network '+ net)
        for ip in allip:
            conectar(ip,comandos,1)
        for ip in allip:
            conectar(ip,['no router ospf 1','no router eigrp 1'],1)

def activarEIGRP(dispositivos):
    pOcteto = []
    allip = []
    if dispositivos != None:
        for fila in dispositivos:
            ips = fila[2]
            ip = ips.split(sep=",")[0]
            p = ip.split(sep=".")[0]
            if p not in pOcteto:
                pOcteto.append(p)
            allip.append(ip)
        comandos = ['router eigrp 1']
        for net in pOcteto:
            comandos.append('network '+ net +'.0.0.0 0.0.0.255')
        for ip in allip:
            conectar(ip,comandos,1)
        for ip in allip:
            conectar(ip,['no router ospf 1','no router rip'],1)

def levantaSSH(dispositivos,responsable,psw,privilegio,sshusr):
    if dispositivos != None:
        for fila in dispositivos:
            ips = fila[2]
            ip = ips.split(sep=",")[0]
            comandos = ['username '+ sshusr +' privilege '+ privilegio +' password '+psw]
            conectar(ip,comandos,1)
            conectar(ip,['wr'],0)

def deleteSSH(dispositivos,psw,sshusr):
    if dispositivos != None:
        for fila in dispositivos:
            ips = fila[2]
            ip = ips.split(sep=",")[0]
            comandos = ['no username '+ sshusr +' password '+psw]
            conectar(ip,comandos,1)
            conectar(ip,['wr'],0)

def actaulizarSSH(dispositivos,psw, lvl ,sshusr,pswold):
    if dispositivos != None:
        for fila in dispositivos:
            ips = fila[2]
            ip = ips.split(sep=",")[0]
            comandos = ['no username '+ sshusr +' password '+pswold,'username '+ sshusr +' privilege '+lvl+' password '+psw]
            conectar(ip,comandos,1)
            conectar(ip,['wr'],0)
