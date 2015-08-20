supported_protocols = {}

# Get supported application protocols
def get_protocols():
    global supported_protocols
    fp = open("conf/protocols.list")
    protocols = fp.readlines()
    for protocol in protocols:
        protocol = protocol.strip()
        supported_protocols[protocol] = 1

# Get application level protocol
def get_highest_protocol(packet):
    global supported_protocols
    if not supported_protocols:
        get_protocols()
    for layer in reversed(packet.layers):
        if layer.layer_name in supported_protocols:
            return layer.layer_name
    return "wtf"

# Returns a dictionary containing the packet layer data
def get_layers(packet):
    n = len(packet.layers)
    highest_protocol = get_highest_protocol(packet)

    layers = {}
    layers["link"] = packet.layers[0]._all_fields
    layer_above_transport = 0
    for i in range(1,n):
        if packet.layers[i].layer_name == "arp":
            layers["network"] = packet.layers[i]._all_fields
            return highest_protocol, layers

        elif packet.layers[i].layer_name == "ip":
            layers["network"] = packet.layers[i]._all_fields

        elif packet.layers[i].layer_name == "tcp" or packet.layers[i].layer_name == "udp" or packet.layers[i].layer_name == "icmp" or packet.layers[i].layer_name == "esp":
            layers["transport"] = packet.layers[i]._all_fields
            if highest_protocol == "tcp" or highest_protocol == "udp" or highest_protocol == "icmp" or highest_protocol == "esp":
                return highest_protocol, layers
            layer_above_transport = i+1
            break

        else:
            layers[packet.layers[i].layer_name] = packet.layers[i]._all_fields
            layers[packet.layers[i].layer_name]["envelope"] = packet.layers[i-1].layer_name

    for j in range(layer_above_transport,n):
        if packet.layers[j].layer_name == highest_protocol:
            layers["application"] = packet.layers[j]._all_fields

        else:
            layers[packet.layers[j].layer_name] = packet.layers[j]._all_fields
            layers[packet.layers[j].layer_name]["envelope"] = packet.layers[j-1].layer_name

    return highest_protocol, layers
