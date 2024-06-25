# coding=utf-8
from scapy.all import *
from scapy.layers.inet import UDP, IP ,TCP
from scapy.layers.l2 import Ether
from collections import defaultdict
import sys,StringIO

sent_packets = defaultdict(bool)

def save_packet(packet):
    buf = StringIO.StringIO()
    # 重定向
    old_stdout = sys.stdout
    sys.stdout = buf
    packet.show2()
    # 恢复标准输出
    sys.stdout = old_stdout
    output = buf.getvalue()
    with open('captured_packets.txt', 'a') as file:
        file.write(output + '\n\n')

def Callback(packet):
    global sent_packets
    # 获取数据包的摘要信息，用于唯一标识一个数据包
    packet_summary = packet.summary()
    # 检查是否已经发送过这个数据包，如果已发送则直接返回
    if sent_packets[packet_summary]:
        return 
    if IP in packet and (UDP in packet or TCP in packet):

        packet.show2()
        # 保存包信息到txt
        save_packet(packet)

        sent_packets[packet_summary]=True
        sendp(packet, iface="h2-eth0")


if __name__ == '__main__':
    ip = '10.0.1.1'
    # connection, p4info_helper = _Connection.GetConnection()
    result = sniff(filter="tcp or udp and host "+ip, count=-1, prn=Callback)
