import os

supported_protocols = {}

# Get application level protocol
def get_highest_protocol(packet):
    npackets = len(packet.layers)
    global supported_protocols
    if npackets == 2:
        return packet.layers[1].layer_name
    elif npackets == 3:
        return packet.layers[2].layer_name
    for i in range(3,npackets):
        if packet.layers[i].layer_name in supported_protocols:
            return packet.layers[i].layer_name
    return packet.layers[2].layer_name

# Returns a dictionary containing the packet layer data
def get_layers(packet):
    npackets = len(packet.layers)
    highest_protocol = get_highest_protocol(packet)
    layers = {}
    layers["link"] = packet.layers[0]._all_fields
    layers["network"] = packet.layers[1]._all_fields
    if npackets == 3:
        layers["transport"] = packet.layers[2]._all_fields
    for j in range(3,npackets):
        layers["transport"] = packet.layers[2]._all_fields
        if packet.layers[j].layer_name == highest_protocol:
            layers["application"] = packet.layers[j]._all_fields
        else:
            layers[packet.layers[j].layer_name] = packet.layers[j]._all_fields
            if j == 3:
                layers[packet.layers[j].layer_name]["envelope"] = packet.transport_layer.lower()
            elif j == 4 or j == 5:
                layers[packet.layers[j].layer_name]["envelope"] = highest_protocol
    return highest_protocol, layers

# Returns list of network interfaces (nic)
def list_interfaces():
    proc = os.popen("tshark -D")  # Note tshark must be in $PATH
    tshark_out = proc.read()
    interfaces = tshark_out.splitlines()
    for i in range(len(interfaces)):
        interface = interfaces[i].strip(str(i+1)+".")
        print interface

# Get supported application protocols
def load_config():
    global supported_protocols
    fp = open("conf/protocols.list")
    protocols = fp.readlines()
    for protocol in protocols:
        protocol = protocol.strip()
        supported_protocols[protocol] = 1
