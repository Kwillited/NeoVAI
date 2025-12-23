"""MCP工具相关API路由"""
from flask import Blueprint, request, jsonify

# 导入MCP服务类
from app.services.mcp_service import MCPService

# 创建设置API蓝图（前缀统一为 /api/mcp）
mcp_bp = Blueprint('mcp', __name__, url_prefix='/api/mcp')

# 获取MCP设置
@mcp_bp.route('/mcp', methods=['GET'])
def get_mcp_settings():
    return jsonify(MCPService.get_mcp_settings())

# 保存MCP设置
@mcp_bp.route('/mcp', methods=['POST'])
def save_mcp_settings():
    data = request.json
    settings = MCPService.save_mcp_settings(data)
    return jsonify({
        'message': 'MCP设置已保存',
        'settings': settings
    })