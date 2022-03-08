


def build_set_limits(type, limit):
    return f'02{type},{limit}'

def build_close_proc(pid):
    return f'03{pid}'

def build_ban_proc(name):
    return f'04{name}'

def build_close_sys():
    return f'05close'

def build_net_block():
    return "06deny"

def build_send_port(port):
    return f'07{port}'

def build_unban_proc(name):
    return f'08{name}'

def build_close_pc():
    return f'09shut'

def build_key(key):
    # return f'11{key}'
    ret = f'11{key}'
    print(ret)
    return ret

def build_start():
    return "10start"
def break_msg(msg):
    code = msg[1][:2]
    main_msg = str(msg[1][2:]).split(",")
    msg_lst = []
    msg_lst.append(code)
    for m in main_msg:
        msg_lst.append(m)
    return msg_lst





