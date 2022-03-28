


def build_set_limits(type, limit):
    '''
    :param type: the type of the limit
    :param limit: the limit
    :return: the set limits msg
    '''
    return f'02{type},{limit}'

def build_close_proc(pid):
    '''

    :param pid: process id
    :return: close proc msg
    '''
    return f'03{pid}'

def build_ban_proc(name):
    '''

    :param name: the software to ban
    :return: ban proc msg
    '''
    return f'04{name}'

def build_close_sys():
    '''

    :return: the close system msg
    '''
    return f'05close'

def build_send_port(port):
    '''

    :param port: the port
    :return: builds the port msg
    '''
    return f'07{port}'

def build_unban_proc(name):
    '''

    :param name: the software name
    :return: the unban process msg
    '''
    return f'08{name}'

def build_close_pc():
    '''

    :return: the shutdown pc msg
    '''
    return f'09shut'

def build_key(key):
    '''

    :param key: the key
    :return: the key msg
    '''
    ret = b'11' + key
    return ret

def build_start():
    '''

    :return: the msg to start sending procs from client to server
    '''
    return "10start"
def break_msg(msg):
    '''

    :param msg:
    :return: the msg after breakdown
    '''
    code = msg[1][:2]
    #main_msg = str(msg[1][2:]).split(",")
    #msg_lst = []
    msg_lst = [code] + str(msg[1][2:]).split(",")
    print(msg_lst)
    '''
    msg_lst.append(code)
    for m in main_msg:
        msg_lst.append(m)
    '''
    return msg_lst





