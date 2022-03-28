import psutil
import wx
from client.model import Process
from threading import Thread
from pubsub import pub
from client.clientDB import DB
import uuid
class ProcThread(Thread):
    """
    Gets all the process information we need as psutil isn't very fast
    """

    #----------------------------------------------------------------------
    def __init__(self):
        self.mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)for ele in range(0, 8 * 6, 8)][::-1]).upper()
        """Constructor"""
        Thread.__init__(self)
        self.start() 

    def get_cpu(self,p):
        '''
        get the cpu of the proc
        :param p: the proc
        :return:
        '''
        cpu = p.as_dict(['cpu_times'])
        cpu_percent = cpu['cpu_times'].user
        return cpu_percent/100.0

    def get_disk(self,p):
        '''
        get the disk usage of the proc
        :param p: the process
        :return:
        '''
        io_counters = p.io_counters()
        disk_usage_process = io_counters[2] + io_counters[3]  # read_bytes + write_bytes
        disk_io_counter = psutil.disk_io_counters()
        disk_total = disk_io_counter[2] + disk_io_counter[3]  # read_bytes + write_bytes
        return disk_usage_process / disk_total * 100

    def run(self):
        '''
        main thread
        :return:
        '''
        procs = []
        bad_procs = []
        cpu_percent = 0
        mem_percent = 0
        disk_percent = 0
        count = 0
        db = DB()
        # get the processes
        for proc in psutil.process_iter():
            try:
                p = psutil.Process(proc.pid)
                cpu = self.get_cpu(p)
                mem = p.memory_info().vms / (1024 * 1024)
                disk = self.get_disk(p)
                new_proc = Process(p.name(),
                                   str(p.pid),
                                   p.exe(),
                                   p.username(),
                                   str(cpu),
                                   str(mem),
                                   str(disk)
                                   )
                procs.append(new_proc)
                #check limits
                if cpu > float(db.get_cpu_limits_value()):
                    bad_procs.append(procs.index(new_proc))
                if mem > float(db.get_mem_limits_value()):
                    bad_procs.append(procs.index(new_proc))
                if disk > float(db.get_disk_limits_value()):
                    bad_procs.append(procs.index(new_proc))

                #update the sum of the cpu,memory,disk usage
                cpu_percent += cpu
                mem_percent += mem
                disk_percent += disk
                count += 1

            except Exception as e:
                pass
        #check if banned proc has been open
        for s in db.get_soft_value(self.mac):
            for p in procs:
                if str(s[1]) == p.name and str(s[1]):
                    wx.CallAfter(pub.sendMessage, 'open_ban', name=p.name, procs=procs)
                    break





        # send pids to GUI
        wx.CallAfter(pub.sendMessage,'update',procs=procs, bad_procs=bad_procs)
        
        number_of_procs = len(procs)
        wx.CallAfter(pub.sendMessage, 'update_status',procsnum=number_of_procs, totalcpu=cpu_percent, totalmem=mem_percent, totaldisk=disk_percent)



        
            
