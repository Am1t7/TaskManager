



def build_proc(name, pid, exe, username, cpu, mem, disk):
    '''

    :param name: the proc name
    :param pid: the id of the proc
    :param exe: the location of the proc
    :param username: the pc username
    :param cpu: the cpu of the proc
    :param mem: the memory usage of the proc
    :param disk: the disk usage of the proc
    :return: the msg to send build according to the protocol
    '''
    return f'01{name},{pid},{exe},{username},{cpu},{mem},{disk}'

def build_mac(mac):
    '''

    :param mac: the mac address
    :return: the msg to send build according to the protocol
    '''
    return f'02{mac}'

def build_key(key):
    '''

    :param key: the key to send
    :return: the msg to send build according to the protocol
    '''
    return f'04{key}'


def build_done():
    '''

    :return: the msg to send build according to the protocol
    '''
    return f'03done'



def break_msg(msg):
    '''

    :param msg: the msg to break
    :return: the msg to send build according to the protocol
    '''
    code = msg[:2]
    main_msg = str(msg[2:]).split(",")
    msg_lst = []
    msg_lst.append(code)
    for m in main_msg:
        msg_lst.append(m)
    return msg_lst
