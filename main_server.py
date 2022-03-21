import server_com
import server_pro
import serverGraphic
import queue
import setting
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
import AESCipher
import time


mac = ""
server_db = DB()
used_port = [setting.SERVER_PORT]
procs = []
bad_procs = []
key_lst = []
rsa_obj = RSAClass.RSAClass()
mac_ip_dic = {}
running = True


def get_port():
    port = random.randint(1000,2000)
    while port in used_port:
        port = random.randint(1000,2000)
    used_port.append(port)
    return port

def handle_sending_msgs(msg_q, comm):
    global running
    while running:
        mac, data_send = msg_q.get()
        if mac != "112233":
            comm.send_msg(mac_ip_dic[mac], str(data_send))

def gen_key():
    # string that contains all the letters + all the digits
    l = string_c.ascii_letters + "123456789"
    string = ''

    # randomizing a 16 char long string
    for i in range(16):
        char = random.choice(l)
        string += char

    # checking if the string isn't being used already as a symetric key
    if string in key_lst:
        return gen_key()

    else:
        # if it isn't being used , add to the symetric key list and return the key
        key_lst.append(string)
        return string


def main_loop(msg_q, comm):
    global procs
    global mac
    global bad_procs
    global running
    cpu_percent = 0
    mem_percent = 0
    disk_percent = 0
    count = 0
    pc_count = 0
    while running:
        data = msg_q.get()
        ip = data[0]
        #print("main server: ",ip,data)
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

            if msg[0] == "02":
                pc_count+=1
                mac = str(msg[1]).replace(":", "-")
                #cl_pub_key = msg[2]
                #sym_key = gen_key()
                #send_msg_q.put(RSAClass.encrypt_msg(sym_key,cl_pub_key))
                wx.CallAfter(pub.sendMessage, 'add', mac=mac, pass_limit=False, created=False)
                #wx.CallAfter(pub.sendMessage, 'add', mac = mac, pass_limit = False, created=False, count=pc_count)
                server_db.pc_limit_add(mac, 1000, 1000, 1000)
                #port = get_port()
                #comm = server_com.server_com(setting.SERVER_IP, port, msg_q)
                #build...(port)
                # sne msg
                mac_ip_dic[mac] = data[0]

            elif msg[0] == "01":
                p = Process(msg[1], msg[2], msg[3], msg[4], msg[5], msg[6], msg[7])
                procs.append(p)
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
                #proc = msg[1].split(",")
                #print(proc)

            elif msg[0] == "03":
                mac = None
                for ind in mac_ip_dic.keys():
                    if mac_ip_dic[ind] == ip:
                        mac = ind
                        break
                if mac:

                    wx.CallAfter(pub.sendMessage, f"{mac}update_server", procs = procs, bad_procs = bad_procs)
                    wx.CallAfter(pub.sendMessage, f"{mac}update_status_server", procsnum=count, totalcpu=cpu_percent, totalmem=mem_percent,totaldisk=disk_percent)
                    procs = []
                    bad_procs = []
                    count = 0
                    cpu_percent = 0
                    mem_percent = 0
                    disk_percent = 0

            #print("------------------------------------",msg)



def close_server():
    global running
    running = False
    msg_q.put("ffff")
    send_msg_q.put(("112233","close"))
    comm.stop_threads()



pub.subscribe(close_server ,'close_sr')
msg_q = queue.Queue()
send_msg_q = queue.Queue()
comm = server_com.server_com(setting.SERVER_IP,setting.SERVER_PORT,msg_q)
threading.Thread(target=main_loop, args=(msg_q,comm,)).start()
threading.Thread(target=handle_sending_msgs, args=(send_msg_q,comm,)).start()

server_db.add_user("amit", hashlib.md5("12345".encode()).hexdigest())

app = wx.App(False)
print("dffff", mac)
frame = serverGraphic.ServerFrame(send_q=send_msg_q, mac=mac)
app.MainLoop()