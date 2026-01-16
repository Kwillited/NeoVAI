"""设置数据访问类"""
from app.repositories.base_repository import BaseRepository
import json

class SettingRepository(BaseRepository):
    """设置数据访问类，处理设置相关的数据访问"""
    
    def get_all_settings(self):
        """获取所有设置"""
        query = "SELECT * FROM settings"
        return self.fetch_all(query)
    
    def get_setting_by_key(self, key):
        """根据键获取设置"""
        query = "SELECT * FROM settings WHERE key = ?"
        return self.fetch_one(query, (key,))
    
    def create_or_update_setting(self, key, value):
        """创建或更新设置"""
        # 将设置值转换为JSON字符串
        value_json = json.dumps(value)
        query = '''
        INSERT OR REPLACE INTO settings (key, value)
        VALUES (?, ?)
        '''
        return self.execute(query, (key, value_json))
    
    def delete_setting(self, key):
        """根据键删除设置"""
        query = "DELETE FROM settings WHERE key = ?"
        return self.execute(query, (key,))
    
    def delete_all_settings(self):
        """删除所有设置"""
        query = "DELETE FROM settings"
        return self.execute(query)
