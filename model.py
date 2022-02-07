########################################################################
class Process(object):
    """
    Definition of Process model for ObjectListView
    """

    #----------------------------------------------------------------------
    def __init__(self, name, pid, exe, user, cpu, mem, disk, desc=None):
        """Constructor"""
        self.name = name
        self.pid = pid
        self.exe = exe
        self.user = user
        self.cpu = cpu
        self.mem = mem
        self.disk = disk
