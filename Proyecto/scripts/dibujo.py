from pyvis.network import Network
import json, ipaddress, os

#0 admin, 1 user
def cambiarEnlaces(net, out_net, tipo_user): #if para base_template 
	fp = open(net, 'r')
	fo = open(out_net, 'w')
	for i in enumerate(fp):
		if i[0] == 0:
			if tipo_user == 0:
				fo.write('''{% extends "Base_Admin.html" %}\n''')
			else:
				fo.write('''{% extends "Base_Usr.html" %}\n''')
		elif i[0] == 1:
			fo.write('''{% block title %}.: Dibuja Topologia :.{% endblock %}\n''')
		elif i[0] == 2:
			fo.write('''{% block css%}<link rel='stylesheet' href="{{ url_for('static',filename='css/vis.css') }}" type='text/css' />{% endblock %} \n''')
		elif i[0] == 3:
			fo.write('''{% block js%}<script type='text/javascript' src="{{ url_for('static',filename='js/vis-network.min.js') }}"></script>{% endblock %}\n''')
			fo.write("{% block contenido %}\n")	
		elif i[0] == 4:
			fo.write('''<!-- CONTENIDO --><br><br><br><div class="row" style="margin-bottom: 5%;"><!-- Timeline --><h2 class="center-align">Topología</h2></div>''')
		elif i[0] == 5 or i[0] == 6:
			fo.write("\n")		
		elif i[0] == 14:
			fo.write("\t\twidth: 900px;\n")
		elif i[0] == 15:
			fo.write("\t\theight: 750px;\n") 
		elif i[0] == 17:
			fo.write('''display: inline-block;\nmargin: 0 auto;\npadding: 3px;\nposition: relative;''')
		elif i[0] == 18:
			fo.write("\n")
		elif i[0] == 19:	
			fo.write("\n")
		elif i[0] == 29:
			fo.write("\n")
		elif i[0] == 31:
			fo.write("\n")
		elif i[0] == 32:
			fo.write('''<center><div id = "mynetwork"></div></center>''')
		elif i[0] == 106:
			fo.write("{% endblock %}\n")
		elif i[0] == 107:
			fo.write("\n")			
		else:
			fo.write(i[1])
	fp.close()
	fo.close()

def eliminarTemporal(file):
	os.remove(file)

def conexionesCli2edges(general_net, clients_dic, clients_id, routers_dic):
	edges = [] 
	nets = []
	for router in general_net:
		for interface in router["interfaces"]:
			red = interface["idnet"]
			for client, os in clients_dic.items():
				an_address = ipaddress.ip_address(client)
				a_network = ipaddress.ip_network(red)
				if an_address in a_network:
					edges.append((routers_dic[router["hostname"]], clients_id[client]))
					nets.append(red)
	return edges, nets


def client2Id(clients_dic, i):
	clients_id = {}
	j = i
	for client in clients_dic:
		clients_id[client] = j
		j += 1
	return clients_id

def devices2devicesDic(devices):
	dicDispositivos = {}
	for device in devices:
		for key in device:
			dicDispositivos[key] = device[key]
	return dicDispositivos

def obtenerDispositivos(devices):
	interfaces = {}
	clients = {}
	for ip, dis_type in devices.items():
		if "Cisco_Router_IOS" in dis_type:
			interfaces[ip] = dis_type
		else:
			clients[ip] = dis_type
	return interfaces, clients

def routers2routersDic(routers):
	routers_dic = {} 
	i = 0
	for router in routers:
		routers_dic[router] = i
		i+=1
	return routers_dic

def conexiones2edges(interconexiones, routers_dic):
	edges = []
	nets = []
	for interconexion in interconexiones:
		#separar routers
		router1 = interconexion.split(":")[0].split("-")[0]
		router2 = interconexion.split(":")[0].split("-")[1]
		net = interconexion.split(":")[1]
		edges.append((routers_dic[router1], routers_dic[router2]))
		nets.append(net)
	return edges, nets

def construirDibujoTopologia(routers, interconexiones, devices, general):
	routers_dic = routers2routersDic(routers)
	edges, redes = conexiones2edges(interconexiones, routers_dic)

	devices_dic = devices2devicesDic(devices)
	interfaces_dic, clients_dic = obtenerDispositivos(devices_dic)
	clients_id = client2Id(clients_dic, len(routers_dic))

	edges_cli, redes_cli = conexionesCli2edges(general, clients_dic, clients_id, routers_dic)

	net = Network("1000px", "1000px")

	print(clients_id)
	#nodos de cada router
	for router in routers_dic:
		print("anadiendo nodo router {}".format(router))
		net.add_node(routers_dic[router], "{}".format(router), physics=False,mass=1, level=1, shape="image", title="", image="/static/icons/blue/router.svg")

	#conexiones entre routers
	for (edge, red) in zip(edges, redes):
		print("anadiendo edge router {}".format(edge))
		net.add_edge(*edge, title=red)

	#nodos de cada cliente
	for client, id_cli in clients_id.items():
		print("anadiendo nodo cli {}".format(client))
		net.add_node(id_cli, "{}".format(client), physics=False, mass=1, level=3, shape="image", title="{}".format(clients_dic[client]), image="/static/icons/blue/client.svg")
		#net.add_node(clients_dic[client], "{}".format(client), physics=False, mass=1, level=3, shape="image", title="{}".format(clients_dic[client]), image="/static/icons/blue/client.svg")
	#conexiones de clientes
	for (edge, red) in zip(edges_cli, redes_cli):
		print("anadiendo edge cli {}".format(edge))
		net.add_edge(*edge, title=red)

	return net
