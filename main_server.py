import server_com
import server_pro
import serverGraphic
import queue
import wx
import threading
from pubsub import pub
import setting
import random
from model import Process
from serverDB import DB
import hashlib
import string as string_c
import RSAClass

# the mac address of the client pc
mac = ""
server_db = DB()
used_port = [setting.SERVER_PORT]
# all the processes that runs on the client pc
procs = []
# processes that passed the limits
bad_procs = []
key_lst = []
rsa_obj = RSAClass.RSAClass()
mac_ip_dic = {}
# keeps the thread alive until false
running = True



def handle_sending_msgs(msg_q, comm):
    '''
    sending msg to the client
    :param msg_q:
    :param comm:
    :return:
    '''
    global running
    while running:
        mac, data_send = msg_q.get()
        #check if the server has been closed
        if mac != "112233":
            comm.send_msg(mac_ip_dic[mac], str(data_send))

def gen_key():
    '''

    :return: the generated key
    '''
    # string that contains all the letters + all the digits
    st_all = string_c.ascii_letters + "123456789"
    string = ''

    # randomizing a 16 char long string
    for i in range(16):
        char = random.choice(st_all)
        string += char

    # checking if the string isn't being used already as a symetric key
    if string in key_lst:
        return gen_key()

    else:
        # if it isn't being used , add to the symetric key list and return the key
        key_lst.append(string)
        return string


def main_loop(msg_q):
    '''
    the main loop that recv the msg from the client
    :param msg_q: the recv msg q
    :return:
    '''
    global procs
    global mac
    global bad_procs
    global running
    cpu_percent = 0
    mem_percent = 0
    disk_percent = 0
    count = 0
    while running:
        #getting the data from the q
        data = msg_q.get()
        ip = data[0]
        #check if need to delete a pc from the connected pc
        if data[1] == "del":
            mac = None
            for ind in mac_ip_dic.keys():
                if mac_ip_dic[str(ind)] == ip:
                    mac = ind
                    break
            if mac:
                wx.CallAfter(pub.sendMessage, 'del', mac=mac)
        else:
            msg = server_pro.break_msg(data)
            # check if the message code is "02"
            if msg[0] == "02":
                #adding a pc to the display of connected pc
                mac = str(msg[1]).replace(":", "-")
                wx.CallAfter(pub.sendMessage, 'add', mac=mac, pass_limit=False, created=False)
                server_db.pc_limit_add(mac, 1000, 1000, 1000)
                mac_ip_dic[mac] = data[0]
            #check if the code is "01"
            elif msg[0] == "01":
                #building the process object for the procs that recived from client
                p = Process(msg[1], msg[2], msg[3], msg[4], msg[5], msg[6], msg[7])
                procs.append(p)
                #check if one of the procs passed a limit
                if float(msg[5]) > float(server_db.get_cpu_limits_value(mac)):
                    bad_procs.append(procs.index(p))
                if float(msg[6]) > float(server_db.get_mem_limits_value(mac)):
                    bad_procs.append(procs.index(p))
                if float(msg[7]) > float(server_db.get_disk_limits_value(mac)):
                    bad_procs.append(procs.index(p))
                for s in server_db.get_soft_value(mac):
                    if str(s) == p.name:
                        bad_procs.append(procs.index(p))
                cpu_percent += float(msg[5])
                mem_percent += float(msg[6])
                disk_percent += float(msg[7])
                count += 1
            #check if the client done send him processes
            elif msg[0] == "03":
                mac = None
                for ind in mac_ip_dic.keys():
                    if mac_ip_dic[ind] == ip:
                        mac = ind
                        break
                if mac:
                    #if done calling update graphic
                    wx.CallAfter(pub.sendMessage, f"{mac}update_server", procs = procs, bad_procs = bad_procs)
                    wx.CallAfter(pub.sendMessage, f"{mac}update_status_server", procsnum=count, totalcpu=cpu_percent, totalmem=mem_percent,totaldisk=disk_percent)
                    procs = []
                    bad_procs = []
                    count = 0
                    cpu_percent = 0
                    mem_percent = 0
                    disk_percent = 0

def close_server():
    '''
    closing the server
    :return:
    '''
    global running
    running = False
    msg_q.put("ffff")
    send_msg_q.put(("112233","close"))
    comm.stop_threads()


# pub subscribe
pub.subscribe(close_server ,'close_sr')
#the recv q
msg_q = queue.Queue()
#the send q
send_msg_q = queue.Queue()
#communicatin object
comm = server_com.server_com(setting.SERVER_IP,setting.SERVER_PORT,msg_q)
#starts threads
threading.Thread(target=main_loop, args=(msg_q,)).start()
threading.Thread(target=handle_sending_msgs, args=(send_msg_q,comm,)).start()

server_db.add_user("amit", hashlib.md5("12345".encode()).hexdigest())

#start the graphic
app = wx.App(False)
frame = serverGraphic.ServerFrame(send_q=send_msg_q, mac=mac)
app.MainLoop()