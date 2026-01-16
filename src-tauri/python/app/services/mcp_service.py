"""MCP工具相关业务逻辑服务"""
from app.services.setting_service import SettingService
from app.services.base_service import BaseService


class MCPService(BaseService):
    """MCP服务类，封装所有MCP相关的业务逻辑"""

    @staticmethod
    def get_mcp_settings():
        """获取MCP设置"""
        return SettingService.get_mcp_settings()

    @staticmethod
    def save_mcp_settings(data):
        """保存MCP设置"""
        return SettingService.save_mcp_settings(data)

    @staticmethod
    def get_notification_settings():
        """获取通知设置"""
        return SettingService.get_notification_settings()

    @staticmethod
    def save_notification_settings(data):
        """保存通知设置"""
        return SettingService.save_notification_settings(data)