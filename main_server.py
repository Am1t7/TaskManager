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




used_port = [setting.SERVER_PORT]
procs = []
def get_port():
    port = random.randint(1000,2000)
    while port in used_port:
        port = random.randint(1000,2000)
    used_port.append(port)
    return port

def main_loop(msg_q, comm):
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
            procs.append(msg[1])
            if msg_q.empty():
                wx.CallAfter(pub.sendMessage, 'update_server', procs = procs)


        print("------------------------------------",msg)



msg_q = queue.Queue()
comm = server_com.server_com(setting.SERVER_IP,setting.SERVER_PORT,msg_q)
threading.Thread(target=main_loop, args=(msg_q,comm,)).start()


app = wx.App(False)
frame = serverGraphic.ServerFrame()
app.MainLoop()