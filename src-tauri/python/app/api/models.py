"""模型相关API路由"""
from flask import Blueprint, request, jsonify, current_app, send_from_directory
import os

# 导入模型服务层
from app.services.model_service import ModelService

# 创建模型API蓝图（前缀统一为 /api/models）
model_bp = Blueprint('model', __name__, url_prefix='/api/models')

# 获取图标目录的绝对路径
ICONS_DIR = 'C:\\Users\\admin\\AppData\\Local\\NeoVAI\\NeoVAI\\icon'

# 获取所有模型供应商以及模型版本
@model_bp.route('', methods=['GET'])
def get_models():
    models = ModelService.get_all_models()
    return jsonify({'models': models})

# 获取模型供应商图标
@model_bp.route('/icons/<filename>', methods=['GET'])
def get_model_icon(filename):
    """
    提供模型供应商图标文件下载功能
    参数: filename - 图标文件名，如 'OpenAI.png'
    """
    try:
        # 从数据库获取图片
        from app.core.data_manager import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 提取模型名称（去掉文件扩展名）
        model_name = filename.replace('.png', '')
        
        # 查询数据库中的图标
        cursor.execute("SELECT icon_blob FROM models WHERE name = ?", (model_name,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            # 从数据库返回图片
            from flask import current_app
            return current_app.response_class(result[0], mimetype='image/png')
        else:
            # 从文件系统返回图片（向后兼容）
            return send_from_directory(ICONS_DIR, filename)
    except FileNotFoundError:
        # 如果图标文件不存在，返回404错误
        return jsonify({'error': '图标文件不存在'}), 404
    except Exception as e:
        # 处理其他可能的错误
        return jsonify({'error': str(e)}), 500

# 配置特定模型（按名称）
@model_bp.route('/<model_name>', methods=['POST'])
def configure_model(model_name):
    data = request.json
    success, message, model = ModelService.configure_model(model_name, data)
    
    if not success:
        return jsonify({'error': message}), 404
    
    return jsonify({
        'message': message,
        'model': model
    })

# 删除特定模型配置（按名称）
@model_bp.route('/<model_name>', methods=['DELETE'])
def delete_model(model_name):
    success, message = ModelService.delete_model(model_name)
    
    if not success:
        return jsonify({'error': message}), 404
    
    return jsonify({'message': message})

# 更新模型启用状态
@model_bp.route('/<model_name>/enabled', methods=['POST'])
def update_model_enabled(model_name):
    data = request.json
    enabled = data.get('enabled', True)
    
    success, message = ModelService.update_model_enabled(model_name, enabled)
    
    if not success:
        return jsonify({'error': message}), 404
    
    return jsonify({
        'message': message,
        'enabled': enabled
    })

# 删除特定模型的特定版本
@model_bp.route('/<model_name>/versions/<version_name>', methods=['DELETE'])
def delete_version(model_name, version_name):
    success, message, model = ModelService.delete_version(model_name, version_name)
    
    if not success:
        if message == '模型不存在':
            return jsonify({'error': message}), 404
        elif message == '该模型没有版本信息' or message == '版本不存在':
            return jsonify({'error': message}), 400
        else:
            return jsonify({'error': message}), 400
    
    return jsonify({
        'message': message,
        'model': model
    })

# 辅助函数：从模型的versions数组中获取特定版本的配置信息
def get_version_config(model, version_name):
    return ModelService.get_version_config(model, version_name)
