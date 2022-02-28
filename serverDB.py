import sqlite3

# !!! DB = Database !!!

class DB:

    def __init__(self):
        """
        The builder for DB class
        :param DB_name: The database's name
        :type DB_name: String
        """

        self.DB_name = "ServerDB"

        # The table's name
        self.users_tbl_name = "users"
        self.limits_tbl_name = "limits"
        self.ban_procs_tbl_name = "Ban_procs"

        # The pointer to the DB
        self.conn = None

        # The pointer to the DB's cursor
        self.cursor = None

        # Creating the DB
        self._createDB()

    def _createDB(self):
        """
        The function create the data base with the values
        :return:
        """

        self.conn = sqlite3.connect(self.DB_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

        # create the data base with the values
        sql = f"CREATE TABLE IF NOT EXISTS {self.users_tbl_name} ( username TEXT, password TEXT)"
        self.cursor.execute(sql)
        sql = f"CREATE TABLE IF NOT EXISTS {self.limits_tbl_name} ( mac TEXT, CPU FLOAT, Memory FLOAT, Disk FLOAT)"
        self.cursor.execute(sql)
        sql = f"CREATE TABLE IF NOT EXISTS {self.ban_procs_tbl_name} ( mac TEXT, software TEXT)"
        self.cursor.execute(sql)

        self.conn.commit()

#---------------------------------------------------------------- users----------------------------------------------------

    def username_exist(self, username):
        '''
        check if the esername is exist if he is return true if not false
        :param username: the username you want to check
        :return:
        '''

        sql = f"SELECT username FROM {self.users_tbl_name} WHERE username='{username}'"
        self.cursor.execute(sql)

        return not len(self.cursor.fetchall()) == 0

    def pass_exist(self,password):
        sql = f"SELECT password FROM {self.users_tbl_name} WHERE password='{password}'"
        self.cursor.execute(sql)

        return not len(self.cursor.fetchall()) == 0


    def add_user(self, username, password):
        '''
        add a user to the db
        :param username: the username of the user
        :param password: the password of the user
        :return: true if the user was added or false if not
        '''

        retValue = False

        if not self.username_exist(username):

            retValue = True
            sql = f"INSERT INTO {self.users_tbl_name} VALUES ('{username}', '{password}')"
            self.cursor.execute(sql)
            # update the db
            self.conn.commit()

        return retValue


    def delete_user(self,username):
        '''
        delete a user details from the db
        :param username: the username of the user you want to delete
        :return:
        '''
        sql = f"DELETE FROM {self.users_tbl_name} WHERE username = '{username}'"
        self.cursor.execute(sql)
        # update the db
        self.conn.commit()


    def update_user_details(self, value_to_update, change):
        '''
        update the user details
        :param value_to_update: the detail you wont to update
        :param change: what to change this detail to
        :param before: what there was bedore the change
        :return:
        '''
        sql = f"UPDATE {self.users_tbl_name} SET {value_to_update} = '{change}'"
        self.cursor.execute(sql)
        # update the db
        self.conn.commit()


#---------------------------------------------------------------- limits ----------------------------------------------

    def mac_exist(self, mac):
        sql = f"SELECT mac FROM {self.limits_tbl_name} WHERE mac='{mac}'"
        self.cursor.execute(sql)

        return not len(self.cursor.fetchall()) == 0

    def pc_limit_add(self, mac, cpu, mem, disk):
        retValue = False

        if not self.mac_exist(mac):

            retValue = True
            sql = f"INSERT INTO {self.limits_tbl_name} VALUES ('{mac}', '{cpu}', '{mem}', '{disk}')"
            self.cursor.execute(sql)
            # update the db
            self.conn.commit()

        return retValue

    def update_cpu_value(self, value):
        sql = f"UPDATE {self.limits_tbl_name} SET CPU = '{value}'"
        self.cursor.execute(sql)
        # update the db
        self.conn.commit()

    def update_mem_value(self, value):
        sql = f"UPDATE {self.limits_tbl_name} SET Memory = '{value}' "
        self.cursor.execute(sql)
        # update the db
        self.conn.commit()

    def update_disk_value(self, value):
        sql = f"UPDATE {self.limits_tbl_name} SET Disk = '{value}'"
        self.cursor.execute(sql)
        # update the db
        self.conn.commit()

    def get_cpu_limits_value(self, mac):
        sql = f"SELECT CPU FROM {self.limits_tbl_name} WHERE mac = '{mac}'"
        self.cursor.execute(sql)
        return self.cursor.fetchone()[0]

    def get_mem_limits_value(self, mac):
        sql = f"SELECT Memory FROM {self.limits_tbl_name} WHERE mac = '{mac}'"
        self.cursor.execute(sql)
        return self.cursor.fetchone()[0]

    def get_disk_limits_value(self, mac):
        sql = f"SELECT Disk FROM {self.limits_tbl_name} WHERE mac = '{mac}'"
        self.cursor.execute(sql)
        return self.cursor.fetchone()[0]



#------------------------------------------------------------------------ Ban Procs -------------------------------------------------------------

    def mac_soft_exist(self, mac, soft):
        sql = f"SELECT mac,software FROM {self.ban_procs_tbl_name} WHERE mac='{mac}' AND software='{soft}'"
        self.cursor.execute(sql)

        return not len(self.cursor.fetchall()) == 0

    def add_ban(self, mac, soft):
        retValue = False

        if not self.mac_soft_exist(mac, soft):

            retValue = True
            sql = f"INSERT INTO {self.limits_tbl_name} VALUES ('{mac}', '{soft}')"
            self.cursor.execute(sql)
            # update the db
            self.conn.commit()

        return retValue




if __name__ == '__main__':
    db = DB()
    db._createDB()
    db.add_user("amit","12345")

