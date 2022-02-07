class Limits():
    def __init__(self):
        self.cpu_limit = 1000.0
        self.mem_limit = 1000.0
        self.disk_limit = 5.0

    def update_limits(self, cpu, mem, disk):
        self.cpu_limit = cpu
        self.mem_limit = mem
        self.disk_limit = disk

    def get_cpu_limit(self):
        return self.cpu_limit

    def get_mem_limit(self):
        return self.mem_limit

    def get_disk_limit(self):
        return self.disk_limit
