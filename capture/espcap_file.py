import os
import datetime
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import pyshark
from espcap_utils import get_layers

# Index packets in Elasticsearch
def index_packets(capture, pcap_file, file_date_utc):
    for packet in capture:
        highest_protocol, layers = get_layers(packet)
        sniff_timestamp = float(packet.sniff_timestamp) # use this field for ordering the packets in ES
        action = {
            "_op_type" : "index",
            "_index" : "packets-"+datetime.datetime.utcfromtimestamp(sniff_timestamp).strftime("%Y-%m-%d"),
            "_type" : "pcap_file",
            "_source" : {
                "file_name" : pcap_file,
                "file_date_utc" : file_date_utc.strftime("%Y-%m-%d %H:%M:%S"),
                "sniff_date_utc" : datetime.datetime.utcfromtimestamp(sniff_timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                "sniff_timestamp" : sniff_timestamp,
                "protocol" : highest_protocol,
                "layers" : layers
            }
        }
        yield action

# Dump raw packets to stdout
def dump_packets(capture, file_date_utc):
    pkt_no = 1
    for packet in capture:
        highest_protocol, layers = get_layers(packet)
        sniff_timestamp = float(packet.sniff_timestamp)
        print "packet no.", pkt_no
        print "* protocol        -", highest_protocol
        print "* file date UTC   -", file_date_utc.strftime("%Y-%m-%d %H:%M:%S")
        print "* sniff date UTC  -", datetime.datetime.utcfromtimestamp(sniff_timestamp).strftime("%Y-%m-%d %H:%M:%S")
        print "* sniff timestamp -", sniff_timestamp
        print "* layers"
        for key in layers:
            print "\t", key, layers[key]
        print
        pkt_no += 1

# Main capture function
def capture(pcap_files, node):
    try:
        es = None
        if (node != None):
            es = Elasticsearch(node)

        print "Loading packet capture file(s)"
        for pcap_file in pcap_files:
            print pcap_file
            stats = os.stat(pcap_file)
            file_date_utc = datetime.datetime.utcfromtimestamp(stats.st_ctime)
            capture = pyshark.FileCapture(pcap_file)

            # If no Elasticsearch node specified, dump to stdout
            if node == None:
                dump_packets(capture, file_date_utc)
            else:
                helpers.bulk(es, index_packets(capture, pcap_file, file_date_utc), chunk_size=2000, raise_on_error=True)

    except Exception as e:
        print "error: ", e
