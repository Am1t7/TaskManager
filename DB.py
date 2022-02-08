import sqlite3

# !!! DB = Database !!!

class DB:

    def __init__(self):
        """
        The builder for DB class
        :param DB_name: The database's name
        :type DB_name: String
        """

        self.DB_name = "AmitDB"

        # The table's name
        self.users_tbl_name = "users"
        self.limits_tbl_name = "limits"
        self.ban_procs_tbl_name = "Ban_procs"

        # The pointer to the DB
        self.conn = None

        # The pointer to the DB's cursor
        self.cursor = None

        # Creating the DB
        self.createDB()

    def createDB(self):
        """
        The function create the data base with the values
        :return:
        """

        self.conn = sqlite3.connect(self.DB_name)
        self.cursor = self.conn.cursor()

        # create the data base with the values
        sql = f"CREATE TABLE IF NOT EXISTS {self.limits_tbl_name} (mac TEXT, cpu FLOAT, mem FLOAT, disk FLOAT)"
        self.cursor.execute(sql)

        # update the db
        self.conn.commit()

    def mac_exist(self, mac):
        '''
        check if the esername is exist if he is return true if not false
        :param username: the username you want to check
        :return:
        '''

        sql = f"SELECT mac FROM {self.limits_tbl_name} WHERE mac='{mac}'"
        self.cursor.execute(sql)

        return not len(self.cursor.fetchall()) == 0

    def add_limits(self, mac, cpu, mem, disk):
        '''
        add a user to the db
        :param username: the username of the user
        :param password: the password of the user
        :return: true if the user was added or false if not
        '''

        retValue = False

        if not self.mac_exist(mac):

            retValue = True
            sql = f"INSERT INTO {self.limits_tbl_name} VALUES ('{mac}', '{cpu}', '{mem}', '{disk}')"
            self.cursor.execute(sql)
            # update the db
            self.conn.commit()

        return retValue
    def delete_limits(self,mac):
        '''
        delete a user details from the db
        :param username: the username of the user you want to delete
        :return:
        '''
        sql = f"DELETE FROM {self.limits_tbl_name} WHERE mac = '{mac}'"
        self.cursor.execute(sql)
        # update the db
        self.conn.commit()
    def update_limits_details(self, value_to_update, change):
        '''
        update the user details
        :param value_to_update: the detail you wont to update
        :param change: what to change this detail to
        :param before: what there was bedore the change
        :return:
        '''
        sql = f"UPDATE {self.limits_tbl_name} SET {value_to_update} = '{change}'"
        self.cursor.execute(sql)
        # update the db
        self.conn.commit()
    def get_limits_value(self, type, mac):
        sql = f"SELECT {type} FROM {self.limits_tbl_name} WHERE mac = '{mac}'"
        self.cursor.execute(sql)
        return self.cursor.fetchone()[0]