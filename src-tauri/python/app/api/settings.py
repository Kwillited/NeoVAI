"""系统设置相关API路由"""
from flask import Blueprint, request, jsonify
import json

# 导入相关服务类
from app.services.mcp_service import MCPService
from app.services.rag_service import RAGService
from app.core.data_manager import db, save_data, set_dirty_flag

# 创建设置API蓝图（前缀统一为 /api/settings）
settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')

# 获取通知设置
@settings_bp.route('/notification', methods=['GET'])
def get_notification_settings():
    """获取通知设置"""
    return jsonify(MCPService.get_notification_settings())

# 保存通知设置
@settings_bp.route('/notification', methods=['POST'])
def save_notification_settings():
    """保存通知设置"""
    data = request.json
    settings = MCPService.save_notification_settings(data)
    set_dirty_flag('settings')
    save_data()
    return jsonify({
        'message': '通知设置已保存',
        'settings': settings
    })

# 获取MCP设置
@settings_bp.route('/mcp', methods=['GET'])
def get_mcp_settings():
    """获取MCP设置"""
    return jsonify(MCPService.get_mcp_settings())

# 保存MCP设置
@settings_bp.route('/mcp', methods=['POST'])
def save_mcp_settings():
    """保存MCP设置"""
    data = request.json
    settings = MCPService.save_mcp_settings(data)
    set_dirty_flag('settings')
    save_data()
    return jsonify({
        'message': 'MCP设置已保存',
        'settings': settings
    })

# 获取基本设置
@settings_bp.route('/basic', methods=['GET'])
def get_basic_settings():
    """获取基本设置"""
    return jsonify(db['settings'].get('system', {}))

# 保存基本设置
@settings_bp.route('/basic', methods=['POST'])
def save_basic_settings():
    """保存基本设置"""
    data = request.json
    # 确保system设置键存在
    if 'system' not in db['settings']:
        db['settings']['system'] = {}
    # 合并基本设置
    db['settings']['system'].update(data)
    set_dirty_flag('settings')
    save_data()
    return jsonify({
        'message': '基本设置已保存',
        'settings': db['settings']['system']
    })
