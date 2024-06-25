#!/usr/bin/env python3
import os
import sys

from scapy.all import *


def handle_pkt(pkt):
    print("got a packet")
    pkt.show2()
    sys.stdout.flush()

def main():
    ifaces = [i for i in os.listdir('/sys/class/net/') if 'eth' in i]
    iface = ifaces[0]
    print("sniffing on %s" % iface)
    sys.stdout.flush()
    sniff(filter="tcp", iface = iface,
          prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()