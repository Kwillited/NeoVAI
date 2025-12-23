"""对话相关API路由"""
from flask import Blueprint, request, jsonify, Response
from app.services.chat_service import ChatService  # 导入对话服务类

# 创建对话API蓝图（前缀统一为 /api/chats）
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chats')

# 获取所有对话
@chat_bp.route('', methods=['GET'])
def get_chats():
    chats = ChatService.get_chats()
    return jsonify({'chats': chats})

# 创建新对话
@chat_bp.route('', methods=['POST'])
def create_chat():
    data = request.json
    title = data.get('title')
    new_chat = ChatService.create_chat(title)
    return jsonify({'chat': new_chat}), 201  # 201 = 创建成功

# 获取单个对话记录（按ID）
@chat_bp.route('/<chat_id>', methods=['GET'])
def get_chat(chat_id):
    # 使用服务层获取对话
    chat = ChatService.get_chat(chat_id)
    if not chat:
        return jsonify({'error': '对话不存在'}), 404  # 404 = 资源不存在
    
    return jsonify({'chat': chat})

# 删除单个对话记录（按ID）
@chat_bp.route('/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    # 使用服务层删除对话
    success = ChatService.delete_chat(chat_id)
    if not success:
        return jsonify({'error': '对话不存在'}), 404  # 404 = 资源不存在
    
    return jsonify({'success': True, 'message': '对话已删除'})

# 删除所有对话记录
@chat_bp.route('/delete-all', methods=['DELETE'])
def delete_all_chats():
    # 使用服务层删除所有对话
    ChatService.delete_all_chats()
    return jsonify({'success': True, 'message': '所有对话已删除'})

# 发送消息（应用层）
@chat_bp.route('/<chat_id>/messages', methods=['POST'])
def send_message(chat_id):
    data = request.json
    
    # 使用服务层处理消息发送，直接传递整个request.json对象
    result = ChatService.send_message(chat_id, data)
    
    # 从请求数据中获取stream参数
    stream = data.get('stream', False)
    
    # 根据stream参数处理响应
    if stream:
        # 流式响应返回生成器函数
        return Response(result(), content_type='text/event-stream')
    else:
        # 普通响应返回json和状态码
        response_data, status_code = result
        return jsonify(response_data), status_code