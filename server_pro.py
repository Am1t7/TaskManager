



def build_set_limits(type, limit):
    return f'02{type}{limit}'

def build_close_proc(name):
    return f'03{name}'

def build_ban_proc(name):
    return f'04{name}'

def build_close_sys(type):
    return f'05{type}'

def build_net_block():
    return "06deny"

def break_msg(msg):
    code = msg[:2]
    main_msg  = msg[2:].split(",")
    msg_tuple = ()




