# espcap

espcap is program that uses pyshark to capture packets from a pcap file or live
from a network interface and index them with Elasticsearch.  Since espcap uses
pyshark - which provides a wrapper API tshark - it can use wireshark dissectors
to parse any protocol.

## Requirements

To run escap you need to install the pyshark and Elasticsearch client packages 
both of which can be obtained using pip as follows:
<pre>
pip install elasticsearch
pip install pyshark
</pre>
## Recommendations

It is highly recommended, although not required, that you use the Anaconda Python 
distribution by Continuum Analytcis for espcap. This distribution contains Python
2.7.10 and bundles a rich set of programming packages for analytics and machine 
learning.  You can download Anaconda Python here: http://continuum.io/downloads.

## Getting Started

You run espcap.py as root. If you supply the <tt>-h</tt> or <tt>--help</tt> flags on the command line
you'll get the information on the most useful ways to run espcap.py:
<pre>
espcap.py [--dir=input_directory] [--node=elasticsearch_host]
          [--file=input_file] [--node=elasticsearch_host]
          [--nic=interface] [--node=elasticsearch_host] [--bpf=packet_filter_string] [--count=max_packets]
          [--help]
          [--list-interfaces]

Example command line option combinations:
espcap.py --d=/home/pcap_direcory --node=localhost:9200
espcap.py --file=./pcap_file --node=localhost:9200
espcap.py --nic=eth0 --node=localhost:9200 --bpf="tcp port 80"
espcap.py --nic=en0 --node=localhost:9200 --bpf="udp port 53" --count=100
</pre>
Note that each of these modes is mutually exclusive. If you try to run espcap.py
in more than one mode you'll get an error message.

You can try espcap.py in file mode using the pcap files contained in the test
directory. To do that run espcap.py as follows (assuming you want to just dump
the packets to stdout):
<pre>
espcap.py --dir=./test
</pre>
When running in live capture mode you can set a maximum packet count after which
the capture will stop or you can just hit ctrl-c to stop a continuous capture
session.

## Packet Indexing

When indexing packet captures into Elasticsearch, an new index is created for each 
day. The index naming format is <i>packets-yyyy-mm-dd</i>. The date is UTC derived from 
the packet sniff timestamp obtained from pyshark either for live captures or the
sniff timestamp read from pcap files. Each index has two types, one for live capture 
<i>pcap_live</i> and file capture <i>pcap_file</i>. Both types are dynamically mapped by
Elasticsearch.

### pcap_file type fields
<pre>
file_name       Name of the pcap file from whence the packets were read
file_date_utc   Creation date UTC when the pcap file was created
sniff_date_utc  Date UTC when the packet was read off the wire
sniff_timestamp Time in milliseconds after the Epoch whne the packet was read
protocol        The highest level protocol
layers          Dictionary containing the packet contents
</pre>
### pcap_live type fields

The <i>pcap_live</i> type is comprised of the same fields except the <i>file_name</i> and
<i>file_date_utc</i> fields.
