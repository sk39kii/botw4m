# -*- coding: utf-8 -*-

import os
import sqlite3

class DatabaseUtil(object):
    u"""DB操作ユーティリティ
    """
    def __init__(self, db=None):
        u"""DB接続しコネクションを保持
        """
        self.conn = None
        self.databasefile = db
        try:
            self.conn = self.getConnectionDB(self.databasefile)
        except Exception as e:
            print("Error: " + str(e))

    def getConnectionDB(self, databasefile):
        u"""DBコネクションの取得(DB指定)
        """
        conn = None
        try:
            if not databasefile is None:
                db_path = os.path.join(os.path.dirname(__file__), databasefile)
                conn = sqlite3.connect(db_path)
        except Exception as e:
            print("Error: " + str(e))
        return conn

    def getConnection(self):
        u"""DBコネクションの取得(保持コネクション)
        """
        return self.checkConnection()

    def checkConnection(self):
        u"""テーブル重複チェック
        """
        if self.conn is None:
            return self.getConnectionDB(self.databasefile)
        else:
            return self.conn

    def checkDuplicate(self, tablename):
        u"""テーブル重複チェック(保持コネクション)
        """
        return self._checkDuplicate(self.checkConnection(), tablename)

    def _checkDuplicate(self, conn, tablename):
        u"""テーブル重複チェック(コネクション指定)
        """
        try:
            sql = "SELECT name FROM sqlite_master"
            if tablename in [v[0] for v in self.execute(sql)]:
                return True
            else:
                return False
        except Exception as e:
            print("Error: " + str(e))

    def execute(self, query, dic=None):
        u"""クエリ実行(保持コネクション)
        """
        return self._execute(self.checkConnection(), query, dic)

    def _execute(self, conn, query, dic):
        u"""クエリ実行(コネクション指定)
        """
        result = None
        try:
            cur = conn.cursor()
            if dic is None:
                cur.execute(query)
            else:
                cur.execute(query, dic)
            result = cur.fetchall()
            conn.commit()
        except Exception as e:
            print("Error: " + str(e))
        return result

    def execute_once(self, databasefile, query):
        u"""クエリ実行(db open > query execute > db Close)
        """
        try:
            conn = self.getConnectionDB(databasefile)
            cur = conn.cursor()
            cur.execute(query)
            result = cur.fetchall()
            conn.commit()
        except Exception as e:
            print("Error: " + str(e))
        finally:
            self._closeConnection(conn)
        return result

    def close(self):
        u"""コネクションクローズ(保持コネクション)
        """
        self._closeConnection(self.conn)

    def _closeConnection(self, conn):
        u"""コネクションクローズ(コネクション指定)
        ※no check isinstance
        """
        if not conn is None:
            conn.close()

    def list_tables(self):
        u"""テーブル一覧
        """
        sql = "SELECT name FROM sqlite_master WHERE type='table'"
        for tbl in [v[0] for v in self.execute(sql)]:
            print(tbl)

    def list_tablesDB(self, db):
        u"""テーブル一覧(DB指定)
        """
        sql = "SELECT name FROM sqlite_master WHERE type='table'"
        for tbl in [v[0] for v in self.execute_once(db, sql)]:
            print(tbl)
