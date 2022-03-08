



def build_proc(name, pid, exe, username, cpu, mem, disk):
    return f'01{name},{pid},{exe},{username},{cpu},{mem},{disk}'

def build_mac(mac, pub_key):
    return f'02{mac},{pub_key}'


def build_response(func_code, type):
    return f'{func_code}{type}'


def build_done():
    return f'03done'



def break_msg(msg):
    code = msg[:2]
    main_msg = str(msg[2:]).split(",")
    msg_lst = []
    msg_lst.append(code)
    for m in main_msg:
        msg_lst.append(m)
    return msg_lst
