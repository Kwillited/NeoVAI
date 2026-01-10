"""对话相关业务逻辑服务"""
import sys
import uuid
import json
from datetime import datetime
from app.core.data_manager import db, save_data, get_db_connection  # 依赖数据管理模块
from app.models.model_manager import ModelManager  # 导入模型管理器
from app.services.base_service import BaseService

class ChatService(BaseService):
    """对话服务类，封装所有对话相关的业务逻辑"""

    @staticmethod
    def get_chats():
        """获取所有对话"""
        try:
            # 获取数据库连接
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 先从数据库加载最新数据
            cursor.execute("SELECT * FROM chats ORDER BY updated_at DESC")
            chats = cursor.fetchall()
            
            chat_list = []
            for chat_row in chats:
                # 处理可能的字段缺失情况
                chat_id = chat_row[0]
                title = chat_row[1] if len(chat_row) > 1 else '未命名对话'
                preview = chat_row[2] if len(chat_row) > 2 else ''
                created_at = chat_row[3] if len(chat_row) > 3 else datetime.now().isoformat()
                updated_at = chat_row[4] if len(chat_row) > 4 else datetime.now().isoformat()
                
                # 获取对话的所有消息
                cursor.execute("SELECT * FROM messages WHERE chat_id = ? ORDER BY created_at", (chat_id,))
                messages = cursor.fetchall()
                
                # 构建消息列表
                message_list = []
                for msg_row in messages:
                    msg_id = msg_row[0]
                    role = msg_row[2] if len(msg_row) > 2 else 'user'
                    content = msg_row[3] if len(msg_row) > 3 else ''
                    msg_created_at = msg_row[4] if len(msg_row) > 4 else datetime.now().isoformat()
                    model = msg_row[5] if len(msg_row) > 5 else None
                    
                    message_list.append({
                        'id': msg_id,
                        'role': role,
                        'content': content,
                        'createdAt': msg_created_at,
                        'model': model
                    })
                
                # 添加对话到列表
                chat_list.append({
                    'id': chat_id,
                    'title': title,
                    'preview': preview,
                    'createdAt': created_at,
                    'updatedAt': updated_at,
                    'messages': message_list
                })
            
            # 关闭数据库连接
            conn.close()
            
            # 更新内存数据库
            db['chats'] = chat_list
            return chat_list
        except Exception as e:
            print(f"❌ 获取对话列表失败: {str(e)}")
            # 失败时返回内存数据库中的对话
            return db['chats']

    @staticmethod
    def create_chat(title=None):
        """创建新对话"""
        try:
            # 获取数据库连接
            conn = get_db_connection()
            cursor = conn.cursor()
            
            chat_id = str(uuid.uuid4())  # 生成唯一对话ID
            now = datetime.now().isoformat()  # 时间戳（ISO格式）
            
            title = title or '新对话'
            
            # 直接插入到SQLite数据库
            cursor.execute('''
            INSERT INTO chats (id, title, preview, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ''', (chat_id, title, '', now, now))
            conn.commit()
            conn.close()
            
            # 创建对话对象
            new_chat = {
                'id': chat_id,
                'title': title,
                'preview': '',
                'createdAt': now,
                'updatedAt': now,
                'messages': []
            }
            
            # 更新内存数据库
            db['chats'].insert(0, new_chat)  # 新增对话放列表开头（最新优先）
            
            return new_chat
        except Exception as e:
            print(f"❌ 创建对话失败: {str(e)}")
            # 回退到内存操作
            chat_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            title = title or '新对话'
            new_chat = {
                'id': chat_id,
                'title': title,
                'preview': '',
                'createdAt': now,
                'updatedAt': now,
                'messages': []
            }
            db['chats'].insert(0, new_chat)
            save_data()
            return new_chat

    @staticmethod
    def get_chat(chat_id):
        """获取单个对话记录（按ID）"""
        # 先尝试从内存获取
        chat = next((c for c in db['chats'] if c['id'] == chat_id), None)
        if chat:
            return chat
        
        try:
            # 获取数据库连接
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 从数据库获取
            cursor.execute("SELECT * FROM chats WHERE id = ?", (chat_id,))
            chat_row = cursor.fetchone()
            if not chat_row:
                conn.close()
                return None
            
            # 处理可能的字段缺失情况
            chat_id = chat_row[0]
            title = chat_row[1] if len(chat_row) > 1 else '未命名对话'
            preview = chat_row[2] if len(chat_row) > 2 else ''
            created_at = chat_row[3] if len(chat_row) > 3 else datetime.now().isoformat()
            updated_at = chat_row[4] if len(chat_row) > 4 else datetime.now().isoformat()
            
            # 获取对话的所有消息
            cursor.execute("SELECT * FROM messages WHERE chat_id = ? ORDER BY created_at", (chat_id,))
            messages = cursor.fetchall()
            
            # 构建消息列表
            message_list = []
            for msg_row in messages:
                msg_id = msg_row[0]
                role = msg_row[2] if len(msg_row) > 2 else 'user'
                content = msg_row[3] if len(msg_row) > 3 else ''
                msg_created_at = msg_row[4] if len(msg_row) > 4 else datetime.now().isoformat()
                
                message_list.append({
                    'id': msg_id,
                    'role': role,
                    'content': content,
                    'createdAt': msg_created_at
                })
            
            # 关闭数据库连接
            conn.close()
            
            # 构建对话对象
            chat = {
                'id': chat_id,
                'title': title,
                'preview': preview,
                'createdAt': created_at,
                'updatedAt': updated_at,
                'messages': message_list
            }
            
            # 更新内存数据库
            db['chats'].append(chat)
            return chat
        except Exception as e:
            print(f"❌ 获取对话失败: {str(e)}")
            return None

    @staticmethod
    def delete_chat(chat_id):
        """删除单个对话记录（按ID）"""
        try:
            # 获取数据库连接
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 从数据库中删除对话（级联删除消息）
            cursor.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
            conn.commit()
            conn.close()
            
            # 更新内存数据库
            chat_index = next((i for i, c in enumerate(db['chats']) if c['id'] == chat_id), None)
            if chat_index is not None:
                db['chats'].pop(chat_index)
            
            return True
        except Exception as e:
            print(f"❌ 删除对话失败: {str(e)}")
            # 尝试从内存中删除
            chat_index = next((i for i, c in enumerate(db['chats']) if c['id'] == chat_id), None)
            if chat_index is not None:
                db['chats'].pop(chat_index)
                return True
            return False

    @staticmethod
    def delete_all_chats():
        """删除所有对话记录"""
        try:
            # 获取数据库连接
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 从数据库中删除所有对话和消息
            cursor.execute("DELETE FROM messages")
            cursor.execute("DELETE FROM chats")
            conn.commit()
            conn.close()
            
            # 清空内存中的对话数据
            db['chats'] = []
            return True
        except Exception as e:
            print(f"❌ 删除所有对话失败: {str(e)}")
            # 尝试清空内存
            db['chats'] = []
            return True
    
    @staticmethod
    def get_chat_context(chat_id, max_messages=10):
        """
        获取对话上下文历史
        
        参数:
            chat_id: 对话ID
            max_messages: 最大获取的消息数量，默认10条
            
        返回:
            格式化的上下文消息列表，或者None（如果对话不存在）
        """
        # 查找匹配ID的对话
        chat = ChatService.get_chat(chat_id)
        if not chat:
            return None
        
        # 获取对话历史消息
        messages = chat.get('messages', [])
        
        # 如果消息数量超过max_messages，只保留最近的max_messages条
        if len(messages) > max_messages:
            messages = messages[-max_messages:]
        
        # 转换为适合模型输入的格式
        formatted_messages = []
        for msg in messages:
            # 确保消息有必要的字段
            if 'role' in msg and 'content' in msg:
                # 原始内容
                original_content = msg['content']
                # 剔除content中的think标签内容
                content = original_content
                
                # 定义可能的think标签格式
                think_tag_pairs = [
                    ('<think>', '</think>'),  # 尖括号格式
                    ('[think]', '[/think]'),  # 方括号格式
                ]
                
                # 对每种标签格式进行过滤
                for opening_tag, closing_tag in think_tag_pairs:
                    while opening_tag in content:
                        start = content.find(opening_tag)
                        if start != -1:
                            # 从start + len(opening_tag)的位置开始查找结束标签
                            end = content.find(closing_tag, start + len(opening_tag))
                            if end != -1:
                                # 保留开始标签前的内容和结束标签后的内容
                                content = content[:start] + content[end + len(closing_tag):]
                            else:
                                break
                
                # 去除多余的空白字符
                content = content.strip()
                
                formatted_messages.append({
                    'role': msg['role'],
                    'content': content
                })
        
        return formatted_messages

    @staticmethod
    def get_rag_enhanced_prompt(question, rag_config=None):
        """RAG增强提示"""
        # 如果提供了rag_config参数，使用它，否则从数据库设置中获取
        if rag_config and isinstance(rag_config, dict):
            rag_settings = rag_config
        else:
            rag_settings = db['settings'].get('rag', {})
        
        if not rag_settings.get('enabled', False):
            return question
        try:
            # 使用VectorStoreService
            from app.services.vector_store_service import VectorStoreService
            vector_service = VectorStoreService.get_instance()
            if vector_service:
                # 获取RAG设置，处理前端可能使用的不同键名
                # 将前端的topK映射到后端的top_k
                top_k = rag_settings.get('topK', rag_settings.get('top_k', 3))
                score_threshold = rag_settings.get('score_threshold', 0.7)
                
                # 执行向量搜索
                result = vector_service.search_documents(question, k=top_k, score_threshold=score_threshold)
                
                # 构造增强提示
                if result:
                    context = "\n".join([f"参考文档{i+1}：{doc.page_content[:200]}..." 
                                        for i, doc in enumerate(result)])
                    if context:
                        return f"参考文档：{context}\n问题：{question}"
                return question
            print("VectorStoreService实例未初始化，跳过RAG增强")
            return question
        except Exception as e:
            print(f"RAG调用失败: {str(e)}")
            # 确保即使RAG失败，原始问题也能正常返回
            return question

    @staticmethod
    def parse_model_info(model_name):
        """
        解析前端发送的模型格式 "Ollama-qwen3:0.6b"
        返回: (模型名称, 版本名称, 模型显示名称)
        """
        parsed_model_name = model_name
        parsed_version_name = None
        
        # 解析模型名称和版本
        if model_name and '-' in model_name:
            parts = model_name.split('-', 1)
            if len(parts) == 2:
                parsed_model_name = parts[0]
                parsed_version_name = parts[1]
        
        # 构建模型显示名称
        model_display_name = parsed_model_name
        # 添加对None值的处理
        if parsed_model_name and parsed_version_name:
            model_display_name = f"{parsed_model_name} - {parsed_version_name}"
        
        return parsed_model_name, parsed_version_name, model_display_name

    @staticmethod
    def validate_model(model_name):
        """
        验证模型是否存在且已配置
        返回: (model_object, error_response, error_code)
        """
        model = next((m for m in db['models'] if m['name'] == model_name), None)
        if not model:
            return None, {'error': '模型不存在'}, 404
        if not model['configured']:
            return None, {'error': '模型未配置，无法调用'}, 400
        return model, None, None
    
    @staticmethod
    def get_version_config(model, version_id):
        """
        获取模型的版本配置
        
        参数:
            model: 模型对象
            version_id: 模型版本ID
            
        返回:
            版本配置字典
        """
        # 尝试从模型对象中获取版本配置
        if 'versions' in model and isinstance(model['versions'], list):
            # 查找匹配的版本
            for version in model['versions']:
                if version.get('id') == version_id:
                    return version
        # 如果没有找到匹配的版本或模型没有versions字段，返回默认配置
        return {
            'streaming_config': True,  # 默认启用流式传输
            'temperature': 0.7,  # 默认温度
            'max_tokens': 4096  # 默认最大令牌数
        }



    @staticmethod
    def create_ai_message(now, content, model_display_name):
        """创建标准格式的AI回复消息"""
        return {
            'id': str(uuid.uuid4()),
            'role': 'assistant',
            'content': content,  # 保留原始content字段以兼容旧版前端
            'createdAt': now,
            'model': model_display_name
        }

    @staticmethod
    def update_chat_and_save(chat, message_text, user_message, ai_message, now):
        """更新对话并保存"""
        # 添加AI回复到对话（内存）
        chat['messages'].append(ai_message)
        
        # 更新对话的更新时间
        chat['updatedAt'] = now
        
        # 更新对话预览（使用消息的前50个字符）
        preview_text = message_text[:50] + (message_text[50:] and '...')
        chat['preview'] = preview_text
        
        # 自动更新对话标题（如果是首次消息且标题还是默认的"新对话"）
        new_title = chat['title']
        if len(chat['messages']) == 2 and chat['title'] == '新对话':
            # 使用用户的第一条消息作为标题（截取前30个字符）
            new_title = message_text[:30] + (message_text[30:] and '...')
            chat['title'] = new_title
        
        try:
            # 获取数据库连接
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 保存用户消息到数据库
            cursor.execute('''
            INSERT OR REPLACE INTO messages (id, chat_id, role, content, created_at, model)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_message['id'], chat['id'], user_message['role'], user_message['content'], user_message['createdAt'], user_message.get('model')))
            
            # 保存AI消息到数据库
            cursor.execute('''
            INSERT OR REPLACE INTO messages (id, chat_id, role, content, created_at, model)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (ai_message['id'], chat['id'], ai_message['role'], ai_message['content'], ai_message['createdAt'], ai_message.get('model')))
            
            # 更新对话信息
            cursor.execute('''
            UPDATE chats SET title = ?, preview = ?, updated_at = ?
            WHERE id = ?
            ''', (new_title, preview_text, now, chat['id']))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ 更新对话失败: {str(e)}")

    @staticmethod
    def _prepare_messages_for_model(chat_id, enhanced_question):
        """
        准备发送给模型的消息格式
        
        参数:
            chat_id: 对话ID
            enhanced_question: 增强后的问题
        
        返回:
            格式化的消息列表
        """
        # 获取对话上下文历史
        context_messages = ChatService.get_chat_context(chat_id)
        
        # 准备消息格式，如果有上下文则使用上下文，否则使用当前问题
        if context_messages and len(context_messages) > 0:
            # 替换最后一条消息（即当前消息）的内容为增强后的问题
            messages = context_messages.copy()
            if messages:
                messages[-1]['content'] = enhanced_question
        else:
            # 如果没有上下文历史，只发送当前问题
            messages = [{'role': 'user', 'content': enhanced_question}]
        
        return messages
    
    @staticmethod
    def chat_with_model_stream(model_name, messages, parsed_version_name, temperature=0.7):
        """
        直接调用的流式模型回复函数
        
        参数:
            model_name: 模型名称
            messages: 消息列表
            temperature: 随机性参数，默认0.7
            parsed_version_name: 解析后的模型版本名称（可选）
        
        返回:
            生成器，产生流式响应块
        """
        # 使用通用验证函数验证模型
        model, error_response, _ = ChatService.validate_model(model_name)
        if error_response:
            error_data = error_response
            yield f'data: {json.dumps(error_data, ensure_ascii=False)}\n\n'
            return
        
        # 检查是否启用了流式传输
        version_id = parsed_version_name
        version_config = ChatService.get_version_config(model, version_id)
        
        streaming_config = version_config.get('streaming_config', False)
        if not streaming_config:
            error_data = {'error': '该模型未启用流式传输'}
            yield f'data: {json.dumps(error_data, ensure_ascii=False)}\n\n'
            return

        try:
            # 使用模型管理器获取流式响应
            stream = ModelManager.chat(model_name, model, version_config, messages, temperature, stream=True)

            # 直接迭代并返回流式响应
            for chunk in stream:
                yield chunk

        except Exception as e:
            # 捕获所有异常并返回错误信息
            print(f'调用模型失败: {str(e)}')
            response_data = {'error': str(e)}
            yield f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'

    @staticmethod
    def handle_streaming_response(chat, message_text, user_message, now,
                                 enhanced_question, parsed_model_name, parsed_version_name, model_params, model_display_name):
        """处理流式响应"""
        def generate():
            try:
                # 准备消息格式
                messages = ChatService._prepare_messages_for_model(chat['id'], enhanced_question)
                
                # 获取temperature参数
                temperature = model_params.get('temperature', 0.7)
                
                # 初始化完整回复
                full_reply = ""
                
                # 使用流式模型回复函数获取响应，传入parsed_version_name
                for chunk in ChatService.chat_with_model_stream(parsed_model_name, messages, parsed_version_name, temperature):
                    # 检查是否是错误消息格式
                    if isinstance(chunk, str) and chunk.startswith('data: {"error"'):
                        yield chunk
                        continue
                    
                    # 尝试解析chunk数据
                    try:
                        # 如果chunk已经是格式化的字符串，直接处理
                        if isinstance(chunk, str) and chunk.startswith('data: '):
                            chunk_str = chunk[6:].strip()
                            chunk_data = json.loads(chunk_str)
                            
                            if 'chunk' in chunk_data:
                                actual_chunk = chunk_data['chunk']
                                full_reply += actual_chunk
                                yield chunk  # 直接传递格式化的chunk
                            elif 'error' in chunk_data:
                                yield chunk  # 直接传递错误信息
                        else:
                            # 假设chunk是直接的内容块
                            full_reply += chunk
                            response_data = {
                                'chunk': chunk,
                                'done': False
                            }
                            yield f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'
                    except Exception as e:
                        print(f"处理流式响应块失败: {e}")
                        # 尝试作为直接内容处理
                        full_reply += str(chunk)
                        response_data = {
                            'chunk': str(chunk),
                            'done': False
                        }
                        yield f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'
                
                # 创建AI回复，确保包含完整的模型和版本信息
                ai_message = ChatService.create_ai_message(now, full_reply, model_display_name)
                
                # 更新对话并保存
                ChatService.update_chat_and_save(chat, message_text, user_message, ai_message, now)
                
                # 发送最终完成信号
                final_data = {
                    'chunk': '',
                    'done': True,
                    'chat': chat,
                    'user_message': user_message,
                    'ai_message': ai_message
                }
                yield f'data: {json.dumps(final_data, ensure_ascii=False)}\n\n'
            except Exception as e:
                # 捕获所有异常并返回错误信息
                print(f'流式处理失败: {str(e)}')
                response_data = {'error': str(e)}
                yield f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'
        
        return generate

    @staticmethod
    def handle_regular_response(chat, message_text, user_message, now,
                              enhanced_question, parsed_model_name, parsed_version_name, model_params, model_display_name):
        """处理普通响应"""
        try:
            # 使用通用验证函数验证模型
            model, error_response, error_code = ChatService.validate_model(parsed_model_name)
            if error_response:
                return error_response, error_code

            # 准备消息格式
            messages = ChatService._prepare_messages_for_model(chat['id'], enhanced_question)
            
            # 获取temperature参数
            temperature = model_params.get('temperature', 0.7)
            
            # 获取版本配置
            version_id = parsed_version_name
            version_config = ChatService.get_version_config(model, version_id)

            # 使用模型管理器调用模型
            response = ModelManager.chat(parsed_model_name, model, version_config, messages, temperature)
            
            # 获取模型回复内容
            ai_reply = response['content']
        except Exception as e:
            # 捕获所有异常并返回错误信息
            print(f'调用模型失败: {str(e)}')
            return {'error': f'调用模型失败: {str(e)}'}, 500
        
        # 创建AI回复，确保包含完整的模型和版本信息
        ai_message = ChatService.create_ai_message(now, ai_reply, model_display_name)
        
        # 更新对话并保存
        ChatService.update_chat_and_save(chat, message_text, user_message, ai_message, now)
        
        return {
            'success': True,
            'chat': chat,
            'user_message': user_message,
            'ai_message': ai_message
        }, 201

    @staticmethod
    def send_message(chat_id, data):
        """发送消息（应用层）
        
        参数:
            chat_id: 对话ID
            data: 包含所有必要信息的请求数据对象
        """
        # 从数据中提取所需参数
        message_text = data.get('message')
        model_name = data.get('model', '')
        model_params = data.get('modelParams', {})
        rag_config = data.get('ragConfig', {})
        stream = data.get('stream', False)
        
        # 查找匹配ID的对话
        chat = ChatService.get_chat(chat_id)
        if not chat:
            return {'error': '对话不存在'}, 404
        
        now = datetime.now().isoformat()
        
        # 创建用户消息
        user_message = {
            'id': str(uuid.uuid4()),
            'role': 'user',
            'content': message_text,
            'createdAt': now
        }
        chat['messages'].append(user_message)
        
        # 使用辅助函数解析模型信息
        # parsed_version_name 目前未直接使用，但为了代码清晰和未来扩展性保留接收
        parsed_model_name, parsed_version_name, model_display_name = ChatService.parse_model_info(model_name)
        
        # 如果没有传递模型，返回错误
        if not parsed_model_name:
            return {'error': '请指定模型'}, 400
        
        # 调用RAG系统构造增强提示，考虑前端传递的ragConfig配置
        enhanced_question = ChatService.get_rag_enhanced_prompt(message_text, rag_config) if rag_config.get('enabled', False) else message_text
        
        # 根据stream参数决定是返回普通响应还是流式响应
        if stream:
            # 流式响应处理
            return ChatService.handle_streaming_response(
                chat, message_text, user_message, now,
                enhanced_question, parsed_model_name, parsed_version_name, model_params, model_display_name
            )
        else:
            # 普通响应处理
            return ChatService.handle_regular_response(
                chat, message_text, user_message, now,
                enhanced_question, parsed_model_name, parsed_version_name, model_params, model_display_name
            )