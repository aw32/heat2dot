#!/usr/bin/python3
# Reads json or yaml from stdin
# Interprets structure as heat template
# Generates dot graph from heat template

# Dependencies:
# * PyYaml

import sys
import json
import yaml

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class Server:
    def __init__(self, idx,longName=None, shortName=None):
        self.idx = idx
        self.longName = longName
        self.shortName = shortName
        self.portIdx = []
        self.broken = False

class Port:
    def __init__(self, idx, longName=None, shortName=None):
        self.idx = idx
        self.longName = longName
        self.shortName = shortName
        self.broken = False

    def dot(self):
        if self.broken:
            return "port"+str(self.idx)+" [style=filled,fillcolor=red,shape=ellipse,label=\""+str(self.shortName)+"\"];"
        else:
            return "port"+str(self.idx)+" [style=filled,fillcolor=white,shape=ellipse,label=\""+str(self.shortName)+"\"];"

class Net:
    def __init__(self, idx, longName=None, shortName=None):
        self.idx = idx
        self.longName = longName
        self.shortName = shortName
        self.broken = False

    def dot(self):
        if self.broken:
            return "net"+str(self.idx)+" [shape=box,style=filled,fillcolor=red,label=\""+str(self.shortName)+"\"];"
        else:
            return "net"+str(self.idx)+" [shape=box,style=filled,fillcolor=lawngreen,label=\""+str(self.shortName)+"\"];"

class Subnet:
    def __init__(self, idx, longName=None, shortName=None):
        self.idx = idx
        self.longName = longName
        self.shortName = shortName
        self.broken = False
    def dot(self):
        if self.broken:
            return "subnet"+str(self.idx)+" [shape=octagon,style=filled,fillcolor=red,label=\""+str(self.shortName)+"\"];"
        else:
            return "subnet"+str(self.idx)+" [shape=octagon,label=\""+str(self.shortName)+"\"];"

class Router:
    def __init__(self, idx, longName=None, shortName=None):
        self.idx = idx
        self.longName = longName
        self.shortName = shortName
        self.broken = False
    def dot(self):
        if self.broken:
            return "router"+str(self.idx)+" [style=filled,fillcolor=red,shape=diamond,label=\""+str(self.shortName)+"\"];"
        else:
            return "router"+str(self.idx)+" [style=filled,fillcolor=lightpink1,shape=diamond,label=\""+str(self.shortName)+"\"];"

class RouterInterface:
    def __init__(self, idx, longName=None, shortName=None):
        self.idx = idx
        self.longName = longName
        self.shortName = shortName
        self.routerIdx = None
        self.subnetIdx = None
        self.broken = False
    def dot(self):
        if self.broken:
            return "routerInterface"+str(self.idx)+" [shape=triangle,style=filled,fillcolor=red,label=\""+str(self.shortName)+"\"];"
        else:
            return "routerInterface"+str(self.idx)+" [shape=triangle,label=\""+str(self.shortName)+"\"];"

class FloatingIP:
    def __init__(self, idx, longName=None, shortName=None):
        self.idx = idx
        self.longName = longName
        self.shortName = shortName
        self.broken = False
    def dot(self):
        if self.broken:
            return "floating"+str(self.idx)+" [shape=egg,style=filled,fillcolor=red,label=\""+str(self.shortName)+"\"];"
        else:
            return "floating"+str(self.idx)+" [shape=egg,label=\""+str(self.shortName)+"\"];"

def findPortIdxByName(ports,name):
    for idx,port in enumerate(ports):
        if port["properties"]["name"]==name:
            return idx

def findNetIdxByName(nets,name):
    for idx,net in enumerate(nets):
        if net["properties"]["name"]==name:
            return idx

def findSubnetIdxByName(subnets,name):
    for idx,subnet in enumerate(subnets):
        if subnet["properties"]["name"]==name:
            return idx

def findRouterIdxByName(routers,name):
    for idx,router in enumerate(routers):
        if router["properties"]["name"]==name:
            return idx

##### START PROGRAM #####

# read from stdin
text = ""
for line in sys.stdin:
    text += line

jsonFile = True
yamlFile = True

try:
    textobj = json.loads(text)
except Exception as e:
    eprint("JSON parse failure")
    eprint(e)
    jsonFile = False

if jsonFile == False:
    try:
        textobj = yaml.load(text)
    except Exception as e:
        eprint("YAML parse failure")
        eprint(e)
        yamlFile = False

if jsonFile == False and yamlFile == False:
    eprint("Parsing unsuccessful")
    exit(1)

if jsonFile == True:
    eprint("Parsed as JSON")

if yamlFile == True:
    eprint("Parsed as YAML")

if "heat_template_version" in textobj:
    eprint("heat_template_version",textobj["heat_template_version"])

if not "resources" in textobj:
    eprint("Failed to find resources array")
    exit(1)

# sort resources according to resource type

resources = textobj["resources"]
servers = []
ports = []
nets = []
subnets = []
routers = []
routerinterfaces = []
floatings = []
withouttype = 0
others = {}

for resourceName in resources:
    obj = resources[resourceName]
    if "type" not in obj:
        withouttype += 1
        continue
    if obj["type"] == "OS::Nova::Server":
        servers.append(obj)
    elif obj["type"] == "OS::Neutron::Port":
        ports.append(obj)
    elif obj["type"] == "OS::Neutron::Net":
        nets.append(obj)
    elif obj["type"] == "OS::Neutron::Subnet":
        subnets.append(obj)
    elif obj["type"] == "OS::Neutron::Router":
        routers.append(obj)
    elif obj["type"] == "OS::Neutron::RouterInterface":
        routerinterfaces.append(obj)
    elif obj["type"] == "OS::Neutron::FloatingIP":
        floatings.append(obj)
    else:
        eprint("Unknown resource type",obj["type"])
        others[obj.type] += 1

eprint("------")
eprint("Servers: \t\t",str(len(servers)))
eprint("Ports: \t\t\t",str(len(ports)))
eprint("Nets: \t\t\t",str(len(nets)))
eprint("Subnets: \t\t",str(len(subnets)))
eprint("Routers: \t\t",str(len(routers)))
eprint("RouterInterfaces: \t",str(len(routerinterfaces)))
eprint("FloatingIPs: \t\t",str(len(floatings)))

if withouttype > 0:
    eprint("------")
    eprint("Without type: \t\t",str(withouttype))

if len(others)>0:
    eprint("------")
    eprint("Unknown types:")
    for typus in others:
        eprint(typus+": \t\t",str(others[typus]))
eprint("------")

# create wrapper objects for known types

dotServers = []
dotPorts = []
dotNets = []
dotSubnets = []
dotRouters = []
dotRouterinterfaces = []
dotFloatings = []

# create graph objects
for idx,jsonServer in enumerate(servers):
    failure = False
    server = Server(idx,longName="server"+str(idx),shortName="server"+str(idx))
    # check available attributes
    if "properties" not in jsonServer:
        eprint("missing properties in OS::Nova::Server object")
        server.broken = True
    else:
        if "name" not in jsonServer["properties"]:
            eprint("missing name in OS::Nova::Server object")
            server.broken = True
        else:
            server.longName = jsonServer["properties"]["name"]
            server.shortName = jsonServer["properties"]["name"].split(":")[0]

        if "networks" not in jsonServer["properties"]:
            eprint("missing networks in OS::Nova::Server object")
            server.broken = True
        else:
            networks = jsonServer["properties"]["networks"]
            for net in networks:
                if "port" not in net:
                    eprint("missing port in networks in OS::Nova::Server object")
                    server.broken = True
                elif "get_resource" not in net["port"]:
                    eprint("missing get_resource in port in networks in OS::Nova::Server object")
                    server.broken = True
                else:
                    portIdx = findPortIdxByName(ports,net["port"]["get_resource"])
                    if portIdx == None:
                        eprint("Port",net["port"]["get_resource"],"for OS::Nova::Server object",server.shortName,"not found")
                        server.broken = True
                    server.portIdx.append(portIdx)
    dotServers.append(server)    

for idx,jsonPort in enumerate(ports):
    port = Port(idx,longName="port"+str(idx),shortName="port"+str(idx))
    if "properties" not in jsonPort:
        eprint("missing properties in OS::Neutron::Port object")
        port.broken = True
    else:
        if "name" not in jsonPort["properties"]:
            eprint("missing name in OS::Neutron::Port object")
            port.broken = True
        else:
            port.longName = jsonPort["properties"]["name"]
            port.shortName = jsonPort["properties"]["name"].split(":")
            if len(port.shortName)<3:
                eprint("Name of OS::Neutron::Port object unexpected")
                eprint("  use full name instead:",port.longName)
                port.shortName = port.longName
            else:
                port.shortName = port.shortName[0]+":"+port.shortName[1]+":"+port.shortName[2]
    
        if "network" not in jsonPort["properties"]:
            eprint("missing network in OS::Neutron::Port object")
            port.broken = True
        elif "get_resource" not in jsonPort["properties"]["network"]:
            eprint("missing get_resource in network in OS::Neutron::Port object")
            port.broken = True
        else:
            port.netIdx = findNetIdxByName(nets,jsonPort["properties"]["network"]["get_resource"])
            if port.netIdx == None:
                eprint("Net",jsonPort["properties"]["network"]["get_resource"],"for OS::Neutron::Port object",port.shortName,"not found")
                port.broken = True
    dotPorts.append(port)

for idx,jsonNet in enumerate(nets):
    net = Net(idx,longName="net"+str(idx),shortName="net"+str(idx))
    if "properties" not in jsonNet:
        eprint("missing properties in OS::Neutron::Net object")
        net.broken = True
    else:
        if "name" not in jsonNet["properties"]:
            eprint("missing name in OS::Neutron::Net object")
            net.broken = True
        else:
            net.longName = jsonNet["properties"]["name"]
            net.shortName =net.longName.split(":")
            if len(net.shortName)<2:
                eprint("Name of OS::Neutron::Net object unexpected")
                eprint("  use full name instead:",net.longName)
                net.shortName = net.longName
            else:
                net.shortName = net.shortName[0]+":"+net.shortName[1]
    dotNets.append(net)

for idx,jsonSubnet in enumerate(subnets):
    subnet = Subnet(idx,longName="subnet"+str(idx),shortName="subnet"+str(idx))
    if "properties" not in jsonSubnet:
        eprint("missing properties in OS::Neutron::Subnet object")
        subnet.broken = True
    else:
        if "name" not in jsonSubnet["properties"]:
            eprint("missing name in OS::Neutron::Subnet object")
            subnet.broken = True
        else:
            subnet.longName = jsonSubnet["properties"]["name"]
            subnet.shortName = subnet.longName.split(":")
            if len(subnet.shortName)<2:
                eprint("Name of OS::Neutron::Subnet object unexpected")
                eprint("  use full name instead:",subnet.longName)
                subnet.shortName = subnet.longName
            else:
                subnet.shortName = subnet.shortName[0]+":"+subnet.shortName[1]
        if "cidr" not in jsonSubnet["properties"]:
            eprint("missing cidr in OS::Neutron::Subnet object")
            subnet.broken = True
        else:
            subnet.cidr = jsonSubnet["properties"]["cidr"]
        if "gateway_ip" not in jsonSubnet["properties"]:
            eprint("missing gateway_ip in OS::Neutron::Subnet object")
            subnet.broken = True
        else:
            subnet.gatewayIp = jsonSubnet["properties"]["gateway_ip"]
        if "network" not in jsonSubnet["properties"]:
            eprint("missing network in OS::Neutron::Subnet object")
            subnet.broken = True
        elif "get_resource" not in jsonSubnet["properties"]["network"]:
            eprint("missing get_resource in network in OS::Neutron::Subnet object")
            subnet.broken = True
        else:
            subnet.netIdx = findNetIdxByName(nets,jsonSubnet["properties"]["network"]["get_resource"])
            if subnet.netIdx == None:
                eprint("Net",jsonSubnet["properties"]["network"]["get_resource"],"for OS::Neutron::Subnet object",subnet.shortName,"not found")
                subnet.broken = True
    dotSubnets.append(subnet)

for idx,jsonRouter in enumerate(routers):
    router = Router(idx,longName="router"+str(idx),shortName="router"+str(idx))
    if "properties" not in jsonRouter:
        eprint("missing properties in OS::Neutron::Router object")
        router.broken = True
    else:
        if "name" not in jsonRouter["properties"]:
            eprint("missing name in OS::Neutron::Router object")
            router.broken = True
        else:
            router.longName = jsonRouter["properties"]["name"]
            router.shortName = router.longName.split(":")
            if len(router.shortName)<2:
                eprint("Name of OS::Neutron::Router object unexpected")
                eprint("  use full name instead:",router.longName)
                router.shortName = router.longName
            else:
                router.shortName = router.shortName[0]+":"+router.shortName[1];
    dotRouters.append(router)

for idx,jsonRouterInterface in enumerate(routerinterfaces):
    routerInterface = RouterInterface(idx,longName="ri"+str(idx),shortName="ri"+str(idx))
    if "properties" not in jsonRouterInterface:
        eprint("missing properties in OS::Neutron::RouterInterface object")
        routerInterface.broken = True
    else:
        if "router" not in jsonRouterInterface["properties"]:
            eprint("missing router in OS::Neutron::RouterInterface object")
            routerInterface.broken = True
        elif "get_resource" not in jsonRouterInterface["properties"]["router"]:
            eprint("missing get_resource in router in OS::Neutron::RouterInterface object")
            routerInterface.broken = True
        else:
            routerInterface.routerIdx = findRouterIdxByName(routers,jsonRouterInterface["properties"]["router"]["get_resource"])
            if routerInterface.routerIdx == None:
                eprint("Router",jsonRouterInterface["properties"]["router"]["get_resource"],"for OS::Neutron::RouterInterface object not found")
                routerInterface.broken = True
        if "subnet" not in jsonRouterInterface["properties"]:
            eprint("missing subnet in OS::Neutron::RouterInterface object")
            routerInterface.broken = True
        elif "get_resource" not in jsonRouterInterface["properties"]["subnet"]:
            eprint("missing get_resource in subnet in OS::Neutron::RouterInterface object")
            routerInterface.broken = True
        else:
            routerInterface.subnetIdx = findSubnetIdxByName(subnets,jsonRouterInterface["properties"]["subnet"]["get_resource"])
            if routerInterface.subnetIdx == None:
                eprint("Subnet",jsonRouterInterface["properties"]["subnet"]["get_resource"],"for OS::Neutron::RouterInterface object not found")
                routerInterface.broken = True
    dotRouterinterfaces.append(routerInterface)

for idx,jsonFloating in enumerate(floatings):
    floating = FloatingIP(idx,longName="fip"+str(idx),shortName="fip"+str(idx))
    if "properties" not in jsonFloating:
        eprint("missing properties in OS::Neutron::FloatingIP object")
        floating.broken = True
    else:
        if "port_id" not in jsonFloating["properties"]:
            eprint("missing port_id in OS::Neutron::FloatingIP object")
            floating.broken = True
        elif "get_resource" not in jsonFloating["properties"]["port_id"]:
            eprint("missing get_resource in port_id in OS::Neutron::FloatingIP object")
            floating.broken = True
        else:
            floating.portIdx = findPortIdxByName(ports,jsonFloating["properties"]["port_id"]["get_resource"])
            if floating.portIdx == None:
                eprint("Port",jsonFloating["properties"]["port_id"]["get_resource"],"for OS::Neutron::FloatingIP object not found")
                floating.broken = True
    dotFloatings.append(floating)

# printing graph
print("graph heat {")
#print("layout=patchwork;")


for idx,server in enumerate(dotServers):
    print("subgraph cluster_server"+str(idx)+" {")
    print("label=\""+server.shortName+"\";")
    print("fillcolor=lightblue1;")
    print("style=filled;")
    for portIx in server.portIdx:
        if portIx == None:
            pass
        else:
            port = dotPorts[portIx]
            print(port.dot())
    print("}")

# nets
for idx,net in enumerate(dotNets):
    print(net.dot())

# subnets
for idx,subnet in enumerate(dotSubnets):
    print(subnet.dot())

# routers
for idx,router in enumerate(dotRouters):
    print(router.dot())

# router interfaces
for idx,routerInterface in enumerate(dotRouterinterfaces):
    print(routerInterface.dot())

# floating ips
for idx,floating in enumerate(dotFloatings):
    print(floating.dot())

# connect ports to nets
for idx,port in enumerate(dotPorts):
    print("port"+str(idx),"--","net"+str(port.netIdx))
# connect subnets to nets
for idx,subnet in enumerate(dotSubnets):
    print("subnet"+str(idx),"--","net"+str(subnet.netIdx))
# connect router interfaces to subnets and routers
for idx,routerInterface in enumerate(dotRouterinterfaces):
    print("subnet"+str(routerInterface.subnetIdx),"--","routerInterface"+str(idx)+";")
    print("routerInterface"+str(idx),"--","router"+str(routerInterface.routerIdx)+";")
# connect floating ip to port
for idx,floating in enumerate(dotFloatings):
    print("port"+str(floating.portIdx),"--","floating"+str(idx)+";")

# legend
print("subgraph cluster_legend {")
print("label=\"Legend\";")
# server legend
print("subgraph cluster_legend_server {")
print("label=\"server\";")
print("fillcolor=lightblue1;")
print("style=filled;")
print(Port("legend",shortName="port").dot())
print("}")
# net legend
print(Net("legend",shortName="net").dot())
# subnet legend
print(Subnet("legend",shortName="subnet").dot())
# router legend
print(Router("legend",shortName="router").dot())
# router interface legend
print("routerInterfacelegend [shape=triangle,label=\"router interface\"];")
# floating ip legend
print("floatinglegend [shape=egg,label=\"floating ip\"];")
print("}")
print("}")
eprint("------")
eprint("Exiting")
eprint("------")


