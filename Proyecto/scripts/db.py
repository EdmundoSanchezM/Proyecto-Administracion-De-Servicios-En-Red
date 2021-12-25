import sqlite3
import datetime

def conecta_db(name):
	return sqlite3.connect(name)

def close_db(conexion):
	conexion.close()

def crea_tbs(conexion):
    cursor_tb = conexion.cursor()
    cursor_tb.execute(
			"""
				create table if not exists tipoUsr(
					idTipoUsr integer not null primary key,
					descrip text not null
				)
			"""
	)
    cursor_tb.execute(
			"""
				create table if not exists persona(
					email text not null primary key,
					nombre text not null,
					apaterno text not null,
					amaterno text not null,
					telefono integer not null,
					idTipoUsr integer not null,
					contra text not null,
					foreign key(idTipoUsr) references tipoUsr(idTipoUsr)
				)
			"""
	)
    cursor_tb.execute(
			"""
				create table if not exists dispositivos(
					modelo text not null,
					nombre text not null primary key,
					ips text not null
				)
			"""
		)
    cursor_tb.execute(
			"""
				create table if not exists sshusers(
					email text not null,
					password text not null,
					lvlprivilegio integer not null,					
					username text not null primary key,
					foreign key(email) references persona(email)
				)
			"""
		)
    cursor_tb.execute(
			"""
				create table if not exists routersnmp(
					modelo text not null ,
					nombre text not null,
					ip text not null primary key
				)
			"""
		)
    cursor_tb.execute(
			"""
				create table if not exists inforsnmp(
					ip text not null primary key,
					nombre text not null,
					sistem text not null,
					locali text not null,					
					contac text not null
				)
			"""
		)
    cursor_tb.execute(
			"""
				create table if not exists rep_sistema(
					idRepor integer not null primary key,
					Actividad text not null,
					email text not null,
					fecha timestamp default current_timestamp
				)
			"""
		)
    cursor_tb.execute(
			"""
				create table if not exists interfaces(
					router_id  text not null,
					name text not null,
					ip text not null,
					net text not null,
                    mask text not null,
                    if_mtu text not null,
                    if_speed text not null,
                    if_physaddress text not null,
                    if_adminstatus text not null,
                    if_operstatus text not null,
                    mib_index text not null
				)
			"""
		)
    cursor_tb.execute(
			"""
				create table if not exists paquetes(
					ip_p  text not null,
					ip_d text not null,
					enviados text not null,
					recibidos text not null,
                    danadosE text not null,
                    danadosR text not null,
                    tiempo text not null
				)
			"""
		)
    # Ingresamos los tipos de usuario que tendra el sistema
    llena_cats(conexion,"tipoUsr","idTipoUsr","0",[0,'Administrador'],'idTipoUsr,descrip')
    llena_cats(conexion,"tipoUsr","idTipoUsr","1",[1,'Cliente'],'idTipoUsr,descrip')
    alta_usur(conexion,'xxx@gmail.com','Edmundo Josue','Sanchez','Mendez',7777777777,'xxx',0)#Admin
    alta_ssh_user(conexion,'xxx@gmail.com','admin',15,'admin')#ssh admin
    alta_router(conexion,'cisco_ios','R1','10.0.1.254,10.0.4.254,10.0.7.254,10.0.3.254')
    alta_router(conexion,'cisco_ios','R2','10.0.4.253,10.0.5.254')
    alta_router(conexion,'cisco_ios','R3','10.0.3.253,10.0.9.254,10.0.8.254,10.0.2.254')
    alta_router(conexion,'cisco_ios','R4','10.0.9.253,10.0.6.254')
    alta_router(conexion,'cisco_ios','PRUEBA','10.0.2.253')

def alta_router(conexion, modelo, nombre, ips):
	cursor_tb = conexion.cursor()
	sentencia = "insert OR IGNORE into dispositivos values(?,?,?)"
	cursor_tb.execute(sentencia,(modelo,nombre,ips))
	conexion.commit()

def llena_cats(conexion,tabla,campo,valor,list_data,columnas):
	cursor_tb = conexion.cursor()
	respuesta = cursor_tb.execute("select * from {} where {}={}".format(tabla,campo,valor))
	existencia = respuesta.fetchone()
	if existencia == None:
		sentencia = "insert into {}({}) values(?,?)".format(tabla,columnas)
		cursor_tb.execute(sentencia,list_data)
		conexion.commit()
		# print("Registro exitoso")

def regresa_nombre(conexion,email):
	cursor_tb = conexion.cursor()
	sentencia = "select nombre from persona where email=?"
	respuesta = cursor_tb.execute(sentencia,(email,))
	for fila in respuesta:
		return fila[0]
		
def valida_login(conexion,correo,psw,opc):
	cursor_tb = conexion.cursor()
	if(opc==1):
		sentencia = "select * from persona where email=? and contra=?"
		respuesta = cursor_tb.execute(sentencia,(correo,psw))
	if(opc==2):
		sentencia = "select * from persona where email=?"
		respuesta = cursor_tb.execute(sentencia,(correo,))
	existencia = respuesta.fetchone()
	if existencia != None:				
		sentencia = "select idTipoUsr from persona where email=?"
		respuesta = cursor_tb.execute(sentencia,(correo,))
		if(respuesta.fetchone()[0]==0):
			return "Administrador"
		else:
			return "Cliente"
	else:
		return "Invalido"

def valida_email(conexion,email):
	cursor_tb = conexion.cursor()
	sentencia = "select * from persona where email=?"
	respuesta = cursor_tb.execute(sentencia,(email,))
	existencia = respuesta.fetchone()
	if existencia!=None:
		existe = 1		
	else:
		existe = 0		
	return existe

def alta_usur(conexion,email,nom,apep,apem,telefono,psw,tipo):
	msj = ""
	credenciales = valida_login(conexion,email,psw,2)
	if(credenciales=="Invalido"):
		correo = valida_email(conexion,email)
		if(correo==0):
			cursor_tb = conexion.cursor()
			sentencia = "insert into persona values(?,?,?,?,?,?,?)"
			respuesta = cursor_tb.execute(sentencia,(email,nom,apep,apem,telefono,tipo,psw))
			conexion.commit()
			if(tipo==0):
				msj = "Administrador registrado"
			elif(tipo==1):
				msj = "Cliente registrado"
		elif(correo==1):
			msj = "Existe una persona con ese correo"
	elif(credenciales=="Administrador"):
		msj = "Existe un administrador con ese correo"
	elif(credenciales=="Cliente"):
		msj = "Existe un cliente con ese correo"	
	return msj

def consulta_usur(conexion,tipo):
	cursor_tb = conexion.cursor()
	if(tipo==0):
		sentencia = "select * from persona where idTipoUsr=0"
	elif(tipo==1):
		sentencia = "select * from persona where idTipoUsr=1"
	return cursor_tb.execute(sentencia)

def consulta_SSH(conexion):
	cursor_tb = conexion.cursor()
	sentencia = "select * from sshusers"
	return cursor_tb.execute(sentencia)

def consulta_usur_esp(conexion,usr):
	cursor_tb = conexion.cursor()
	sentencia = "select * from persona where email=?"
	return cursor_tb.execute(sentencia,(usr,))

def consulta_usur_ssh(conexion,email,usr):
	cursor_tb = conexion.cursor()
	sentencia = "select * from sshusers where email=? and username=?"
	return cursor_tb.execute(sentencia,(email,usr))

def valida_ssh_user(conexion,usuario):
	cursor_tb = conexion.cursor()
	sentencia = "select * from sshusers where username=?"
	respuesta = cursor_tb.execute(sentencia,(usuario,))
	existencia = respuesta.fetchone()
	if existencia!=None:
		existe = 1		
	else:
		existe = 0		
	return existe

def valida_user_have_ssh(conexion,email):
	cursor_tb = conexion.cursor()
	sentencia = "select * from sshusers where email=?"
	respuesta = cursor_tb.execute(sentencia,(email,))
	existencia = respuesta.fetchone()
	if existencia!=None:
		existe = 1		
	else:
		existe = 0		
	return existe

def alta_ssh_user(conexion,email,password,lvl,username):
	msj = ""
	ssh_usr_existe = valida_user_have_ssh(conexion,email)
	if(ssh_usr_existe==0):
		usuario = valida_ssh_user(conexion,username)
		if(usuario==0):
			cursor_tb = conexion.cursor()
			sentencia = "insert into sshusers values(?,?,?,?)"
			respuesta = cursor_tb.execute(sentencia,(email,password,lvl,username))
			conexion.commit()
			msj = "Usuario ssh registrado"
		else:
			msj = "Una persona ya tiene ese usuario ssh"
	else:
		msj = "Usted ya tiene usuario ssh registrado, si quiere subirlo de privilegio contacte con los administradores"
	return msj

def cambio_usur(conexion,psw,cel,ema):
	msj = ""
	credenciales = valida_login(conexion,ema,"uwu",2)
	if(credenciales=="Administrador"):		
		cursor_tb = conexion.cursor()
		if(len(psw)!=0):
			sentencia = "update persona set telefono=?, contra = ? where email=?"
			respuesta = cursor_tb.execute(sentencia,(cel, psw, ema))
		else:
			sentencia = "update persona set telefono=? where email=?"
			respuesta = cursor_tb.execute(sentencia,(cel, ema))
		conexion.commit()
		msj = "Administrador {} modificado".format(ema)
	elif(credenciales=="Cliente"):
		cursor_tb = conexion.cursor()
		if(len(psw)!=0):
			sentencia = "update persona set telefono=?, contra = ? where email=?"
			respuesta = cursor_tb.execute(sentencia,(cel, psw, ema))
		else:
			sentencia = "update persona set telefono=? where email=?"
			respuesta = cursor_tb.execute(sentencia,(cel, ema))
		conexion.commit()
		msj = "Cliente {} modificado".format(ema)
	elif(credenciales=="Invalido"):
		msj = "El usuario no existe"

	return msj

def cambio_usur_ssh(conexion, psw, priv, usr):
	msj = ""		
	cursor_tb = conexion.cursor()
	if(len(psw)!=0):
		sentencia = "update sshusers set password=?, lvlprivilegio = ? where username=?"
		respuesta = cursor_tb.execute(sentencia,(psw, priv, usr))
	else:
		sentencia = "update sshusers set lvlprivilegio = ? where username=?"
		respuesta = cursor_tb.execute(sentencia,(priv, usr))
	conexion.commit()
	msj = "Usuario SSH {} modificado".format(usr)
	return msj

def elimina_usur(conexion,usr):
	msj = ""
	cursor_tb = conexion.cursor()
	sentencia = "select * from persona where email=?"
	respuesta = cursor_tb.execute(sentencia,(usr,))
	existencia = respuesta.fetchone()
	if existencia!=None:		
		#sentencia = "delete from credenciales where usr=?"
		#cursor_tb.execute(sentencia,(usr,))
		sentencia = "delete from persona where email=?"
		cursor_tb.execute(sentencia,(usr,))
		conexion.commit()
		print("Persona {} eliminada".format(usr))
	else:
		msj = "La persona ya no existe en el sistema"

	return msj

def elimina_ssh_user(conexion,usr):
	msj = ""
	cursor_tb = conexion.cursor()
	sentencia = "select * from sshusers where username=?"
	respuesta = cursor_tb.execute(sentencia,(usr,))
	existencia = respuesta.fetchone()
	if existencia!=None:		
		#sentencia = "delete from credenciales where usr=?"
		#cursor_tb.execute(sentencia,(usr,))
		sentencia = "delete from sshusers where username=?"
		cursor_tb.execute(sentencia,(usr,))
		conexion.commit()
		print("Usuario SSH {} eliminada".format(usr))
	else:
		msj = "La persona ya no existe en el sistema"

	return msj

def bdadmin_usr_admin(conexion,usr,tipo):
	msj = ""
	cursor_tb = conexion.cursor()
	sentencia = "select * from persona where email=?"
	respuesta = cursor_tb.execute(sentencia,(usr,))
	existencia = respuesta.fetchone()
	if existencia!=None:		
		#sentencia = "delete from credenciales where usr=?"
		#cursor_tb.execute(sentencia,(usr,))
		sentencia = "update persona set idTipoUsr=? where email=?"
		cursor_tb.execute(sentencia,(tipo,usr,))
		conexion.commit()
	else:
		msj = "La persona ya no existe en el sistema"
	return msj

def valida_disp(conexion,idDisp):
	cursor_tb = conexion.cursor()
	sentencia = "select * from dispositivos where idDisp=?"
	respuesta = cursor_tb.execute(sentencia,(idDisp,))
	existencia = respuesta.fetchone()
	if existencia!=None:
		existe = 1		
	else:
		existe = 0
	return existe

def alta_disp(conexion,list_data):
	cursor_tb = conexion.cursor()
	valida = valida_disp(conexion,list_data[0])
	if valida == 0:
		sentencia = "insert into dispositivos(idDisp,nombre,sistem,locali,encarg,contac,timeac,timemo) values(?,?,?,?,?,?,'','')"
		cursor_tb.execute(sentencia,list_data)
		conexion.commit()
		return "Registro exitoso"
	else:
		return "Dispositivo previamente registrado"

def consulta_disp(conexion):
	cursor_tb = conexion.cursor()
	sentencia = "select * from routersnmp"
	return cursor_tb.execute(sentencia)

def consulta_disp_esp(conexion,idDisp):
    cursor_tb = conexion.cursor()
    sentencia = "select * from inforsnmp where ip=?"
    return cursor_tb.execute(sentencia,(idDisp,))

def modifica_disp(conexion,list_data):
	cursor_tb = conexion.cursor()
	sentencia = "update dispositivos set sistem=?, locali=?, contac=?  where idDisp=?"
	cursor_tb.execute(sentencia,list_data)
	conexion.commit()
	return "Dispositivo modificado"

def inserta_paquetes(conexion,idDisp,paqEnviados,paqPerdidos):
	cursor_tb = conexion.cursor()
	respuesta = cursor_tb.execute("select max(idHist) from historial_paquetes")				
	idReg = respuesta.fetchone()[0]
	if(idReg==None):
		idRegistro=1
	else:
		idRegistro = int(idReg)
		idRegistro = idRegistro+1	
	sentencia = "insert into historial_paquetes(idHist,idDisp,paqEnv,paqPer) values(?,?,?,?)"
	cursor_tb.execute(sentencia,(idRegistro,idDisp,paqEnviados,paqPerdidos))
	conexion.commit()
	return "Registro insertado"

def consulta_paquetes(conexion,idDisp):
	cursor_tb = conexion.cursor()
	sentencia = "select * from historial_paquetes where idDisp=? order by idDisp desc"
	return cursor_tb.execute(sentencia,(idDisp,))	

def consulta_paquete_esp(conexion,idDisp):
	cursor_tb = conexion.cursor()
	respuesta = cursor_tb.execute("select max(idHist) from historial_paquetes where idDisp=?",(idDisp,))	
	idReg = respuesta.fetchone()[0]	
	sentencia = "select paqEnv,paqPer from historial_paquetes where idHist=?"
	respuesta = cursor_tb.execute(sentencia,(idReg,))	
	return respuesta.fetchone()

def alertas_activas(conexion,idDisp,email):
	cursor_tb = conexion.cursor()
	sentencia = "select idEdoCo from control_alertas where idDisp=? and email=?"
	respuesta = cursor_tb.execute(sentencia,(idDisp,email))
	existencia = respuesta.fetchone()
	if existencia == None:		
		return (2,)
	else:
		return existencia

def valida_control(conexion,idDisp,email):
	cursor_tb = conexion.cursor()
	sentencia = "select * from control_alertas where idDisp=? and email=?"
	respuesta = cursor_tb.execute(sentencia,(idDisp,email))
	existencia = respuesta.fetchone()
	if existencia!=None:
		existe = 1		
	else:
		existe = 0
	return existe


def config_alertas(conexion,idDisp,email):
	cursor_tb = conexion.cursor()
	exis_dispo = valida_disp(conexion,idDisp)
	if(exis_dispo==1):
		exis_email = valida_email(conexion,email)
		if(exis_email==1):
			exis_reg = valida_control(conexion,idDisp,email)
			if(exis_reg==1):				
				sentencia = "select idEdoCo from control_alertas where idDisp=? and email=?"
				respuesta = cursor_tb.execute(sentencia,(idDisp,email))
				idstatus = respuesta.fetchone()[0]
				if(idstatus==1):
					sentencia = "update control_alertas set idEdoCo=2 where idDisp=? and email=?"
					respuesta = cursor_tb.execute(sentencia,(idDisp,email))
					conexion.commit()
					return "Alertas Desactivadas"
				elif(idstatus==2):
					sentencia = "update control_alertas set idEdoCo=1 where idDisp=? and email=?"
					respuesta = cursor_tb.execute(sentencia,(idDisp,email))
					conexion.commit()
					return "Alertas Activadas"
			else:				
				respuesta = cursor_tb.execute("select max(idContr) from control_alertas ")				
				idreg = respuesta.fetchone()[0]
				if(idreg==None):
				  	idRegistro=1
				else:
				 	idRegistro = int(idreg)
				 	idRegistro = idRegistro+1				
				sentencia = "insert into control_alertas(idContr,email,idDisp,idEdoCo) values(?,?,?,1)"
				cursor_tb.execute(sentencia,(idRegistro,email,idDisp))
				conexion.commit()
				return "Persona registrada para recibir notificaciones"
		else:
			return "No existe el email"
	else:
		return "No existe el dispositivo"

def consult_edo_alertas(conexion,idDisp,email):
	cursor_tb = conexion.cursor()	
	sentencia = "select idEdoCo from control_alertas where idDisp=? and email=?"
	respuesta = cursor_tb.execute(sentencia,(idDisp,email))	
	return respuesta


def regis_alerta(conexion,idDisp,email,descrip):
	cursor_tb = conexion.cursor()
	exis_dispo = valida_disp(conexion,idDisp)
	if(exis_dispo==1):
		exis_email = valida_email(conexion,email)
		if(exis_email==1):
			respuesta = cursor_tb.execute("select max(idAlert) from alertas ")				
			idreg = respuesta.fetchone()[0]
			if(idreg==None):
				  idRegistro=1
			else:
				 idRegistro = int(idreg)
				 idRegistro = idRegistro+1
			sentencia = "insert into alertas(idAlert,idDisp,email,idEdoAler,descrip) values(?,?,?,1,?)"
			cursor_tb.execute(sentencia,(idRegistro,idDisp,email,descrip))
			conexion.commit()
			return "Alerta Registrada"
		else:
			return "No existe el email"
	else:
		return "No existe el dispositivo"

def consul_alertas(conexion,email):
	cursor_tb = conexion.cursor()	
	cursor_tb = conexion.cursor()
	sentencia = "select * from alertas where email=? order by idAlert desc"
	respuesta = cursor_tb.execute(sentencia,(email,))
	return respuesta

def cantidad_alertas(conexion,email):
	cursor_tb = conexion.cursor()	
	sentencia = "select count(*) from alertas where email=?"
	respuesta = cursor_tb.execute(sentencia,(email,))
	return respuesta.fetchone()

def cantidad_alertas_NoVistas(conexion,email):
	cursor_tb = conexion.cursor()	
	sentencia = "select count(*) from alertas where email=? and idEdoAler=1" #Contamos las alertas que esten en 1 "No vistas"
	respuesta = cursor_tb.execute(sentencia,(email,))
	return respuesta.fetchone()

def set_alertas_visto(conexion,email):
	cursor_tb = conexion.cursor()	
	sentencia = "update alertas set idEdoAler=2 where email=?" #Pasamos las alertas en 2 "Vistas"
	respuesta = cursor_tb.execute(sentencia,(email,))
	conexion.commit()
	return "Alertas dejadas en visto"

def inserta_bitacora(conexion,Actividad,email):
	cursor_tb = conexion.cursor()
	respuesta = cursor_tb.execute("select max(idRepor) from rep_sistema")				
	idReg = respuesta.fetchone()[0]
	if(idReg==None):
		idRegistro=1
	else:
		idRegistro = int(idReg)
		idRegistro = idRegistro+1	
	sentencia = "insert into rep_sistema(idRepor,Actividad,email) values(?,?,?)"
	cursor_tb.execute(sentencia,(idRegistro,Actividad,email))
	conexion.commit()
	return "Bitacora insertada"

def consulta_bitacora(conexion):
	cursor_tb = conexion.cursor()
	respuesta = cursor_tb.execute("select * from rep_sistema order by idRepor desc")
	return respuesta

def registrarRouters(conexion,routers):
    cursor_tb = conexion.cursor()
    i=0    
    for router in routers:
        if( i != len(routers)-1):
            sentencia = "insert into routersnmp(modelo,nombre,ip) values(?,?,?)"
            cursor_tb.execute(sentencia,('cisco_ios',router.destination_host.partition(".")[0],router.management_ip))
            conexion.commit()
        i=1+i

def actualizaRouters(routers):
    conexion = conecta_db("Proyecto.db")
    cursor_tb = conexion.cursor()
    cursor_tb.execute("Delete from routersnmp")
    cursor_tb.execute("Delete from inforsnmp")
    conexion.commit()
    i=0    
    for router in routers:
        if( i != len(routers)-1):
            sentencia = "insert into routersnmp(modelo,nombre,ip) values(?,?,?)"
            cursor_tb.execute(sentencia,('cisco_ios',router.destination_host.partition(".")[0],router.management_ip))
            conexion.commit()
        i=1+i
    
def verRoutersSNMP(conexion):
    cursor_tb = conexion.cursor()
    respuesta = cursor_tb.execute("select * from routersnmp")
    return respuesta

def putDataRSNMP(conexion,ip, nombre_disp, nombre_os, lugar, contacto):
    cursor_tb = conexion.cursor()
    sentencia = "insert into inforsnmp(ip,nombre,sistem,locali,contac) values(?,?,?,?,?)"
    cursor_tb.execute(sentencia,(ip, nombre_disp, nombre_os, lugar, contacto))
    conexion.commit()

def modifica_RSNMP(conexion,list_data):
    cursor_tb = conexion.cursor()
    sentencia = "update inforsnmp set nombre=?, locali=?, contac=?  where ip=?"
    cursor_tb.execute(sentencia,(list_data[1],list_data[2],list_data[3],list_data[0]))
    conexion.commit()
    sentencia = "update routersnmp set nombre=? where ip=?"
    cursor_tb.execute(sentencia,(list_data[1],list_data[0]))
    conexion.commit()
    return "Dispositivo modificado"

def saveInterfaz(data):
    conexion = conecta_db("Proyecto.db") 
    cursor_tb = conexion.cursor()
    for inter in data:
        sentencia = "insert into interfaces(router_id,name,ip,net,mask,if_mtu,if_speed,if_physaddress,if_adminstatus,if_operstatus,mib_index) values(?,?,?,?,?,?,?,?,?,?,?)"
        cursor_tb.execute(sentencia,(inter[0],inter[1],inter[2],inter[3],inter[4],inter[5],inter[6],inter[7],inter[8],inter[9],inter[10]))
        conexion.commit()

def getInterfaz(conexion, ip):
    cursor_tb = conexion.cursor()
    sentencia = "select * from interfaces where router_id=?"
    return cursor_tb.execute(sentencia,(ip,))

def getInfoInterfaz(conexion, ip):
    cursor_tb = conexion.cursor()
    sentencia = "select * from interfaces where ip=?"
    return cursor_tb.execute(sentencia,(ip,))

def getMIB(ip):
    conexion = conecta_db("Proyecto.db") 
    cursor_tb = conexion.cursor()
    sentencia = "select mib_index from interfaces where ip=?"
    return cursor_tb.execute(sentencia,(ip,))

def insertPaq(conexion, data):
    cursor_tb = conexion.cursor()
    now = datetime.datetime.now()
    tiempo = str(now.hour)+':'+str(now.minute)+':'+str(now.second)
    sentencia = "insert into paquetes(ip_p,ip_d,enviados,recibidos,danadosE,danadosR,tiempo) values(?,?,?,?,?,?,?)"
    cursor_tb.execute(sentencia,(data[0], data[1], data[2], data[3], data[4], data[5], tiempo))
    conexion.commit()

def getPaq(conexion, ip):
    cursor_tb = conexion.cursor()
    sentencia = "select * from paquetes where ip_p=?"
    return cursor_tb.execute(sentencia,(ip,))
