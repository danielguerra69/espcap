import os
import datetime
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import pyshark

from packet_utils import get_protocol

# Index packets in Elasticsearch
def index_packets(capture, pcap_file, file_date_utc):
    for packet in capture:
        # Build packet layers
        layers = {}
        for j in range(len(packet.layers)):
            layers[packet.layers[j].layer_name] = packet.layers[j]._all_fields
            # Set the envelope layer which is the protocol layer that contains this
            # particular wireshark layer.
            if j > 0:
                layers[packet.layers[j].layer_name]["envelope"] = packet.layers[j-1].layer_name

            # Set the bulk ingestion action to index packet. Note the sniff_timestamp
            # field is only used for sorting so the time zone, current or otherwise,
            # doesn't matter.
            sniff_timestamp = float(packet.sniff_timestamp)
            action = {
                "_op_type" : "index",
                "_index" : "packets-"+datetime.datetime.utcfromtimestamp(sniff_timestamp).strftime("%Y-%m-%d"),
                "_type" : "pcap_file",
                "_source" : {
                    "file_name" : pcap_file,
                    "file_date_utc" : file_date_utc.strftime("%Y-%m-%d %H:%M:%S"),
                    "sniff_date_utc" : datetime.datetime.utcfromtimestamp(sniff_timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                    "sniff_timestamp" : sniff_timestamp,
                    "protocol" : get_protocol(packet),
                    "layers" : layers
                }
            }
            yield action

# Dump raw packets to stdout
def dump_packets(capture, file_date_utc):
    pkt_no = 1
    for packet in capture:
        # Build packet layers
        layers = {}
        for j in range(len(packet.layers)):
            layers[packet.layers[j].layer_name] = packet.layers[j]._all_fields
            # Set the envelope layer which is the protocol layer that contains this
            # particular wireshark layer.
            if j > 0:
                layers[packet.layers[j].layer_name]["envelope"] = packet.layers[j-1].layer_name

            # Dump raw packet data to stdout
            sniff_timestamp = float(packet.sniff_timestamp)
            print "packet no.", pkt_no, "-", get_protocol(packet)
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

            # Get pcap file creation date UTC
            stats = os.stat(pcap_file)
            file_date_utc = datetime.datetime.utcfromtimestamp(stats.st_ctime)
            capture = pyshark.FileCapture(pcap_file)

            # Dump or index packets based on whether an Elasticsearch node is available
            if node == None:
                dump_packets(capture, file_date_utc)
            else:
                helpers.bulk(es, index_packets(capture, pcap_file, file_date_utc), chunk_size=2000, raise_on_error=True)

    except Exception as e:
        print "error: ", e
