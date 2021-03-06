#!/usr/bin/env python

import os
import sys
import getopt
import signal
from capture import file_capture, live_capture
from utils import list_interfaces

def command_line_options():
    print "espcap.py [--dir=pcap_directory] [--node=elasticsearch_host] [--chunk=chunk_size] [--trace]"
    print "          [--file=pcap_file] [--node=elasticsearch_host] [--chunk=chunk_size] [--trace]"
    print "          [--nic=interface] [--node=elasticsearch_host] [--bpf=packet_filter_string] [--chunk=chunk_size] [--count=max_packets] [--trace]"
    print "          [--help]"
    print "          [--list-interfaces]"

def example_usage():
    command_line_options()
    print
    print "Example command line option combinations:"
    print "espcap.py --d=/home/pcap_directory --node=localhost:9200"
    print "espcap.py --file=./pcap_file --node=localhost:9200 --chunk=1000"
    print "espcap.py --nic=eth0 --node=localhost:9200 --bpf=\"tcp port 80\" --chunk=2000"
    print "espcap.py --nic=en0 --node=localhost:9200 --bpf=\"udp port 53\" --count=500"
    sys.exit()

def usage():
    command_line_options()
    sys.exit()

def fine_print():
    print "You must specify only one of the following input modes:"
    print "[--dir=pcap_directory]"
    print "[--file=pcap_file]"
    print "[--nic=nic]"
    print "Run \"espcap.py --help\" for more info"
    sys.exit()

def doh(error):
    print error
    sys.exit(2)

def interrupt_handler(signum, frame):
    print
    print("Packet capture interrupted")
    print "Done"
    sys.exit()

def main():
    if len(sys.argv) == 1:
        usage()
    try:
        opts,args = getopt.gnu_getopt(sys.argv[1:], "", ["trace","dir=","file=","nic=","node=","bpf=","chunk=","count=","help","list-interfaces"])
    except getopt.GetoptError as error:
        print str(error)
        usage()

    pcap_files = []
    pcap_dir = None
    pcap_file = None
    nic = None
    node = None
    bpf = None
    trace = False
    count = 0
    chunk = 100
    for opt, arg in opts:
        if opt == "--help":
            example_usage()
        elif opt == "--dir":
            if pcap_file == None and nic == None:
                pcap_dir = arg
            else:
                fine_print()
        elif opt == "--file":
            if pcap_dir == None and nic == None:
                pcap_file = arg
            else:
                fine_print()
        elif opt == "--nic":
            if pcap_file == None and pcap_dir == None:
                nic = arg
            else:
                fine_print()
        elif opt == "--node":
            node = arg
        elif opt == "--bpf":
            bpf = arg
        elif opt == "--chunk":
            chunk = int(arg)
        elif opt == "--count":
            count = int(arg)
        elif opt == "--trace":
            trace = True
        elif opt == "--list-interfaces":
            list_interfaces()
            sys.exit()
        else:
            doh("Unhandled option "+opt)

    # Bail if no nic or input file has been specified
    if nic == None and pcap_dir == None and pcap_file == None:
        fine_print()

    # Enables interrupting of continuous live capture
    signal.signal(signal.SIGINT, interrupt_handler)

    # Handle multiple pcap files in the given directory
    if pcap_dir != None:
        files = os.listdir(pcap_dir)
        files.sort()
        for file in files:
            if pcap_dir.find("/") > 0:
                pcap_files.append(pcap_dir+file)
            else:
                pcap_files.append(pcap_dir+"/"+file)
        file_capture.capture(pcap_files, node, chunk, trace)

    # Handle only the given pcap file
    elif pcap_file != None:
        pcap_files.append(pcap_file)
        file_capture.capture(pcap_files, node, chunk, trace)

    # Capture and handle packets off the wire
    else:
        live_capture.capture(nic, bpf, node, chunk, count, trace)

if __name__ == "__main__":
    main()
    print "Done"