#!/usr/bin/python2

from config import * 

class Entry:
    def __init__(self):
        self.tableName = ''
        self.srcAddr = 00000000
        self.dstAddr = 00000000
        self.ingressPort = -1
        self.methodName = "set_port"
        self.port = -1
    
    def printEntry(self):
        print(self.tableName, self.srcAddr, self.dstAddr, self.ingressPort, self.methodName, self.port)


class Runtime:


    def __init__(self):
        self.table = []
        self.stack = []
    
    def comparer(self, target, basic, type):

        if target != basic:
            return False
        
        addr = (type, target)
        
        self.stack.append(addr)
        
        return True
    
    def forward(self, port):
        tmpSrcAddr = ''
        tmpDstAddr = ''
        if self.stack[0][0] == SRCTYPE :
            tmpSrcAddr = self.stack[0][1]
            tmpDstAddr = self.stack[1][1]
        else:
            tmpDstAddr = self.stack[0][1]
            tmpSrcAddr = self.stack[1][1]
        
        entry = Entry()
        entry.srcAddr = self.ipHexAddress(tmpSrcAddr)
        entry.dstAddr = self.ipHexAddress(tmpDstAddr)
        entry.tableName = "table_forward"
        entry.port = port
        self.table.append(entry)

    def endif(self):
        self.stack.pop()
    
    
    def save(self, portSave, portRedirect):
        tmpSrcAddr1 = ''
        tmpDstAddr1 = ''
        tmpDstAddr2 = ''
        if self.stack[0][0] == SRCTYPE :
            tmpSrcAddr1 = self.stack[0][1]
            tmpDstAddr1 = self.stack[1][1]
            tmpDstAddr2 = self.stack[1][1]
        else:
            tmpDstAddr2 = self.stack[0][1]
            tmpDstAddr1 = self.stack[0][1]
            tmpSrcAddr1 = self.stack[1][1]
        entry1 = Entry()
        entry2 = Entry()
        entry1.srcAddr = self.ipHexAddress(tmpSrcAddr1)
        entry1.dstAddr = self.ipHexAddress(tmpDstAddr1)
        entry2.dstAddr = self.ipHexAddress(tmpDstAddr2)
        entry1.tableName = "table_save"
        entry2.tableName = "table_redirect"

        entry1.port = portSave
        entry2.ingressPort = portSave
        entry2.port = portRedirect
        self.table.append(entry1)
        self.table.append(entry2)
    
    def encr(self, name, port):
        entry = Entry()
        if name == EGRESS :
            entry.tableName = "table_encr_egress"
        else:
            entry.tableName = "table_encr_ingress"

        entry.methodName = "encr_packet"
        entry.ingressPort = port
        self.table.append(entry)

    def decr(self, name, port):
        entry = Entry()
        if name == EGRESS :
            entry.tableName = "table_decr_egress"
        else:
            entry.tableName = "table_decr_ingress"

        entry.methodName = "decr_packet"
        entry.ingressPort = port
        self.table.append(entry)

    def ipHexAddress(self, ipAddr):
        int_parts = [int(part) for part in ipAddr.split('.')]
        ip_int = (int_parts[0] << 24) + (int_parts[1] << 16) + (int_parts[2] << 8) + int_parts[3]
        return ip_int

    def printTable(self):
        for x in self.table:
            print(x.tableName, x.srcAddr, x.dstAddr, x.ingressPort, x.methodName, x.port)
    
    def getTable(self):
        return self.table
