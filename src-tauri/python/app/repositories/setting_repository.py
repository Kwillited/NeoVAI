"""设置数据访问类"""
from app.repositories.base_repository import BaseRepository
from app.models.models import Setting
import json

class SettingRepository(BaseRepository):
    """设置数据访问类，处理设置相关的数据访问"""
    
    def get_all_settings(self):
        """获取所有设置"""
        return self.db.query(Setting).all()
    
    def get_setting_by_key(self, key):
        """根据键获取设置"""
        return self.db.query(Setting).filter(Setting.key == key).first()
    
    def create_or_update_setting(self, key, value):
        """创建或更新设置"""
        # 将设置值转换为JSON字符串
        value_json = json.dumps(value)
        
        # 查找是否已存在该设置
        existing_setting = self.get_setting_by_key(key)
        if existing_setting:
            # 更新现有设置
            existing_setting.value = value_json
            return self.update(existing_setting)
        else:
            # 创建新设置
            new_setting = Setting(key=key, value=value_json)
            return self.add(new_setting)
    
    def delete_setting(self, key):
        """根据键删除设置"""
        setting = self.get_setting_by_key(key)
        if setting:
            self.delete(setting)
            return True
        return False
    
    def delete_all_settings(self):
        """删除所有设置"""
        result = self.db.query(Setting).delete()
        self.db.commit()
        return result
