"""测试聊天记录保存到数据库功能"""
import pytest
import os
import json
from app.services.chat_service import ChatService
from app.services.data_service import DataService
from app.core.data_manager import load_data, save_chats_to_db

class TestChatSaveToDatabase:
    """测试聊天记录保存到数据库功能"""
    
    def setup_method(self):
        """测试前的设置"""
        # 确保数据服务已初始化
        load_data()
        
        # 清空内存数据
        DataService.clear_chats()
        
        # 清空数据库数据
        from app.repositories.chat_repository import ChatRepository
        from app.repositories.message_repository import MessageRepository
        from app.core.database import get_db
        
        db_session = next(get_db())
        chat_repo = ChatRepository(db_session)
        message_repo = MessageRepository(db_session)
        
        message_repo.delete_all_messages()
        chat_repo.delete_all_chats()
    
    def teardown_method(self):
        """测试后的清理"""
        # 清空测试数据
        from app.repositories.chat_repository import ChatRepository
        from app.repositories.message_repository import MessageRepository
        from app.core.database import get_db
        
        db_session = next(get_db())
        chat_repo = ChatRepository(db_session)
        message_repo = MessageRepository(db_session)
        
        message_repo.delete_all_messages()
        chat_repo.delete_all_chats()
        
        DataService.clear_chats()
    
    def test_chat_save_to_database(self):
        """测试聊天记录保存到数据库"""
        # 创建聊天服务实例
        chat_service = ChatService()
        
        # 创建一个新对话
        chat = chat_service.create_chat("测试对话")
        chat_id = chat["id"]
        
        # 验证对话已创建并添加到内存
        assert len(DataService.get_chats()) == 1
        assert DataService.get_chat_by_id(chat_id) is not None
        
        # 创建测试消息数据
        from datetime import datetime
        now = datetime.now().isoformat()
        
        user_message = {
            "id": "test-user-message-1",
            "role": "user",
            "content": "测试用户消息",
            "createdAt": now
        }
        
        ai_message = {
            "id": "test-ai-message-1",
            "role": "assistant",
            "content": "测试AI回复",
            "createdAt": now,
            "model": "test-model"
        }
        
        # 将用户消息添加到内存中的对话对象
        chat['messages'].append(user_message)
        
        # 更新对话并保存
        chat_service.update_chat_and_save(
            chat=chat,
            message_text="测试用户消息",
            user_message=user_message,
            ai_message=ai_message,
            now=now
        )
        
        # 手动调用保存数据方法
        from app.core.data_manager import save_data
        save_data()
        
        # 验证脏标记已被清除
        from app.core.data_manager import dirty_flags
        assert dirty_flags['chats'] is False
        
        # 从数据库加载数据，验证数据已保存
        from app.repositories.chat_repository import ChatRepository
        from app.repositories.message_repository import MessageRepository
        from app.core.database import get_db
        
        db_session = next(get_db())
        chat_repo = ChatRepository(db_session)
        message_repo = MessageRepository(db_session)
        
        # 从数据库获取所有对话
        chats_from_db = chat_repo.get_all_chats()
        assert len(chats_from_db) == 1
        
        # 从数据库获取对话的消息
        messages_from_db = message_repo.get_messages_by_chat_id(chat_id)
        assert len(messages_from_db) == 2
        
        # 验证消息内容
        message_roles = [msg.role for msg in messages_from_db]
        assert "user" in message_roles
        assert "assistant" in message_roles
        
        # 验证消息内容
        for msg in messages_from_db:
            if msg.role == "user":
                assert msg.actual_content == "测试用户消息"
            elif msg.role == "assistant":
                assert msg.actual_content == "测试AI回复"
        
        # 清空内存数据，然后从数据库重新加载
        DataService.clear_chats()
        
        from app.core.data_manager import load_chats_from_db
        load_chats_from_db()
        
        # 验证数据已从数据库加载到内存
        chats_from_memory = DataService.get_chats()
        assert len(chats_from_memory) == 1
        
        loaded_chat = DataService.get_chat_by_id(chat_id)
        assert loaded_chat is not None
        assert len(loaded_chat["messages"]) == 2
        
        print("测试通过！聊天记录成功保存到数据库。")