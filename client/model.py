# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
class Process(object):
    """
    Definition of Process model for ObjectListView
    """

    # ----------------------------------------------------------------------
    def __init__(self, name, pid, exe, user, cpu, mem, disk):
        """Constructor"""
        #  the process name
        self.name = name
        #  the process id
        self.pid = pid
        #  the process location
        self.exe = exe
        #  the pc that use the process
        self.user = user
        #  the cpu usage of the process
        self.cpu = cpu
        #  the memory usage of the process
        self.mem = mem
        #  the disk usage of the process
        self.disk = disk
