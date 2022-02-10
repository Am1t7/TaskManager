import sqlite3

# !!! DB = Database !!!

class DB:

    def __init__(self):
        """
        The builder for DB class
        :param DB_name: The database's name
        :type DB_name: String
        """

        self.DB_name = "ClientDB"

        # The table's name
        self.limits_tbl_name = "limits"
        self.fields = ['cpu', 'mem', 'disk']

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

        self.conn = sqlite3.connect(self.DB_name)
        self.cursor = self.conn.cursor()

        # create the data base with the values
        sql = f"CREATE TABLE IF NOT EXISTS {self.limits_tbl_name} ( field TEXT, value FLOAT)"
        self.cursor.execute(sql)

        for field in self.fields:
            if not self._field_exist(field):
                sql = f"INSERT INTO {self.limits_tbl_name} VALUES ( '{field}', '10000')"
                self.cursor.execute(sql)

        # update the db
        self.conn.commit()

    def _field_exist(self, field):
        '''
        check if the esername is exist if he is return true if not false
        :param username: the username you want to check
        :return:
        '''

        sql = f"SELECT * FROM {self.limits_tbl_name} WHERE field='{field}'"
        self.cursor.execute(sql)

        return not len(self.cursor.fetchall()) == 0

    def update_cpu_value(self, value):
        sql = f"UPDATE {self.limits_tbl_name} SET value = '{value}' WHERE field = 'cpu'"
        self.cursor.execute(sql)
        # update the db
        self.conn.commit()

    def update_mem_value(self, value):
        sql = f"UPDATE {self.limits_tbl_name} SET value = '{value}' WHERE field = 'mem'"
        self.cursor.execute(sql)
        # update the db
        self.conn.commit()

    def update_disk_value(self, value):
        sql = f"UPDATE {self.limits_tbl_name} SET value = '{value}' WHERE field = 'disk'"
        self.cursor.execute(sql)
        # update the db
        self.conn.commit()

    def get_cpu_limits_value(self):
        sql = f"SELECT value FROM {self.limits_tbl_name} WHERE field = 'cpu'"
        self.cursor.execute(sql)
        return self.cursor.fetchone()[0]

    def get_mem_limits_value(self):
        sql = f"SELECT value FROM {self.limits_tbl_name} WHERE field = 'mem'"
        self.cursor.execute(sql)
        return self.cursor.fetchone()[0]

    def get_disk_limits_value(self):
        sql = f"SELECT value FROM {self.limits_tbl_name} WHERE field = 'disk'"
        self.cursor.execute(sql)
        return self.cursor.fetchone()[0]


if __name__ == '__main__':
    myDB = DB()
    myDB.update_cpu_value(50)
    print(myDB.get_cpu_limits_value())
    myDB.update_mem_value(60)
    print(myDB.get_mem_limits_value())
    myDB.update_disk_value(70)
    print(myDB.get_disk_limits_value())