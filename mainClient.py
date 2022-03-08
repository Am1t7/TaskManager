import client_com
import client_pro
import clientGraphic
import queue
import setting
import wx
import threading
from pubsub import pub
import uuid
import RSAClass
import AESCipher


mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8 * 6, 8)][::-1]).upper()
rsa_obj = RSAClass.RSAClass()
rsa_pub_key = rsa_obj.get_public_key_pem()

def handle_sending_msgs(msg_q, comm):
    while True:
        procs = msg_q.get()
        for p in procs:
            comm.send(client_pro.build_proc(p.name, p.pid, p.exe, p.user, p.cpu, p.mem, p.disk))
            #comm.send(client_pro.build_bad_procs(p.name, p.pid, p.exe, p.name, p.cpu, p.mem, p.disk))
        comm.send(client_pro.build_done())

        #time.sleep(10)
        #comm.send(str(procs[0].name))
        # jeson
        # build protocol
        #if not procs_comm is None:
            # procs_comm.send()


def main_loop(msg_q):
    while True:
        data = msg_q.get()
        msg = client_pro.break_msg(data)

        if msg[0] == "03":
            wx.CallAfter(pub.sendMessage, 'kill', pid=int(msg[1]))

        if msg[0] == "02":
            wx.CallAfter(pub.sendMessage, 'update_limits', type=str(msg[1]), value= msg[2])

        if msg[0] == "04":
            wx.CallAfter(pub.sendMessage, 'ban', mac=mac, soft=msg[1])

        if msg[0] == "08":
            wx.CallAfter(pub.sendMessage, 'del_ban', mac=mac, soft=msg[1])

        if msg[0] == "09":
            wx.CallAfter(pub.sendMessage, 'shut',)

        if msg[0] == "05":
            #frame.Destroy()
            wx.CallAfter(pub.sendMessage, 'close', )
            client_com.Client_com.get_socket(comm).close()

        if msg[0] == "10":
            wx.CallAfter(pub.sendMessage, 'start', )

        # if  create client
        # break -> port
        # procs_comm = client_com.Client_com(setting.SERVER_IP,port,recv_msg_q)
        # procs


        print("client recv ---------------------------",msg)




procs_comm = None

recv_msg_q = queue.Queue()
send_msg_q = queue.Queue()
comm = client_com.Client_com(setting.SERVER_IP,setting.SERVER_PORT,recv_msg_q)
threading.Thread(target=main_loop, args=(recv_msg_q,)).start()
threading.Thread(target=handle_sending_msgs, args=(send_msg_q,comm,)).start()


app = wx.App(False)
frame = clientGraphic.MainFrame(send_msg_q)
app.MainLoop()