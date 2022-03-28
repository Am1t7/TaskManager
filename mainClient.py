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

# the mac address of the pc
mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8 * 6, 8)][::-1]).upper()
rsa_obj = RSAClass.RSAClass()
rsa_pub_key = rsa_obj.get_public_key_pem()
# keeps the thread alive until false
running = True

def handle_sending_msgs(msg_q, comm):
    '''
    handle the msg that send from the client to the server
    :param msg_q: the q of msg to send
    :param comm: the communication object
    :return:
    '''
    global running
    while running:
        #get from q
        procs = msg_q.get()
        if procs != "close":
            for p in procs:
                #send
                comm.send(client_pro.build_proc(p.name, p.pid, p.exe, p.user, p.cpu, p.mem, p.disk))
            comm.send(client_pro.build_done())

def main_loop(msg_q):
    '''
    the main loop that gets msg from server
    :param msg_q: the q of recv msg
    :return:
    '''
    global running
    while running:
        #gets the data
        data = msg_q.get()
        msg = client_pro.break_msg(data)

        #check if the code is "03" and call the graphic
        if msg[0] == "03":
            wx.CallAfter(pub.sendMessage, 'kill', pid=int(msg[1]))
        # check if the code is "02" and call the graphic
        elif msg[0] == "02":
            wx.CallAfter(pub.sendMessage, 'update_limits', type=str(msg[1]), value= msg[2])
        # check if the code is "04" and call the graphic
        elif msg[0] == "04":
            wx.CallAfter(pub.sendMessage, 'ban', mac=mac, soft=msg[1])
        # check if the code is "08" and call the graphic
        elif msg[0] == "08":
            wx.CallAfter(pub.sendMessage, 'del_ban', mac=mac, soft=msg[1])
        # check if the code is "09" and call the graphic
        elif msg[0] == "09":
            wx.CallAfter(pub.sendMessage, 'shut',)
        # check if the code is "05" and call the graphic
        elif msg[0] == "05":
            wx.CallAfter(pub.sendMessage, 'close', )
            client_com.Client_com.get_socket(comm).close()
            close_client()
        # check if the code is "10" and call the graphic
        elif msg[0] == "10":
            wx.CallAfter(pub.sendMessage, 'start', )

def close_client():
    '''
    closing the client
    :return:
    '''
    global running
    running = False
    recv_msg_q.put("ffff")
    send_msg_q.put("close")
    comm.stop_threads()


# pub subscribe
pub.subscribe(close_client ,'close_cl')


procs_comm = None
# the recv q
recv_msg_q = queue.Queue()
#send q
send_msg_q = queue.Queue()
#communication object
comm = client_com.Client_com(setting.SERVER_IP,setting.SERVER_PORT,recv_msg_q)
#starting the threads
threading.Thread(target=main_loop, args=(recv_msg_q,)).start()
threading.Thread(target=handle_sending_msgs, args=(send_msg_q,comm,)).start()

#starts the graphic
app = wx.App(False)
frame = clientGraphic.MainFrame(send_msg_q)
app.MainLoop()