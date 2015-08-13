import os

# Returns a dictionary containing the packet layer data
def get_layers(packet):
    layers = {}
    for j in range(len(packet.layers)):
        layers[packet.layers[j].layer_name] = packet.layers[j]._all_fields
        if j > 0:
            layers[packet.layers[j].layer_name]["envelope"] = packet.layers[j-1].layer_name
    return layers

# Returns list of network interfaces (nic)
def list_interfaces():
    tcpdump = out = os.popen("tcpdump -D")
    tcpdump_out = tcpdump.read()
    interfaces = tcpdump_out.splitlines()
    for i in range(len(interfaces)):
        interface = interfaces[i].strip(str(i+1)+".")
        print interface
