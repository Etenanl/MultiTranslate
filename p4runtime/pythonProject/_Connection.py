# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import struct
import os
import sys
from SocketServer import BaseRequestHandler, TCPServer
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '../../utils/'))

import p4runtime_lib.bmv2
import p4runtime_lib.helper
from usrProgram.Environment import Entry

global dpid
global dpid_p4helper
dpid_sw = {}
dpid_p4helper = {}


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print "123"  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.

def GetConnection(Address='127.0.0.1:50051', Device_id=0,
                  Proto_dump_file='/home/myp4/MultiTranslate/p4runtime/basic/logs/' + 's1' + '-p4runtime-requests.txt',
                  Info_file='/home/myp4/MultiTranslate/p4runtime/basic/build/basic.p4info',
                  Json_file='/home/myp4/MultiTranslate/p4runtime/basic/build/basic.json'):
    connection = p4runtime_lib.bmv2.Bmv2SwitchConnection(
        address=Address,
        device_id=Device_id,
        proto_dump_file=Proto_dump_file)
        
    connection.MasterArbitrationUpdate()

    print 'ok'
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(Info_file)
    # connection.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
    #                                      bmv2_json_file_path=Json_file)
    print 'pipeline'
    return connection, p4info_helper


def AddTableForward(connection, p4info_helper, entry):
    matchMap = {}
    matchMap['hdr.ipv4.srcAddr'] = (entry.srcAddr)
    matchMap['hdr.ipv4.dstAddr'] = (entry.dstAddr)
    actionParMap = {}
    actionParMap['port'] = entry.port
    table_entry = p4info_helper.buildTableEntry(
        table_name='MyIngress.table_forward',
        match_fields=matchMap,
        action_name='MyIngress.set_port',
        action_params=actionParMap
    )
    print table_entry
    connection.WriteTableEntry(table_entry)
    print "success"
    


def AddTableSave(connection, p4info_helper, entry):
    matchMap = {}
    matchMap['hdr.ipv4.srcAddr'] = (entry.srcAddr)
    matchMap['hdr.ipv4.dstAddr'] = (entry.dstAddr)
    actionParMap = {}
    actionParMap['port'] = entry.port
    table_entry = p4info_helper.buildTableEntry(
        table_name='MyIngress.table_save',
        match_fields=matchMap,
        action_name='MyIngress.set_port',
        action_params=actionParMap,
    )
    connection.WriteTableEntry(table_entry)


def AddTableRedirect(connection, p4info_helper, entry):
    matchMap = {}
    matchMap['hdr.ipv4.dstAddr'] = (entry.dstAddr)
    matchMap['standard_metadata.ingress_port'] = (entry.ingressPort)
    actionParMap = {}
    actionParMap["port"] = entry.port
    table_entry = p4info_helper.buildTableEntry(
        table_name='MyIngress.table_redirect',
        match_fields=matchMap,
        action_name='MyIngress.set_port',
        action_params=actionParMap,
    )
    connection.WriteTableEntry(table_entry)

def AddTableEncr_Ingress(connection,p4info_helper,entry):
    matchMap ={}
    matchMap['hdr.ipv4.srcAddr'] = (entry.srcAddr)
    matchMap['hdr.ipv4.dstAddr'] = (entry.dstAddr)
    matchMap['standard_metadata.ingress_port'] = (entry.ingressPort)
    actionParMap = {}
    table_entry = p4info_helper.buildTableEntry(
        table_name='MyIngress.table_encr_ingress',
        match_fields=matchMap,
        action_name='MyIngress.encr_packet',
        action_params=actionParMap,
    )
    connection.WriteTableEntry(table_entry)

def AddTableEncr_Egress(connection,p4info_helper,entry):
    matchMap ={}
    matchMap['hdr.ipv4.srcAddr'] = (entry.srcAddr)
    matchMap['hdr.ipv4.dstAddr'] = (entry.dstAddr)
    matchMap['standard_metadata.egress_port'] = (entry.ingressPort)
    actionParMap = {}
    table_entry = p4info_helper.buildTableEntry(
        table_name='MyEgress.table_encr_egress',
        match_fields=matchMap,
        action_name='MyEgress.encr_packet',
        action_params=actionParMap,
    )
    connection.WriteTableEntry(table_entry)

def AddTableDecr_Ingress(connection,p4info_helper,entry):
    matchMap ={}
    matchMap['hdr.ipv4.srcAddr'] = (entry.srcAddr)
    matchMap['hdr.ipv4.dstAddr'] = (entry.dstAddr)
    matchMap['standard_metadata.ingress_port'] = (entry.ingressPort)
    actionParMap = {}
    table_entry = p4info_helper.buildTableEntry(
        table_name='MyIngress.table_decr_ingress',
        match_fields=matchMap,
        action_name='MyIngress.decr_packet',
        action_params=actionParMap,
    )
    connection.WriteTableEntry(table_entry)

def AddTableDecr_Egress(connection,p4info_helper,entry):
    matchMap ={}
    matchMap['hdr.ipv4.srcAddr'] = (entry.srcAddr)
    matchMap['hdr.ipv4.dstAddr'] = (entry.dstAddr)
    matchMap['standard_metadata.egress_port'] = (entry.ingressPort)
    actionParMap = {}
    table_entry = p4info_helper.buildTableEntry(
        table_name='MyEgress.table_decr_egress',
        match_fields=matchMap,
        action_name='MyEgress.decr_packet',
        action_params=actionParMap,
    )
    connection.WriteTableEntry(table_entry)

def AddTableTest(connection, p4info_helper):
    matchMap = {}
    matchMap['hdr.ipv4.srcAddr'] = (1677777743)
    matchMap['hdr.ipv4.dstAddr'] = (0x11)
    actionParMap = {}
    actionParMap['port'] = 3
    table_entry = p4info_helper.buildTableEntry(
        table_name='MyIngress.table_forward',
        match_fields=matchMap,
        action_name='MyIngress.set_port',
        action_params=actionParMap
    )
    print table_entry
    connection.WriteTableEntry(table_entry)
    

if __name__ == '__main__':
    # First we start the Server Socket for Modal loading
    # ModalLoadingThread = threading.Thread(target=ModalLoadingFun,args=(modal_loading_server_port,))
    # ModalLoadingThread.setDaemon(True)
    # ModalLoadingThread.start()

    # RuntimeThread = threading.Thread(target=RuntimeFun,args=(runtime_server_port,))
    # RuntimeThread.setDaemon(True)
    # RuntimeThread.start()
    # connection, p4info_helper = GetConnection()
    # AddTableTest(connection, p4info_helper)
    pass
    
    
    
