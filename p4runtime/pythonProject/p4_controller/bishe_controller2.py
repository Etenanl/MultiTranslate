#!/usr/bin/env python2
import struct
import os
import sys
from SocketServer import BaseRequestHandler, TCPServer

# Import P4Runtime lib from parent utils dir
# Probably there's a better way of doing this.
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '../../utils/'))
import p4runtime_lib
import p4runtime_lib.helper

global dpid
global dpid_p4helper
dpid_sw = {}
dpid_p4helper = {}

def readTableRules(p4info_helper, sw , data_dpid):
    """
    Reads the table entries from all tables on the switch.

    :param p4info_helper: the P4Info helper
    :param sw: the switch connection
    """
    print '\n----- Reading tables rules for %s, dpid is %d -----' % (sw.name,data_dpid)
    for response in sw.ReadTableEntries():
        for entity in response.entities:
            entry = entity.table_entry
            # TODO For extra credit, you can use the p4info_helper to translate
            #      the IDs the entry to names
            table_name = p4info_helper.get_tables_name(entry.table_id)
            print '%s: ' % table_name,
            for m in entry.match:
                print p4info_helper.get_match_field_name(table_name, m.field_id),
                print '%r' % (p4info_helper.get_match_field_value(m),),
            action = entry.action.action
            action_name = p4info_helper.get_actions_name(action.action_id)
            print '->', action_name,
            for p in action.params:
                print p4info_helper.get_action_param_name(action_name, p.param_id),
                print '%r' % p.value,
            print

def printASCII(str):
    a=[0]*len(str)
    i=0

    for x in str:
        a[i]=value = (struct.unpack('>B' ,str[i:i+1]))[0]
        i=i+1
    result=list(a)
    print result

def dealwithMsg(ClientSocket):
    # deal with the messaage form the program environment
    rest = ''
    while True:
        data = rest+ClientSocket.recv(2048)  #this function is blocked when there is no message arrived
        rest = ''
        '''printASCII(data)'''

        index = 0
        data_len = len(data)
        while(index<data_len):
            if(index+4>data_len):
                rest = data[index:data_len]
                break

            msg_length = (struct.unpack('>H' ,data[(index+2):(index+4)]))[0]
            if(msg_length<=data_len-index):
                data_type = (struct.unpack('>H' ,data[(index):(index+2)]))[0]
                if(data_type==1):
                    # Then send the reply
                    ClientSocket.sendall(b'\x00\x02\x00\x08\x50\x34\x00\x00')
                    ClientSocket.shakeIsComplete = True
                    print "Received a request of controller Type. And send the reply."
                elif(data_type==3):
                    # Then send the reply
                    ClientSocket.sendall(b'\x00\x04\x00\x08\x00\x00\x00\x00')
                    print "Received a request of echo form the Program Environment. And send the reply."
                elif(data_type==6):
                    # This is a command to connect a p4 switch
                    data_dpid = (struct.unpack('>I' ,data[(index+4):(index+8)]))[0]
                    data_sw_ip = (struct.unpack('>I' ,data[(index+8):(index+12)]))[0]
                    sw_ip_str = int_to_ipstr(data_sw_ip)
                    data_sw_port = (struct.unpack('>H' ,data[(index+12):(index+14)]))[0]

                    '''print '********************************************'
                    print sw_ip_str+":"+ str(data_sw_port)
                    print data_dpid
                    print 'logs/'+str(data_dpid)+'-p4runtime-requests.txt'
                    print '********************************************'''

                    s = p4runtime_lib.bmv2.Bmv2SwitchConnection(
                         address=sw_ip_str+":"+ str(data_sw_port),
                         device_id=data_dpid,
                         proto_dump_file='logs/'+str(data_dpid)+'-p4runtime-requests.txt')
                    # Send master arbitration update message to establish this controller as
                    # master (required by P4Runtime before performing any other write operation)
                    s.MasterArbitrationUpdate()
                    dpid_sw[data_dpid]=s
                    print "Switch (dpid = "+str(data_dpid)+") has connected. And Master has set. "
                elif(data_type==7):
                    # This is command to download the .json fiel and .p4info file
                    data_dpid = (struct.unpack('>I' ,data[(index+4):(index+8)]))[0]
                    sw = dpid_sw[data_dpid];
                    pathStr = data[index+8:index+msg_length];

                    print '************************************************'
                    print (struct.unpack('>H' ,data[(index):(index+2)]))[0]
                    print (struct.unpack('>H' ,data[(index+2):(index+4)]))[0]
                    print pathStr
	            print "path"
                    print data
                    print '************************************************'

                    p4info_helper = p4runtime_lib.helper.P4InfoHelper(pathStr + '.p4info')
                    dpid_p4helper[data_dpid] = p4info_helper

                    print '************************************************'
                    print data_dpid
                    print p4info_helper.p4info
                    print pathStr+".json"
                    print '************************************************'

                    sw.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                   bmv2_json_file_path=pathStr+".json")
                    print "Installed P4 Program using SetForwardingPipelineConfig on dpid = "+str(data_dpid)
                elif(data_type==9):
                    # This is a message to install the flow rule
                    data_dpid = (struct.unpack('>I' ,data[(index+4):(index+8)]))[0]
                    offset = index+8;

                    tableNameLen = (struct.unpack('>B' ,data[offset:offset+1]))[0]
                    offset = offset+1;
                    tableName = data[offset:offset+tableNameLen];
                    offset = offset+tableNameLen;

                    matchNum = (struct.unpack('>B' ,data[offset:offset+1]))[0]
                    offset = offset + 1;
                    matchMap = {}

                    while matchNum>0:
                        matchNameLen = (struct.unpack('>B' ,data[offset:offset+1]))[0]
                        offset=offset+1;
                        matchName = data[offset:offset+matchNameLen]
                        offset=offset+matchNameLen;
                        matchValueLen = (struct.unpack('>B' ,data[offset:offset+1]))[0]
                        offset = offset+1
                        matchValue = data[offset:offset+matchValueLen]
                        offset = offset+matchValueLen
                        matchMask = data[offset:offset+matchValueLen]
                        offset = offset+matchValueLen
                        matchRealValue = 0
                        matchRealMask = 0
                        index_i=0
                        while(index_i<matchValueLen):
                            matchRealValue = matchRealValue*256+(struct.unpack('>B' ,matchValue[index_i:index_i+1]))[0]
                            matchRealMask = matchRealMask*256+(struct.unpack('>B' ,matchMask[index_i:index_i+1]))[0]
                            index_i = index_i+1
                        if(matchRealMask!=0):
                            matchMap[matchName] = (matchRealValue,matchRealMask)
                        matchNum = matchNum-1;


                    actionNameLen = (struct.unpack('>B' ,data[offset:offset+1]))[0]
                    offset = offset+1;
                    actionName = data[offset:offset+actionNameLen]
                    offset = offset+actionNameLen
                    actionParNum = (struct.unpack('>B' ,data[offset:offset+1]))[0]
                    offset = offset + 1
                    actionParMap = {}
                    while actionParNum>0:
                        actionParNameLen = (struct.unpack('>B' ,data[offset:offset+1]))[0]
                        offset=offset+1
                        actionParName = data[offset:offset+actionParNameLen]
                        offset=offset+actionParNameLen
                        actionParValLen = (struct.unpack('>B' ,data[offset:offset+1]))[0]
                        offset = offset+1
                        actionParVal = data[offset:offset+actionParValLen]
                        offset = offset+actionParValLen
                        actionParRealVal=0
                        index_i=0
                        while(index_i<actionParValLen):
                            actionParRealVal =actionParRealVal*256+(struct.unpack('>B' ,actionParVal[index_i:index_i+1]))[0]
                            index_i = index_i+1
                        actionParMap[actionParName]=actionParRealVal
                        actionParNum = actionParNum-1

                    prior = (struct.unpack('>H' ,data[offset:offset+2]))[0]

                    '''print '************************************************'
                    print data_dpid
                    print tableName
                    print matchMap
                    print actionName
                    print actionParMap
                    print prior
                    print '************************************************'''

                    # install the rule
                    table_entry = dpid_p4helper[data_dpid].buildTableEntry(
                        table_name=tableName,
                        match_fields=matchMap,
                        action_name=actionName,
                        action_params=actionParMap,
                        priority=prior)
                    sw = dpid_sw[data_dpid]
                    sw.WriteTableEntry(table_entry)
                    print "Installed P4 rule on dpid = "+str(data_dpid)
                    readTableRules(dpid_p4helper[data_dpid], sw , data_dpid)




                else:
                    print "other type msg"
                ########################################################
                # the other type msg
                ########################################################
                index = index+ msg_length
            else:
                rest = data[index:data_len]
                break


def int_to_ipstr(num):
    s = []
    for i in range(4):
        s.append(str(num %256))
        num /= 256
    return '.'.join(s[::-1])


def ModalLoadingFun(serPort):
    ModalLoadingServ = TCPServer(('', int(serPort)), ModalLoadingHandler)
    print "ModalLoading Server start.\n"
    ModalLoadingServ.serve_forever()


class ModalLoadingHandler(BaseRequestHandler):
    def handle(self):
        print 'A modal Loading has connected successfully!\n'
        dealwithMsg(self.request)

def RuntimeFun(serPort):
    RuntimeServ = TCPServer(('', int(serPort)), RuntimeHandler)
    print "RuntimeSystem Server start.\n"
    RuntimeServ.serve_forever()



class RuntimeHandler(BaseRequestHandler):
    def handle(self):
        print 'A Runtime System has connected successfully!\n'
        dealwithMsg(self.request)


if __name__ == '__main__':
   

   # First we start the Server Socket for Modal loading
    #ModalLoadingThread = threading.Thread(target=ModalLoadingFun,args=(modal_loading_server_port,))
    #ModalLoadingThread.setDaemon(True)
    #ModalLoadingThread.start()

    #RuntimeThread = threading.Thread(target=RuntimeFun,args=(runtime_server_port,))
    #RuntimeThread.setDaemon(True)
    #RuntimeThread.start()
    s = p4runtime_lib.bmv2.Bmv2SwitchConnection(
                       address='127.0.0.1:50052',
                       device_id=1,
                       proto_dump_file='logs/'+'2'+'-p4runtime-requests.txt')
                    # Send master arbitration update message to establish this controller as
                    # master (required by P4Runtime before performing any other write operation)
    s.MasterArbitrationUpdate()
    print 'ok'
    p4info_helper = p4runtime_lib.helper.P4InfoHelper('/home/lxh/p4_pof_new_v1.0/bishe/ipv4.p4info')
    s.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                   bmv2_json_file_path='/home/lxh/p4_pof_new_v1.0/bishe/ipv4.json')
    print 'pipeline'

    matchMap={}
    matchMap['hdr.ipv4.srcAddr'] = (0xA000101,4294967295)
    matchMap['hdr.ipv4.dstAddr'] = (0xA000102,4294967295)
    actionParMap={}
    actionParMap["port"] = 2
    table_entry = p4info_helper.buildTableEntry(
                        table_name='MyIngress.ipv4',
                        match_fields=matchMap,
                        action_name='MyIngress.ipv4_forward',
                        action_params=actionParMap,
                       )
                   
    s.WriteTableEntry(table_entry)
    
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ipv4",
        match_fields={
            "hdr.ipv4.srcAddr": (0xA000102,4294967295),
	    "hdr.ipv4.dstAddr": (0xA000101,4294967295),
        },
        action_name="MyIngress.ipv4_forward",
        action_params={
            "port": 1
        })
    s.WriteTableEntry(table_entry)
    
# tag-forward
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.tagIdentify",
        match_fields={
            "hdr.tag.outport": (1,0xffff),
        },
        action_name="MyIngress.tag_forward",
        action_params={
            "port": 1
        })
    s.WriteTableEntry(table_entry)

    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.tagIdentify",
        match_fields={
            "hdr.tag.outport": (2,0xffff),
        },
        action_name="MyIngress.tag_forward",
        action_params={
            "port": 2
        })
    s.WriteTableEntry(table_entry)
    #print "Switch (dpid = "+str(data_dpid)+") has connected. And Master has set. "
    print 'dd'
    #while(True):
     #   pass
