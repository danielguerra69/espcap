import os

# Returns the highest level protocol in the packet
def get_protocol(packet):
    if len(packet.layers) > 3:
        protocol = packet.layers[3].layer_name
        if protocol == "data":
            protocol = packet.layers[4].layer_name
    else:
        protocol = packet.layers[2].layer_name
    return protocol

# Returns a dictionary containing the packet layer data
def get_layers(packet):
    layers = {}
    for j in range(len(packet.layers)):
        layers[packet.layers[j].layer_name] = packet.layers[j]._all_fields
        # Set the envelope layer which is the protocol layer that contains this
        # particular wireshark layer.
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
