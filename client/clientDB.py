import sqlite3

#  !!! DB = Database !!!

class DB:
    '''
    the client database
    '''

    def __init__(self):
        """
        The builder for DB class
        """

        self.DB_name = "ClientDB"

        # The limit table name
        self.limits_tbl_name = "limits"
        self.fields = ['cpu', 'mem', 'disk']
        # the ban procs table name
        self.ban_procs_tbl_name = "Ban_procs"

        # The pointer to the DB
        self.conn = None

        # The pointer to the DB's cursor
        self.cursor = None

        # Creating the DB
        self._createDB()

    def _createDB(self):
        """
        The function create both data bases with the values
        :return:
        """
        # connecting
        self.conn = sqlite3.connect(self.DB_name)
        self.cursor = self.conn.cursor()

        # create the data base with the values
        sql = f"CREATE TABLE IF NOT EXISTS {self.limits_tbl_name} ( field TEXT, value FLOAT)"
        self.cursor.execute(sql)
        sql = f"CREATE TABLE IF NOT EXISTS {self.ban_procs_tbl_name} ( mac TEXT, software TEXT)"
        self.cursor.execute(sql)
        # insert values to the fields
        for field in self.fields:
            if not self._field_exist(field):
                sql = f"INSERT INTO {self.limits_tbl_name} VALUES ( '{field}', '10000')"
                self.cursor.execute(sql)

        #  update the db
        self.conn.commit()

    def _field_exist(self, field):
        '''
        check if the field is exist if he is return true if not false
        :param field: the field you want to check
        :return:
        '''

        sql = f"SELECT * FROM {self.limits_tbl_name} WHERE field='{field}'"
        self.cursor.execute(sql)

        return not len(self.cursor.fetchall()) == 0

    def update_cpu_value(self, value):
        '''
        updating the cpu value
        :param value: the value to update to
        :return:
        '''
        sql = f"UPDATE {self.limits_tbl_name} SET value = '{value}' WHERE field = 'cpu'"
        self.cursor.execute(sql)
        #  update the db
        self.conn.commit()

    def update_mem_value(self, value):
        '''
        updating the memory value
        :param value: the value to update to
        :return:
        '''
        sql = f"UPDATE {self.limits_tbl_name} SET value = '{value}' WHERE field = 'mem'"
        self.cursor.execute(sql)
        #  update the db
        self.conn.commit()

    def update_disk_value(self, value):
        '''
        updating the disk value
        :param value: the value to update to
        :return:
        '''
        sql = f"UPDATE {self.limits_tbl_name} SET value = '{value}' WHERE field = 'disk'"
        self.cursor.execute(sql)
        #  update the db
        self.conn.commit()

    def get_cpu_limits_value(self):
        '''
        get the cpu value
        :return:
        '''
        sql = f"SELECT value FROM {self.limits_tbl_name} WHERE field = 'cpu'"
        self.cursor.execute(sql)
        return self.cursor.fetchone()[0]

    def get_mem_limits_value(self):
        '''
        get the memory value
        :return:
        '''
        sql = f"SELECT value FROM {self.limits_tbl_name} WHERE field = 'mem'"
        self.cursor.execute(sql)
        return self.cursor.fetchone()[0]

    def get_disk_limits_value(self):
        '''
        get the disk value
        :return:
        '''
        sql = f"SELECT value FROM {self.limits_tbl_name} WHERE field = 'disk'"
        self.cursor.execute(sql)
        return self.cursor.fetchone()[0]


# ------------------------------------------------------------------------ Ban Procs ------------------------------------------------------------

    def mac_soft_exist(self, mac, soft):
        '''
        check if the mac and the software are exists
        :param mac: the mac address
        :param soft: the software name
        :return: true if they exist and false if not
        '''
        sql = f"SELECT mac,software FROM {self.ban_procs_tbl_name} WHERE mac='{mac}' AND software='{soft}'"
        self.cursor.execute(sql)

        return not len(self.cursor.fetchall()) == 0

    def add_ban(self, mac, soft):
        '''
        adding a banned software
        :param mac: the mac address
        :param soft: the software name
        :return: return true if add or false if not
        '''
        retValue = False

        if not self.mac_soft_exist(mac, soft):

            retValue = True
            sql = f"INSERT INTO {self.ban_procs_tbl_name} VALUES ('{mac}', '{soft}')"
            self.cursor.execute(sql)
            #  update the db
            self.conn.commit()

        return retValue

    def delete_ban_proc(self,mac,name):
        '''
        delete ban software details from the db
        :param username: the username of the user you want to delete
        :return:
        '''
        sql = f"DELETE FROM {self.ban_procs_tbl_name} WHERE mac = '{mac}' AND software = '{name}'"
        self.cursor.execute(sql)
        #  update the db
        self.conn.commit()

    def get_soft_value(self, mac):
        '''
        get the software value
        :param mac: the mac address
        :return:
        '''
        sql = f"SELECT * FROM {self.ban_procs_tbl_name} WHERE mac = '{mac}'"
        self.cursor.execute(sql)
        return self.cursor.fetchall()