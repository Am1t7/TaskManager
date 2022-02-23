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




used_port = [setting.SERVER_PORT]
procs = []
def get_port():
    port = random.randint(1000,2000)
    while port in used_port:
        port = random.randint(1000,2000)
    used_port.append(port)
    return port

def handle_sending_msgs(msg_q, comm):
    while True:
        data_send = msg_q.get()
        print(data_send)
        #send_msg = server_pro.break_msg(data_send)
        comm.send_msg('127.0.0.1', str(data_send))

def main_loop(msg_q, comm):
    global procs
    cpu_percent = 0
    mem_percent = 0
    disk_percent = 0
    count = 0
    while True:
        data = msg_q.get()
        msg = server_pro.break_msg(data)

        if msg[0] == "02":
            wx.CallAfter(pub.sendMessage, 'add', mac = str(msg[1]))
            #port = get_port()
            #comm = server_com.server_com(setting.SERVER_IP, port, msg_q)
            #build...(port)
            # sne msg

        elif msg[0] == "01":
            procs.append(Process(msg[1], msg[2], msg[3], msg[4], msg[5], msg[6], msg[7]))
            cpu_percent += float(msg[5])
            mem_percent += float(msg[6])
            disk_percent += float(msg[7])
            count += 1
            #proc = msg[1].split(",")
            #print(proc)

        elif msg[0] == "03":
            wx.CallAfter(pub.sendMessage, 'update_server', procs = procs)
            wx.CallAfter(pub.sendMessage, 'update_status_server', procsnum=count, totalcpu=cpu_percent, totalmem=mem_percent,totaldisk=disk_percent)
            procs = []
            count = 0
            cpu_percent = 0
            mem_percent = 0
            disk_percent = 0

        #elif msg[0] == "04":
         #   wx.CallAfter(pub.sendMessage, 'update_status_server', procsnum=msg[1], totalcpu=msg[2], totalmem=msg[3], totaldisk=msg[4])


        print("------------------------------------",msg)



msg_q = queue.Queue()
send_msg_q = queue.Queue()
comm = server_com.server_com(setting.SERVER_IP,setting.SERVER_PORT,msg_q)
threading.Thread(target=main_loop, args=(msg_q,comm,)).start()
threading.Thread(target=handle_sending_msgs, args=(send_msg_q,comm,)).start()

app = wx.App(False)
frame = serverGraphic.ServerFrame(send_q=send_msg_q)
app.MainLoop()