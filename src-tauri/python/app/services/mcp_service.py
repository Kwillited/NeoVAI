"""MCP工具相关业务逻辑服务"""
from app.core.data_manager import db, set_dirty_flag  # 依赖数据管理模块


class MCPService:
    """MCP服务类，封装所有MCP相关的业务逻辑"""

    @staticmethod
    def get_mcp_settings():
        """获取MCP设置"""
        return db['settings']['mcp']

    @staticmethod
    def save_mcp_settings(data):
        """保存MCP设置"""
        # 覆盖MCP设置（确保字段完整，无则用默认值）
        db['settings']['mcp'] = {
            'enabled': data.get('enabled', False),
            'server_address': data.get('server_address', ''),
            'server_port': data.get('server_port', 8080),
            'timeout': data.get('timeout', 30)
        }
        set_dirty_flag('settings')
        return db['settings']['mcp']

    @staticmethod
    def get_notification_settings():
        """获取通知设置"""
        return db['settings']['notification']

    @staticmethod
    def save_notification_settings(data):
        """保存通知设置"""
        # 覆盖通知设置（确保字段完整，无则用默认值）
        db['settings']['notification'] = {
            'enabled': data.get('enabled', True),
            'newMessage': data.get('newMessage', True),
            'sound': data.get('sound', False),
            'system': data.get('system', True),
            'displayTime': data.get('displayTime', '5秒')
        }
        set_dirty_flag('settings')
        return db['settings']['notification']