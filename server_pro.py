



def build_set_limits(type, limit):
    return f'02{type}{limit}'

def build_close_proc(name):
    return f'03{name}'

def build_ban_proc(pid):
    return f'04{pid}'

def build_close_sys(type):
    return f'05{type}'

def build_net_block():
    return "06deny"

def build_send_port(port):
    return f'07{port}'

def break_msg(msg):
    code = msg[1][:2]
    main_msg = str(msg[1][2:]).split(",")
    msg_lst = []
    msg_lst.append(code)
    for m in main_msg:
        msg_lst.append(m)
    return msg_lst





