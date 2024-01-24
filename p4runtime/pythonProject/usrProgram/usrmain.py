#!/usr/bin/python2

from UsrPrograming import pipeline
from Environment import Runtime

class Packet:
    src = "10.0.1.1"
    dst = "10.0.3.3"

packet = Packet()

rt = Runtime()
pipeline(packet, rt)
entries = rt.getTable()

for e in entries:
    e.printEntry()

