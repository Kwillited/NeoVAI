"""对话相关业务逻辑服务"""
import sys
import uuid
import json
from datetime import datetime
from app.services.data_service import DataService
from app.repositories.chat_repository import ChatRepository
from app.repositories.message_repository import MessageRepository
from app.services.base_service import BaseService

class ChatService(BaseService):
    """对话服务类，封装所有对话相关的业务逻辑"""

    @staticmethod
    def get_chats():
        """获取所有对话"""
        try:
            # 使用Repository获取所有对话
            chat_repo = ChatRepository()
            message_repo = MessageRepository()
            
            # 先从数据库加载最新数据
            chats = chat_repo.get_all_chats()
            
            chat_list = []
            for chat_row in chats:
                # 处理可能的字段缺失情况
                chat_id = chat_row[0]
                title = chat_row[1] if len(chat_row) > 1 else '未命名对话'
                preview = chat_row[2] if len(chat_row) > 2 else ''
                created_at = chat_row[3] if len(chat_row) > 3 else datetime.now().isoformat()
                updated_at = chat_row[4] if len(chat_row) > 4 else datetime.now().isoformat()
                pinned = bool(chat_row[5] if len(chat_row) > 5 else 0)
                
                # 获取对话的所有消息
                messages = message_repo.get_messages_by_chat_id(chat_id)
                
                # 构建消息列表
                message_list = []
                for msg_row in messages:
                    msg_id = msg_row[0]
                    role = msg_row[2] if len(msg_row) > 2 else 'user'
                    content = msg_row[3] if len(msg_row) > 3 else ''
                    msg_created_at = msg_row[5] if len(msg_row) > 5 else datetime.now().isoformat()
                    model = msg_row[6] if len(msg_row) > 6 else None
                    files = msg_row[7] if len(msg_row) > 7 else None
                    
                    # 解析files字段（JSON字符串转列表）
                    files_list = []
                    if files:
                        try:
                            files_list = json.loads(files)
                        except json.JSONDecodeError:
                            files_list = []
                    
                    message_list.append({
                        'id': msg_id,
                        'role': role,
                        'content': content,
                        'createdAt': msg_created_at,
                        'model': model,
                        'files': files_list
                    })
                
                # 添加对话到列表
                chat_list.append({
                    'id': chat_id,
                    'title': title,
                    'preview': preview,
                    'createdAt': created_at,
                    'updatedAt': updated_at,
                    'pinned': pinned,
                    'messages': message_list
                })
            
            # 更新内存数据库
            DataService.get_chats().clear()
            DataService.get_chats().extend(chat_list)
            return chat_list
        except Exception as e:
            # 使用BaseService的日志方法
            BaseService.log_error(f"获取对话列表失败: {str(e)}")
            # 失败时返回内存数据库中的对话
            return DataService.get_chats()

    @staticmethod
    def create_chat(title=None):
        """创建新对话"""
        try:
            # 使用Repository创建对话
            chat_repo = ChatRepository()
            
            chat_id = str(uuid.uuid4())  # 生成唯一对话ID
            now = datetime.now().isoformat()  # 时间戳（ISO格式）
            
            title = title or '新对话'
            
            # 使用Repository插入到SQLite数据库
            chat_repo.create_chat(chat_id, title, '', now, now)
            
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
            DataService.add_chat(new_chat)
            
            return new_chat
        except Exception as e:
            # 使用BaseService的日志方法
            BaseService.log_error(f"创建对话失败: {str(e)}")
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
            DataService.add_chat(new_chat)
            return new_chat

    @staticmethod
    def get_chat(chat_id):
        """获取单个对话记录（按ID）"""
        # 先尝试从内存获取
        chat = DataService.get_chat_by_id(chat_id)
        if chat:
            return chat
        
        try:
            # 使用Repository获取对话
            chat_repo = ChatRepository()
            message_repo = MessageRepository()
            
            # 从数据库获取
            chat_row = chat_repo.get_chat_by_id(chat_id)
            if not chat_row:
                return None
            
            # 处理可能的字段缺失情况
            chat_id = chat_row[0]
            title = chat_row[1] if len(chat_row) > 1 else '未命名对话'
            preview = chat_row[2] if len(chat_row) > 2 else ''
            created_at = chat_row[3] if len(chat_row) > 3 else datetime.now().isoformat()
            updated_at = chat_row[4] if len(chat_row) > 4 else datetime.now().isoformat()
            
            # 获取对话的所有消息
            messages = message_repo.get_messages_by_chat_id(chat_id)
            
            # 构建消息列表
            message_list = []
            for msg_row in messages:
                msg_id = msg_row[0]
                role = msg_row[2] if len(msg_row) > 2 else 'user'
                content = msg_row[3] if len(msg_row) > 3 else ''
                msg_created_at = msg_row[5] if len(msg_row) > 5 else datetime.now().isoformat()
                model = msg_row[6] if len(msg_row) > 6 else None
                files = msg_row[7] if len(msg_row) > 7 else None
                
                # 解析files字段（JSON字符串转列表）
                files_list = []
                if files:
                    try:
                        files_list = json.loads(files)
                    except json.JSONDecodeError:
                        files_list = []
                
                message_list.append({
                    'id': msg_id,
                    'role': role,
                    'content': content,
                    'createdAt': msg_created_at,
                    'model': model,
                    'files': files_list
                })
            
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
            existing_chat = DataService.get_chat_by_id(chat_id)
            if not existing_chat:
                DataService.get_chats().append(chat)
            return chat
        except Exception as e:
            # 使用BaseService的日志方法
            BaseService.log_error(f"获取对话失败: {str(e)}")
            return None

    @staticmethod
    def delete_chat(chat_id):
        """删除单个对话记录（按ID）"""
        try:
            # 使用Repository删除对话
            chat_repo = ChatRepository()
            message_repo = MessageRepository()
            
            # 从数据库中删除对话（级联删除消息）
            chat_repo.delete_chat(chat_id)
            
            # 更新内存数据库
            DataService.remove_chat(chat_id)
            
            return True
        except Exception as e:
            # 使用BaseService的日志方法
            BaseService.log_error(f"删除对话失败: {str(e)}")
            # 尝试从内存中删除
            DataService.remove_chat(chat_id)
            return True

    @staticmethod
    def delete_all_chats():
        """删除所有对话记录"""
        try:
            # 使用Repository删除所有对话和消息
            chat_repo = ChatRepository()
            message_repo = MessageRepository()
            
            # 从数据库中删除所有对话和消息
            message_repo.delete_all_messages()
            chat_repo.delete_all_chats()
            
            # 清空内存中的对话数据
            DataService.clear_chats()
            
            return True
        except Exception as e:
            # 使用BaseService的日志方法
            BaseService.log_error(f"删除所有对话失败: {str(e)}")
            # 尝试清空内存
            DataService.clear_chats()
            return True
    
    @staticmethod
    def update_chat_pin(chat_id, pinned):
        """更新对话置顶状态"""
        try:
            # 使用Repository更新对话置顶状态
            chat_repo = ChatRepository()
            message_repo = MessageRepository()
            
            # 获取当前对话信息
            chat_row = chat_repo.get_chat_by_id(chat_id)
            if not chat_row:
                return False
            
            # 处理可能的字段缺失情况
            chat_id = chat_row[0]
            title = chat_row[1] if len(chat_row) > 1 else '未命名对话'
            preview = chat_row[2] if len(chat_row) > 2 else ''
            created_at = chat_row[3] if len(chat_row) > 3 else datetime.now().isoformat()
            updated_at = datetime.now().isoformat()
            
            # 更新数据库中的对话置顶状态
            chat_repo.update_chat(chat_id, title, preview, updated_at, int(pinned))
            
            # 更新内存数据库中的对话
            chats = DataService.get_chats()
            for chat in chats:
                if chat['id'] == chat_id:
                    chat['pinned'] = bool(pinned)
                    chat['updatedAt'] = updated_at
                    break
            
            return True
        except Exception as e:
            # 使用BaseService的日志方法
            BaseService.log_error(f"更新对话置顶状态失败: {str(e)}")
            return False
    
    @staticmethod
    def get_chat_context(chat_id, max_messages=10, deep_thinking=False):
        """
        获取对话上下文历史
        
        参数:
            chat_id: 对话ID
            max_messages: 最大获取的消息数量，默认10条
            deep_thinking: 是否启用深度思考，启用时保留think标签
            
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
                # 剔除content中的think标签内容，仅当未启用深度思考时
                content = original_content
                
                if not deep_thinking:
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
        """RAG增强提示 - 使用LangChain RAG服务"""
        # 只使用前端传递的enabled状态，其余配置从系统获取
        enabled = False
        if rag_config and isinstance(rag_config, dict):
            enabled = rag_config.get('enabled', False)
        
        if not enabled:
            return question
        
        try:
            # 使用新的LangChain RAG服务，它会从配置系统获取完整配置
            from app.services.langchain_rag_service import LangChainRAGService
            rag_service = LangChainRAGService.get_instance()
            return rag_service.get_enhanced_prompt(question, {'enabled': enabled})
        except Exception as e:
            # 使用BaseService的日志方法
            BaseService.log_error(f"RAG调用失败: {str(e)}")
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
        model = DataService.get_model_by_name(model_name)
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
            version_id: 模型版本名称或自定义名称
            
        返回:
            版本配置字典
        """
        # 尝试从模型对象中获取版本配置
        if 'versions' in model and isinstance(model['versions'], list):
            # 查找匹配的版本，支持version_name和custom_name
            for version in model['versions']:
                if version.get('version_name') == version_id or version.get('custom_name') == version_id:
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
            # 先设置脏标记，确保数据会被保存
            DataService.set_dirty_flag('chats', True)
            
            # 使用Repository保存对话和消息
            chat_repo = ChatRepository()
            message_repo = MessageRepository()
            
            # 保存用户消息到数据库
            message_repo.create_message(
                message_id=user_message['id'],
                chat_id=chat['id'],
                role=user_message['role'],
                actual_content=user_message['content'],
                thinking=None,
                created_at=user_message['createdAt'],
                model=user_message.get('model'),
                files=json.dumps(user_message.get('files', []))
            )
            
            # 保存AI消息到数据库
            message_repo.create_message(
                message_id=ai_message['id'],
                chat_id=chat['id'],
                role=ai_message['role'],
                actual_content=ai_message['content'],
                thinking=ai_message.get('thinking'),
                created_at=ai_message['createdAt'],
                model=ai_message.get('model'),
                files=json.dumps(ai_message.get('files', []))
            )
            
            # 更新对话信息
            chat_repo.update_chat(
                chat_id=chat['id'],
                title=new_title,
                preview=preview_text,
                updated_at=now
            )
            
            # 添加直接保存成功日志
            from app.core.logging_config import logger
            logger.info(f"Direct save succeeded: chat_id={chat['id']}, user_msg_id={user_message['id']}, ai_msg_id={ai_message['id']}")
        except Exception as e:
            # 使用BaseService的日志方法
            BaseService.log_error(f"Failed to update chat: {str(e)}")
            # 脏标记已经设置，自动保存机制会处理剩余工作
            from app.core.logging_config import logger
            logger.info(f"Direct save failed, relying on auto-save: chat_id={chat['id']}, error={str(e)}")

    @staticmethod
    def _prepare_messages_for_model(chat_id, enhanced_question, deep_thinking=False):
        """
        准备发送给模型的消息格式
        
        参数:
            chat_id: 对话ID
            enhanced_question: 增强后的问题
            deep_thinking: 是否启用深度思考
        
        返回:
            格式化的消息列表
        """
        # 获取对话上下文历史
        context_messages = ChatService.get_chat_context(chat_id, deep_thinking=deep_thinking)
        
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
            from app.models.model_manager import ModelManager
            stream = ModelManager.chat(model_name, model, version_config, messages, temperature, stream=True)

            # 直接迭代并返回流式响应
            for chunk in stream:
                yield chunk

        except Exception as e:
            # 捕获所有异常并返回错误信息
            BaseService.log_error(f'调用模型失败: {str(e)}')
            response_data = {'error': str(e)}
            yield f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'

    @staticmethod
    def handle_streaming_response(chat, message_text, user_message, now,
                                 enhanced_question, parsed_model_name, parsed_version_name, model_params, model_display_name, deep_thinking=False):
        """处理流式响应"""
        def generate():
            try:
                # 准备消息格式
                messages = ChatService._prepare_messages_for_model(chat['id'], enhanced_question, deep_thinking)
                
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
                        BaseService.log_error(f"处理流式响应块失败: {e}")
                        # 尝试作为直接内容处理
                        full_reply += str(chunk)
                        response_data = {
                            'chunk': str(chunk),
                            'done': False
                        }
                        yield f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'
                
                # 处理think标签，分离思考内容和实际内容
                import re
                think_pattern = re.compile(r'\s*<think>([\s\S]*?)</think>\s*', re.IGNORECASE)
                match = think_pattern.match(full_reply)
                
                thinking_content = None
                actual_content = full_reply
                
                if match:
                    thinking_content = match.group(1)
                    actual_content = think_pattern.sub('', full_reply).strip()
                
                # 创建AI回复，确保包含完整的模型和版本信息
                ai_message = ChatService.create_ai_message(now, actual_content, model_display_name)
                # 添加思考内容到AI消息
                ai_message['thinking'] = thinking_content
                
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
                BaseService.log_error(f'流式处理失败: {str(e)}')
                response_data = {'error': str(e)}
                yield f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'
        
        return generate

    @staticmethod
    def handle_regular_response(chat, message_text, user_message, now,
                              enhanced_question, parsed_model_name, parsed_version_name, model_params, model_display_name, deep_thinking=False):
        """处理普通响应"""
        try:
            # 使用通用验证函数验证模型
            model, error_response, error_code = ChatService.validate_model(parsed_model_name)
            if error_response:
                return error_response, error_code

            # 准备消息格式
            messages = ChatService._prepare_messages_for_model(chat['id'], enhanced_question, deep_thinking)
            
            # 获取temperature参数
            temperature = model_params.get('temperature', 0.7)
            
            # 获取版本配置
            version_id = parsed_version_name
            version_config = ChatService.get_version_config(model, version_id)

            from app.models.model_manager import ModelManager
            response = ModelManager.chat(parsed_model_name, model, version_config, messages, temperature)
            
            # 获取模型回复内容
            ai_reply = response['content']
        except Exception as e:
            # 捕获所有异常并返回错误信息
            BaseService.log_error(f'调用模型失败: {str(e)}')
            return {'error': f'调用模型失败: {str(e)}'}, 500
        
        # 处理think标签，分离思考内容和实际内容
        import re
        think_pattern = re.compile(r'\s*<think>([\s\S]*?)</think>\s*', re.IGNORECASE)
        match = think_pattern.match(ai_reply)
        
        thinking_content = None
        actual_content = ai_reply
        
        if match:
            thinking_content = match.group(1)
            actual_content = think_pattern.sub('', ai_reply).strip()
        
        # 创建AI回复，确保包含完整的模型和版本信息
        ai_message = ChatService.create_ai_message(now, actual_content, model_display_name)
        # 添加思考内容到AI消息
        ai_message['thinking'] = thinking_content
        
        # 更新对话并保存
        ChatService.update_chat_and_save(chat, message_text, user_message, ai_message, now)
        
        return {
            'success': True,
            'chat': chat,
            'user_message': user_message,
            'ai_message': ai_message
        }, 201

    @staticmethod
    def process_uploaded_files(files):
        """处理上传的文件，保存到临时目录并提取内容
        
        参数:
            files: 文件列表
        
        返回:
            提取的文件内容列表
        """
        extracted_contents = []
        
        if not files:
            return extracted_contents
        
        try:
            import os
            import tempfile
            import base64
            import mimetypes
            
            # 创建临时目录
            temp_dir = tempfile.mkdtemp()
            
            for file in files:
                # 检查文件结构
                if isinstance(file, dict) and 'name' in file and 'content' in file:
                    # 这是一个base64编码的文件
                    file_name = file['name']
                    file_content_base64 = file['content']
                    
                    try:
                        # 解码base64内容
                        file_content = base64.b64decode(file_content_base64)
                        
                        # 保存到临时文件
                        file_path = os.path.join(temp_dir, file_name)
                        with open(file_path, 'wb') as f:
                            f.write(file_content)
                        
                        # 简单的文件内容提取
                        content = ""
                        
                        # 根据文件扩展名选择提取方式
                        file_ext = os.path.splitext(file_name)[1].lower()
                        
                        # 只处理文本类文件
                        if file_ext in ['.txt', '.md', '.json', '.csv', '.py', '.js', '.html', '.css', '.xml', '.yaml', '.yml']:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                        elif file_ext in ['.pdf']:
                            # 简单处理PDF，只提取文本
                            try:
                                from PyPDF2 import PdfReader
                                reader = PdfReader(file_path)
                                for page in reader.pages:
                                    content += page.extract_text() + '\n'
                            except ImportError:
                                content = f"[PDF文件内容，无法提取，请安装PyPDF2库]"
                        elif file_ext in ['.doc', '.docx']:
                            # 简单处理Word文档
                            try:
                                from docx import Document
                                doc = Document(file_path)
                                for para in doc.paragraphs:
                                    content += para.text + '\n'
                            except ImportError:
                                content = f"[Word文件内容，无法提取，请安装python-docx库]"
                        else:
                            # 其他文件类型，只显示文件信息
                            content = f"[无法提取该类型文件的内容：{file_name}]"
                        
                        if content:
                            extracted_contents.append(f"文件 {file_name} 内容：\n{content}")
                    except Exception as decode_error:
                        BaseService.log_error(f"解码文件 {file_name} 失败: {str(decode_error)}")
        except Exception as e:
            # 记录错误但不中断流程
            BaseService.log_error(f"处理上传文件失败: {str(e)}")
        
        return extracted_contents
    
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
        user_model_params = data.get('modelParams', {})
        rag_enabled = data.get('ragConfig', {}).get('enabled', False)
        stream = data.get('stream', False)
        deep_thinking = data.get('deepThinking', False)
        files = data.get('files', [])
        
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
            'createdAt': now,
            'files': files  # 保存原始文件信息
        }
        chat['messages'].append(user_message)
        
        # 使用辅助函数解析模型信息
        parsed_model_name, parsed_version_name, model_display_name = ChatService.parse_model_info(model_name)
        
        # 如果没有传递模型，返回错误
        if not parsed_model_name:
            return {'error': '请指定模型'}, 400
        
        # 获取模型配置
        model = DataService.get_model_by_name(parsed_model_name)
        if not model:
            return {'error': f'模型 {parsed_model_name} 不存在'}, 400
        
        # 获取模型默认参数
        model_params = {
            'temperature': 0.7,
            'max_tokens': 2000,
            'top_p': 1,
            'frequency_penalty': 0
        }
        # 合并用户自定义参数
        model_params.update(user_model_params)
        
        # 处理上传的文件
        file_contents = ChatService.process_uploaded_files(files)
        
        # 合并文件内容到消息文本
        full_message_text = message_text
        if file_contents:
            full_message_text += "\n\n" + "\n\n".join(file_contents)
        
        # 调用RAG系统构造增强提示，仅根据enabled状态决定是否启用
        enhanced_question = ChatService.get_rag_enhanced_prompt(full_message_text, {'enabled': rag_enabled}) if rag_enabled else full_message_text
        
        # 根据stream参数决定是返回普通响应还是流式响应
        if stream:
            # 流式响应处理
            return ChatService.handle_streaming_response(
                chat, full_message_text, user_message, now,
                enhanced_question, parsed_model_name, parsed_version_name, model_params, model_display_name, deep_thinking
            )
        else:
            # 普通响应处理
            return ChatService.handle_regular_response(
                chat, full_message_text, user_message, now,
                enhanced_question, parsed_model_name, parsed_version_name, model_params, model_display_name, deep_thinking
            )