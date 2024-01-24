#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header ipv4_options_t {
    varbit<320> options;
}

header tcp_t {
    bit<16>   srcPort;
    bit<16>   dstPort;
    bit<32>   seqNum;
    bit<32>   ackNum;
    bit<4>    off;
    bit<12>   flags;
    bit<16>   window;
    bit<16>   checkSum;
    bit<16>   urgentPoint;
    /* Assume there are no option fields in TCP */
}

header udp_t {
    bit<16>   srcPort;
    bit<16>   dstPort;
    bit<16>   length;
    bit<16>   checkSum;
}

struct metadata {
    /* empty */
}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    ipv4_options_t ipv4_options;
    tcp_t        tcp;
    udp_t        udp;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select (hdr.ipv4.ihl) {
           5: parse_ipv4_next;
           _: parse_ipv4_options;
        }
    }

    state parse_ipv4_options {
       // use information in the ipv4 header to compute the number
       // of bits to extract
       packet.extract(hdr.ipv4_options, (bit<32>)(((bit<16>)hdr.ipv4.ihl - 5) * 32));
       transition parse_ipv4_next;
   }

    state parse_ipv4_next {
        transition select (hdr.ipv4.protocol) {
           0x06: parse_tcp;
           0x11: parse_udp;
           default: accept;
        }
    }

    state parse_tcp {
        packet.extract(hdr.tcp);
        transition accept;
    }

    state parse_udp {
        packet.extract(hdr.udp);
        transition accept;
    }
    
}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {   
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    action drop() {
        mark_to_drop();
    }
    
    action ipv4_forward(egressSpec_t port) {
        standard_metadata.egress_spec = port;
        //hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    action PacketIn(){
        standard_metadata.egress_spec = 3;
    }
    
    table ipv4 {
        key = {
            hdr.ipv4.srcAddr: ternary;
            hdr.ipv4.dstAddr: ternary;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
            PacketIn;
        }
        size = 1024;
        default_action = PacketIn;
    }
    
    apply {
        if (hdr.ipv4.isValid()) {
            ipv4.apply();
        }
    }

    //a simple test
    /*action output(bit<9> port)
    {
        standard_metadata.egress_spec = port;
    }
    
    table simple_table {
        key = {
           standard_metadata.ingress_port : exact;
        }
        actions = {
           output;
           drop;
        }
        size = 1024;
        default_action = drop();
    }
    
    apply {
        simple_table.apply();
    }*/
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
	update_checksum(
	    hdr.ipv4.isValid(),
            { hdr.ipv4.version,
	      hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.ipv4_options);
        packet.emit(hdr.tcp);
        packet.emit(hdr.udp);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
