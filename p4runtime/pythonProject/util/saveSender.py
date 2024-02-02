# coding=utf-8
from scapy.all import *
from scapy.layers.inet import UDP, IP
from scapy.layers.l2 import Ether

class _Packet:
    def __init__(self,srcIP='0,0,0,0',dstIP='0,0,0,0',port=0,protocol=0):
        self.srcIP =srcIP
        self.dstIP =dstIP
        self.port =port
        self.protocol=protocol

def Callback(packet):
    if IP in packet and UDP in packet:
        dst_ip = packet[IP].dst
        # 源IP
        src_ip = packet[IP].src

        dst_port = packet[UDP].dport
        value = ""
        if packet.haslayer(Raw):
            value = packet['Raw'].load

        dst_mac = packet['Ether'].dst

        src_mac = packet['Ether'].src


    # 转发数据
        forward_udp(dst_mac, src_mac, dst_ip, src_ip, dst_port, value)





def forward_udp(dst_mac, src_mac, dst_ip, src_ip, dst_port, value):

    # 创建以太网层
    eth = Ether(dst=dst_mac, src=src_mac)
    # 创建IP层
    ip = IP(src=src_ip, dst=dst_ip)
    # 创建UDP层
    udp = UDP(dport=dst_port + 1)
    # 创建一个UDP数据包
    packet = eth / ip / udp / Raw(value)

    # 通过原始套接字发送数据包，iface:指定网卡名称
    sendp(packet, iface="WLAN")


def Listening(ip='192.168.1.126', port='8888', count=-1, call=Callback):
    # 目标地址

    # 目标端口

    # 监听的规则，iface：监听的网卡名称
    print("start")

    global connection, p4info_helper
    # connection, p4info_helper = _Connection.GetConnection()
    sniff(filter="udp and host "+ip, count=count, prn=call)
if __name__ == '__main__':
    ip = '192.168.101.4'
    # connection, p4info_helper = _Connection.GetConnection()
    result = sniff(filter="udp and host "+ip, count=-1, prn=Callback)
