#!/usr/bin/python2

from usrProgram.config import * 

# usr
def pipeline(packet, rt):
    if rt.comparer(packet.srcIP, "10.0.1.1", SRCTYPE):
        if rt.comparer(packet.dstIP, "10.0.3.3", DSTTYPE):
            rt.forward(3)
            rt.endif()
        if rt.comparer(packet.dstIP, "10.0.3.3", DSTTYPE):
            rt.save(2, 3)
            rt.endif()
        if rt.comparer(packet.dstIP, "10.0.3.3", DSTTYPE):
            rt.encr(INGRESS, 1)
            rt.decr(EGRESS, 3)
            rt.endif()
        rt.endif()







