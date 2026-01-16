"""基础Repository类"""
import sqlite3
from app.core.data_manager import get_db_connection

class BaseRepository:
    """基础Repository类，提供通用的数据访问方法"""
    
    def __init__(self):
        """初始化Repository"""
        self.connection = None
    
    def get_connection(self):
        """获取数据库连接"""
        if not self.connection or self.connection.close():
            self.connection = get_db_connection()
        return self.connection
    
    def execute(self, query, params=None):
        """执行SQL查询（无返回结果）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor.rowcount
    
    def fetch_one(self, query, params=None):
        """执行SQL查询，返回单个结果"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchone()
    
    def fetch_all(self, query, params=None):
        """执行SQL查询，返回所有结果"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
