from .adapter import open_cdb, save_cdb
import os

class QueryBuilder:

    @staticmethod
    def __where__(clause):
        where = []
        for k in clause:
            if clause[k] == None:
                where.append("%s IS NULL" % (k))
            else:
                where.append("%s = \"%s\"" % (k, clause[k]))
        return ",".join(where)

    @staticmethod
    def __set__(clause):
        st = []
        for k in clause:
            if clause[k] == None:
                st.append("%s = NULL" % (k))
            else:
                st.append("%s = \"%s\"" % (k, clause[k]))
        return ",".join(st)

    @staticmethod
    def __insert__(table, data):
        if isinstance(data, dict):
            columns = []
            values = []
            for column in data:
                columns.append(column)
                values.append("\"%s\"" % data[column])
            sql = "INSERT INTO %s (%s) VALUES (%s)" % (table, ",".join(columns), ",".join(values))
        else:
            count = 0
            columns = []
            bulk = []
            for row in data:
                values = []
                for column in row:
                    if count == 0:
                        columns.append(column)
                    values.append("\"%s\"" % data[column])
                count += 1
                bulk.append("(%s)" % (",".join(values)))
            sql = "INSERT INTO %s (%s) VALUES %s" % (table, ",".join(columns), ",".join(bulk))
        return sql

    @staticmethod
    def __create_table__(table, schema):
        definition = []
        for column in schema:
            definition.append("%s %s" % (column, schema[column]))
        sql = "CREATE TABLE %s (%s)" % (table, ",".join(definition))
        return sql

    @staticmethod
    def __drop_table__(table):
        sql = "DROP TABLE %s" % (table)
        return sql

    def __update__(self, table, data, where):
        sql = "UPDATE %s SET %s" % (table, self.__set__(data))
        if isinstance(where, dict):
            sql += " WHERE %s" % self.__where__(where)
        return sql


    def __select__(self, table, fields, where=None, orderby=None):
        sql = "SELECT %s FROM %s" % (",".join(fields), table)
        if isinstance(where, dict):
            sql += " WHERE %s" % self.__where__(where)
        if isinstance(orderby, str):
            sql += " ORDER BY %s" % (orderby)
        return sql

    def __delete__(self, table, where):
        sql = "DELETE FROM %s WHERE %s" % (table, self.__where__(where))
        return sql

class Model(QueryBuilder):

    def __init__(self, conn, table, schema):
        self.conn = conn
        self.table = table
        self.schema = schema

    def down(self):
        sql = self.__drop_table__(self.table)
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        return cur.rowcount

    def up(self):
        sql = self.__create_table__(self.table, self.schema)
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        return cur.rowcount

    def insert(self, data):
        sql = self.__insert__(self.table, data)
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        return cur.lastrowid

    def update(self, where, data):
        sql = self.__update__(self.table, data, where)
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        return cur.rowcount

    def delete(self, where):
        sql = self.__delete__(self.table, where)
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        return cur.rowcount

    def find(self, where=None):
        sql = self.__select__(self.table, ["*"], where)
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return rows

    def first(self, where):
        sql = self.__select__(self.table, ["*"], where)
        cur = self.conn.cursor()
        cur.execute(sql)
        row = cur.fetchone()
        return row

class ORM:

    __models__ = {}

    def __init__(self, filename, password, salt, schema):

        self.filename = filename
        self.password = password
        self.salt = salt

        install = not os.path.exists(filename)

        self.conn = open_cdb(self.filename, self.password, self.salt)

        for table in schema:
            self.__models__[table] = Model(self.conn, table, schema[table])
            if install:
                self.__models__[table].up()
        if install:
            save_cdb(self.conn, self.filename, self.password, self.salt)

    def model(self, name) -> Model|None:
        if name in self.__models__:
            return self.__models__[name]
        return None

    def save(self):
        save_cdb(self.conn, self.filename, self.password, self.salt)
