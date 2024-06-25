# coding=utf-8

from scapy.all import *

from scapy.layers.inet import UDP, IP ,TCP

from scapy.layers.l2 import Ether

from usrProgram.UsrPrograming import pipeline

from usrProgram.Environment import Runtime,Entry



import _Connection

class _Packet:

    def __init__(self,srcIP='0,0,0,0',dstIP='0,0,0,0',port=0,protocol=0):

        self.srcIP =srcIP

        self.dstIP =dstIP

        self.port =port

        self.protocol=protocol



def Callback(packet):

    if IP in packet and (UDP in packet or TCP in packet):

        dst_ip = packet[IP].dst

        # 源IP

        src_ip = packet[IP].src

        # 目的端口

        # dst_port = packet[UDP].dport

        # 数据

        # value = packet['Raw'].load

        # 目的MAC地址

        # dst_mac = packet['Ether'].dst

        # 源MAC地址

        # src_mac = packet['Ether'].src

        '''print(dst_ip)

        print(src_ip)

        print(dst_port)

        print(value)

        print(dst_mac)

        print(src_mac)'''



        p = _Packet(srcIP = src_ip,dstIP = dst_ip)

        # print dst_ip

        ######################

        # do something

        rt = Runtime()

        pipeline(p, rt)

        entries = rt.getTable()

        print entries

        ######################

        for entry in entries:

            entry.printEntry()
            n = len(loadedEntries)
            print n
            print loadedEntries
            loadedEntries.add(Print(entry))
            if(n != len(loadedEntries)):
                try:
                    if entry.tableName == 'table_forward':
                        _Connection.AddTableForward(connection, p4info_helper,entry)
                    elif entry.tableName == 'table_save':
                        _Connection.AddTableSave(connection, p4info_helper,entry)
                    elif entry.tableName == 'table_redirect':
                        _Connection.AddTableRedirect(connection, p4info_helper,entry)
                    elif entry.tableName == 'table_encr_ingress':
                        _Connection.AddTableEncr_Ingress(connection, p4info_helper,entry)
                    elif entry.tableName == 'table_encr_egress':
                        _Connection.AddTableEncr_Egress(connection, p4info_helper,entry)   
                    elif entry.tableName == 'table_decr_ingress':
                        _Connection.AddTableDecr_Ingress(connection, p4info_helper,entry) 
                    elif entry.tableName == 'table_decr_egress':
                        _Connection.AddTableDecr_Egress(connection, p4info_helper,entry) 
                finally:
                    pass
            


    # 转发数据

    # forward_udp(dst_mac, src_mac, dst_ip, src_ip, dst_port, value)

def Print(entry):
    return ""+str(entry.tableName)+str(entry.srcAddr)+str(entry.dstAddr)\
           +str(entry.ingressPort)+str(entry.methodName)

def Listening(ip='172.16.1.74', port='8888', count=-1, call=Callback):

    # 目标地址



    # 目标端口



    # 监听的规则，iface：监听的网卡名称

    # print("start1")



    '''global connection, p4info_helper

    connection, p4info_helper = _Connection.GetConnection()

    sniff(filter="udp and host "+ip, count=count, prn=call)

    print(1)'''

    global connection, p4info_helper
    global loadedEntries
    loadedEntries = {""}


    connection, p4info_helper = _Connection.GetConnection()

    sniff(filter="ip", iface="s2-eth1", count=count, prn=call)



if __name__ == '__main__':

    pass


