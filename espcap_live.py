import datetime
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import pyshark

from packet_utils import get_protocol
from packet_utils import get_layers

# Index packets in Elasticsearch
def index_packets(capture, sniff_date_utc, count):
    # Capture packets up to count, if count == 0 then there it no limit
    for packet in capture.sniff_continuously(packet_count=count):
        # Get the packet layers dictionary
        layers = get_layers(packet)

        # Set the bulk ingestion action to index packet. Note the sniff_timestamp
        # field is only used for sorting so the time zone, current or otherwise,
        # doesn't matter.
        sniff_timestamp = float(packet.sniff_timestamp)
        action = {
            "_op_type" : "index",
            "_index" : "packets-"+sniff_date_utc.strftime("%Y-%m-%d"),
            "_type" : "pcap_live",
            "_source" : {
                "sniff_date_utc" : sniff_date_utc.strftime("%Y-%m-%d %H:%M:%S"),
                "sniff_timestamp" : sniff_timestamp,
                "protocol" : get_protocol(packet),
                "layers" : layers
            }
        }
        yield action

# Dump raw packets to stdout
def dump_packets(capture, sniff_date_utc, count):
    pkt_no = 1
    for packet in capture.sniff_continuously(packet_count=count):
        # Get the packet layers dictionary
        layers = get_layers(packet)

        # Dump raw packet data to stdout
        sniff_timestamp = float(packet.sniff_timestamp)
        print "packet no.", pkt_no, "-", get_protocol(packet)
        print "* sniff date UTC  -", sniff_date_utc.strftime("%Y-%m-%d %H:%M:%S")
        print "* sniff timestamp -", sniff_timestamp
        print "* layers"
        for key in layers:
            print "\t", key, layers[key]
            print
        pkt_no += 1

# Main capture function
def capture(nic, bpf, node, count):
    try:
        es = None
        if (node != None):
            es = Elasticsearch(node)

        # Get packet capture creation date UTC
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