"""设置相关业务逻辑服务"""
from app.services.data_service import DataService
from app.repositories.setting_repository import SettingRepository
from app.services.base_service import BaseService
import json

class SettingService(BaseService):
    """设置服务类，封装所有设置相关的业务逻辑"""
    
    @staticmethod
    def get_notification_settings():
        """获取通知设置"""
        return DataService.get_settings().get('notification', {
            'enabled': True,
            'newMessage': True,
            'sound': False,
            'system': True,
            'displayTime': '5秒'
        })
    
    @staticmethod
    def save_notification_settings(data):
        """保存通知设置"""
        # 确保notification设置键存在
        if 'notification' not in DataService.get_settings():
            DataService.get_settings()['notification'] = {
                'enabled': True,
                'newMessage': True,
                'sound': False,
                'system': True,
                'displayTime': '5秒'
            }
        # 合并通知设置
        DataService.get_settings()['notification'].update(data)
        
        # 使用Repository保存设置到数据库
        setting_repo = SettingRepository()
        setting_repo.create_or_update_setting('notification', DataService.get_settings()['notification'])
        
        # 设置脏标记
        DataService.set_dirty_flag('settings')
        
        return DataService.get_settings()['notification']
    
    @staticmethod
    def get_mcp_settings():
        """获取MCP设置"""
        return DataService.get_settings().get('mcp', {
            'enabled': False,
            'server_address': '',
            'server_port': 8080,
            'timeout': 30
        })
    
    @staticmethod
    def save_mcp_settings(data):
        """保存MCP设置"""
        # 确保mcp设置键存在
        if 'mcp' not in DataService.get_settings():
            DataService.get_settings()['mcp'] = {
                'enabled': False,
                'server_address': '',
                'server_port': 8080,
                'timeout': 30
            }
        # 合并MCP设置
        DataService.get_settings()['mcp'].update(data)
        
        # 使用Repository保存设置到数据库
        setting_repo = SettingRepository()
        setting_repo.create_or_update_setting('mcp', DataService.get_settings()['mcp'])
        
        # 设置脏标记
        DataService.set_dirty_flag('settings')
        
        return DataService.get_settings()['mcp']
    
    @staticmethod
    def get_basic_settings():
        """获取基本设置"""
        return DataService.get_settings().get('system', {})
    
    @staticmethod
    def save_basic_settings(data):
        """保存基本设置"""
        # 确保system设置键存在
        if 'system' not in DataService.get_settings():
            DataService.get_settings()['system'] = {}
        # 合并基本设置
        DataService.get_settings()['system'].update(data)
        
        # 使用Repository保存设置到数据库
        setting_repo = SettingRepository()
        setting_repo.create_or_update_setting('system', DataService.get_settings()['system'])
        
        # 设置脏标记
        DataService.set_dirty_flag('settings')
        
        return DataService.get_settings()['system']
    
    @staticmethod
    def get_all_settings():
        """获取所有设置"""
        return DataService.get_settings()
    
    @staticmethod
    def load_settings_from_db():
        """从数据库加载设置到内存"""
        setting_repo = SettingRepository()
        settings = setting_repo.get_all_settings()
        
        for setting in settings:
            key = setting[0]
            value_json = setting[1]
            try:
                # 尝试将JSON字符串转换为字典
                setting_value = json.loads(value_json)
                DataService.get_settings()[key] = setting_value
            except json.JSONDecodeError:
                # 如果不是JSON格式，直接保存为字符串
                DataService.get_settings()[key] = value_json
        
        return DataService.get_settings()
