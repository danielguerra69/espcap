import sys
import traceback
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import pyshark
from packet_layers import get_layers

# Index packets in Elasticsearch
def index_packets(capture, sniff_date_utc, count):
    for packet in capture.sniff_continuously(packet_count=count): # count == 0 means no limit
        highest_protocol, layers = get_layers(packet)
        sniff_timestamp = float(packet.sniff_timestamp) # use this field for ordering the packets in ES
        action = {
            "_op_type" : "index",
            "_index" : "packets-"+sniff_date_utc.strftime("%Y-%m-%d"),
            "_type" : "pcap_live",
            "_source" : {
                "sniff_date_utc" : sniff_date_utc.strftime("%Y-%m-%d %H:%M:%S"),
                "sniff_timestamp" : sniff_timestamp,
                "protocol" : highest_protocol,
                "layers" : layers
             }
        }
        yield action

# Dump raw packets to stdout
def dump_packets(capture, sniff_date_utc, count): # count == 0 means no limit
    pkt_no = 1
    for packet in capture.sniff_continuously(packet_count=count):
        highest_protocol, layers = get_layers(packet)
        sniff_timestamp = float(packet.sniff_timestamp)
        print "packet no.", pkt_no
        print "* protocol        -", highest_protocol
        print "* sniff date UTC  -", sniff_date_utc.strftime("%Y-%m-%d %H:%M:%S")
        print "* sniff timestamp -", sniff_timestamp
        print "* layers"
        for key in layers:
            print "\t", key, layers[key]
        print
        pkt_no += 1

# Main capture function
def capture(nic, bpf, node, count, trace):
    try:
        es = None
        if (node != None):
            es = Elasticsearch(node)

        sniff_date_utc = datetime.datetime.utcnow()
        if bpf == None:
            capture = pyshark.LiveCapture(interface=nic)
        else:
            capture = pyshark.LiveCapture(interface=nic, bpf_filter=bpf)

        # Dump or index packets based on whether an Elasticsearch node is available
        if node == None:
            dump_packets(capture, sniff_date_utc, count)
        else:
            helpers.bulk(es,index_packets(capture, sniff_date_utc, count), chunk_size=2000, raise_on_error=True)

    except Exception as e:
        print "error: ", e
        if trace == True:
            traceback.print_exc(file=sys.stdout)