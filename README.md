# espcap

espcap is a program that uses pyshark to capture packets from a pcap file or live
from a network interface and index them with Elasticsearch.  Since espcap uses
pyshark - which provides a wrapper API to tshark - it can use wireshark dissectors
to parse any protocol.

## Requirements

To run escap you need to install the pyshark and Elasticsearch client packages 
both of which can be obtained using pip as follows:
<pre>
pip install elasticsearch
pip install pyshark
</pre>

You will also need wireshark and libpcap, if you don't have them already. To make 
sure pyshark can find your tshark binary, open the pyshark config.ini file then 
set the <i>tshark_path</i> field to point tshark. Here is an example from a Mac 
OS system that is pretty typical:
<pre>
tshark_path = /usr/local/bin/tshark
</pre>
Pyshark is usually located in the site-packages/pyshark directory of your Python 
installation. 

Finally, make sure that tshark is in your path.
 
## Recommendations

It is highly recommended, although not required, that you use the Anaconda Python 
distribution by Continuum Analytcis for espcap. This distribution contains Python
2.7.10 and bundles a rich set of programming packages for analytics and machine 
learning.  You can download Anaconda Python here: http://continuum.io/downloads.

## Getting Started

You run espcap.py as root. If you supply the <tt>--help</tt> flags on the command 
line you'll get the information on the most useful ways to run espcap.py:
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
Note that each of these modes is mutually exclusive. If you try to run espcap.py in more 
than one mode you'll get an error message.

You can try espcap.py in file mode using the pcap files contained in test_pcaps. To do 
that run espcap.py as follows (assuming you want to just dump the packets to stdout):
<pre>
espcap.py --dir=./test_pcaps
</pre>
When running in live capture mode you can set a maximum packet count after which the 
capture will stop or you can just hit ctrl-c to stop a continuous capture session.

## Packet Indexing

When indexing packet captures into Elasticsearch, an new index is created for each 
day. The index naming format is <i>packets-yyyy-mm-dd</i>. The date is UTC derived from 
the packet sniff timestamp obtained from pyshark either for live captures or the
sniff timestamp read from pcap files. Each index has two types, one for live capture 
<i>pcap_live</i> and file capture <i>pcap_file</i>. Both types are dynamically mapped by
Elasticsearch.

Index IDs are automatically assigned by Elasticsearch

### pcap_file type fields
<pre>
file_name          Name of the pcap file from whence the packets were read
file_date_utc      Creation date UTC when the pcap file was created
sniff_date_utc     Date UTC when the packet was read off the wire
sniff_timestamp    Time in milliseconds after the Epoch whne the packet was read
protocol           The highest level protocol
layers             Dictionary containing the packet contents
</pre>
### pcap_live type fields

The <i>pcap_live</i> type is comprised of the same fields except the <i>file_name</i> and
<i>file_date_utc</i> fields.

## Packet Layer Structure

Packet layers are mapped in four basic sections based in protocol type within each index:

<ol>
<li>Link - link to the physical network media, usually Ethernet (eth).</li>
<li>Network - network routing layer which is always IP (ip).</li>
<li>Transport - transport layer which is either TCP (tcp) or UDP (udp).</li>
<li>Application - high level Internet protocol such as HTTP (http), DNS (dns), etc.</li>
</ol>

Packet layers reside in a JSON section called <i>layers</i>. Each of the four layers reside
in a JSON section of the same name.  The packet field names include the protocol of the given
layer.  Below is an example of an HTTP packet that has been truncated in the places denoted by
<tt><-- SNIP --></tt>. 

<pre>
{
    "_index": "packets-2015-07-30",
    "_type": "pcap_file",
    "_id": "AU8qrFkng7etWlj8EWpH",
    "_score": null,
    "_source": {
        "layers": {
        "network": {
            "": "Source GeoIP: Unknown",
            "ip.flags.mf": "0",
            "ip.ttl": "55",
            "ip.version": "4",
            "ip.dst_host": "10.0.0.4",
            "ip.flags.df": "0",
            "ip.flags": "0",
            "ip.dsfield": "32",
            "ip.src_host": "74.125.239.39",
            "ip.checksum_good": "0",
            "ip.id": "55992",
            "ip.checksum": "25900",
            "ip.dsfield.ecn": "0",
            "ip.hdr_len": "20",
            "ip.dst": "10.0.0.4",
            "ip.dsfield.dscp": "8",
            "ip.frag_offset": "0",
            "ip.host": "74.125.239.39",
            "ip.flags.rb": "0",
            "ip.addr": "74.125.239.39",
            "ip.len": "75",
            "ip.src": "74.125.239.39",
            "ip.checksum_bad": "0",
            "ip.proto": "6"
        },
        "media": {
            "": "Media Type: application/x-x509-ca-cert (1012 bytes)",
            "envelope": "http"
        },
        "application": {
            "": "HTTP/1.1 200 OK\\r\\n",
            "http.last_modified": "Wed, 29 Jul 2015 15:15:00 GMT",
            "http.response.phrase": "OK",
            "http.time": "0.121884000",
            "data.len": "1012",
            "http.date": "Thu, 30 Jul 2015 04:22:34 GMT",
            "http.request.version": "HTTP/1.1",
            "data.data":"30:82:03:f0:30:82:02:d8:a0:03: <-- SNIP --> ",
            "_ws.expert.message": "HTTP/1.1 200 OK\\r\\n",
            "http.request_in": "14",
            "_ws.expert": "Expert Info (Chat/Sequence): HTTP/1.1 200 OK\\r\\n",
            "_ws.expert.group": "33554432",
            "_ws.expert.severity": "2097152",
            "data": "308203f03 <-- SNIP --> ",
            "http.transfer_encoding": "chunked",
            "http.response.code": "200",
            "http.server": "sffe",
            "http.content_type": "application/x-x509-ca-cert",
            "http.cache_control": "public, max-age=3600",
            "http.response": "1",
            "http.response.line": "Vary: Accept-Encoding\\xd\\xa",
            "http.chat": "HTTP/1.1 200 OK\\r\\n"
        },
        "link": {
            "eth.dst_resolved": "60:f8:1d:cb:43:84",
            "eth.src_resolved": "58:23:8c:b4:42:56",
            "eth.dst": "60:f8:1d:cb:43:84",
            "eth.addr_resolved": "60:f8:1d:cb:43:84",
            "eth.lg": "0",
            "eth.addr": "60:f8:1d:cb:43:84",
            "eth.ig": "0",
            "eth.type": "2048",
            "eth.src": "58:23:8c:b4:42:56"
        },
        "data": {
            "tcp.segments": "2 Reassembled TCP Segments (1441 bytes): #17(1418), #18(23)",
            "envelope": "tcp",
            "tcp.reassembled.data":"48:54:54:50:2f:31: <-- SNIP --> ",
            "tcp.segment": "17",
            "tcp.reassembled.length": "1441",
            "tcp.segment.count": "2"
        },
        "transport": {
            "": "No-Operation (NOP)",
            "tcp.checksum_bad": "0",
            "tcp.segment_data": "bb:8d:d7:ad:52:64:16:57:96:d9:5e:34:7e:c8:35:d8:0d:0a:30:0d:0a:0d:0a",
            "tcp.flags.urg": "0",
            "tcp.ack": "168",
            "tcp.options.type.class": "0",
            "tcp.analysis.bytes_in_flight": "1441",
            "tcp.stream": "1",
            "tcp.options.type.number": "1",
            "tcp.seq": "1419",
            "tcp.analysis.initial_rtt": "0.013221000",
            "tcp.len": "23",
            "tcp.flags.res": "0",
            "tcp.option_len": "10",
            "tcp.analysis": "SEQ/ACK analysis",
            "tcp.hdr_len": "32",
            "tcp.dstport": "59804",
            "tcp.flags.push": "1",
            "tcp.options.type.copy": "0",
            "tcp.window_size": "43648",
            "tcp.flags.ns": "0",
            "tcp.flags.ack": "1",
            "tcp.flags.fin": "0",
            "tcp.option_kind": "8",
            "tcp.checksum_good": "0",
            "tcp.port": "80",
            "tcp.window_size_scalefactor": "128",
            "tcp.window_size_value": "341",
            "tcp.options.type": "1",
            "tcp.options": "01:01:08:0a:8e:8c:fe:1a:17:11:d4:4a",
            "tcp.flags": "24",
            "tcp.flags.ecn": "0",
            "tcp.nxtseq": "1442",
            "tcp.srcport": "80",
            "tcp.checksum": "16319",
            "tcp.urgent_pointer": "0",
            "tcp.options.timestamp.tsval": "2391604762",
            "tcp.flags.syn": "0",
            "tcp.flags.cwr": "0",
            "tcp.flags.reset": "0",
            "tcp.options.timestamp.tsecr": "387044426"
        }
    },
    "protocol": "http",
    "sniff_timestamp": 1438233730.634684,
    "file_name": "test_pcaps/test_http.pcap",
    "sniff_date_utc": "2015-07-30 05:22:10",
    "file_date_utc": "2015-07-30 05:26:19"
 }
</pre>

The convention for accessing protocol fields in the JSON layers structure is:

<pre>
layers.protocol-type.field-name
</pre>

Here are some examples of how to reference specific layer fields taken from the packet
JSON shown above:

<pre>
layers.network.ip.src            Sender IP address
layers.network.ip.dst            Receiver IP address
layers.transport.tcp.srcport     Sender TCP port
layers.transport.tcp.dstport     Receiver TCP port
layers.application.http.chat     HTTP response
</pre>

Note that some layer protocols span two sections. In the above example, the TCP segment has a <i>data</i> 
section associated and the HTTP response has a <i>media</i> section. Extra sections like these can be 
associated with their protocol sections by checking the <i>envelope</i> field contents.

## Protocol Support

Technically epscap recognizes all the protocols supported by wureshark/tshark. However, the wireshark
dissector set includes some strange protocols that are not really Internet protocols in the strictest
sense, but are rather parts of other protocols. One example is <i>media</i> which is actually used to
label an additional layer for the <i>http</i> protocol among other things. Espcap uses the protocols.list
to help deterime the application level protocol in any given packet. This file is derived from tshark
by running the protocols.sh script in the conf directory. To ensure that espcap has only true Internet
protocols to choosed from, the entries in protocols.list that are not truly Internet protocols have
been commented out. Currently the commented out protocols include the following:
<pre>
# _ws.expert
# _ws.lua
# _ws.malformed
# _ws.number_string.decoding_error
# _ws.short
# _ws.type_length
# _ws.unreassembled
# data
# data-l1-events
# data-text-lines
# media
# null
</pre>
If there are any other protocols you believe should not be considered, then you can comment them out in 
this fashion. 

On the other hand If you get a little too frisky and comment out too many protocols or you just want to 
generate a fresh list, you can run the protocols.sh script in the following manner:
<ol>
<li>cd to the conf directory</li>
<li>Run the protocols.sh script which produces a clean protocol list in protocols.txt</li>
<li>Comment out the protocols in the list above and others you don't want to consider</li>
<li>Replace the contents of protocols.list with the contents of protocols.txt.
</ol>

## Known Issues

<ol>
<li>File capture mode sometime gets this error when dumping packets to stdout:  
<pre>'NoneType' object has no attribute 'add_reader'.</pre>
</li>
</ol>
