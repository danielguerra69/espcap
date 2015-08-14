import os
import ConfigParser

tshark = ""
app_protocols = {}

# Get application level protocol
def get_highest_protocol(packet):
    npackets = len(packet.layers)
    global app_protocols
    if npackets == 3:
        return packet.layers[2].layer_name
    if npackets == 4:
        print packet.layers[3].layer_name, packet.layers[3].layer_name in app_protocols
        if packet.layers[3].layer_name in app_protocols:
            return packet.layers[3].layer_name
        return packet.layers[2].layer_name in app_protocols
    if npackets == 5:
        if packet.layers[4].layer_name in app_protocols:
            return packet.layers[4].layer_name in app_protocols
        return packet.layers[3].layer_name in app_protocols
    if npackets == 6:
        return packet.layers[4].layer_name in app_protocols

# Returns a dictionary containing the packet layer data
def get_layers(packet, highest_protocol):
    layers = {}
    for j in range(len(packet.layers)):
        layers[packet.layers[j].layer_name] = packet.layers[j]._all_fields
        if j > 0:
            layers[packet.layers[j].layer_name]["envelope"] = packet.layers[j-1].layer_name
    return layers

# Returns list of network interfaces (nic)
def list_interfaces():
    proc = os.popen(tshark+" -D")
    tshark_out = proc.read()
    interfaces = tshark_out.splitlines()
    for i in range(len(interfaces)):
        interface = interfaces[i].strip(str(i+1)+".")
        print interface

# Get tshark path
def load_config():
    global tshark
    config = ConfigParser.ConfigParser()
    config.readfp(open("./espcap.conf"))
    path = config.get("paths", "tshark")
    tshark = path+"/tshark"

    global app_protocols
    fp = open("./protocols.list")
    protcols = fp.readlines()
    for protocol in protcols:
        app_protocols[protocol] = 1

