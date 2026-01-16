"""消息数据访问类"""
from app.repositories.base_repository import BaseRepository

class MessageRepository(BaseRepository):
    """消息数据访问类，处理消息相关的数据访问"""
    
    def get_messages_by_chat_id(self, chat_id):
        """根据对话ID获取所有消息"""
        query = "SELECT * FROM messages WHERE chat_id = ? ORDER BY created_at"
        return self.fetch_all(query, (chat_id,))
    
    def get_message_by_id(self, message_id):
        """根据ID获取消息"""
        query = "SELECT * FROM messages WHERE id = ?"
        return self.fetch_one(query, (message_id,))
    
    def create_message(self, message_id, chat_id, role, actual_content, thinking, created_at, model):
        """创建新消息"""
        query = '''
        INSERT INTO messages (id, chat_id, role, actual_content, thinking, created_at, model)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        return self.execute(query, (message_id, chat_id, role, actual_content, thinking, created_at, model))
    
    def update_message(self, message_id, role, actual_content, thinking, created_at, model):
        """更新消息"""
        query = '''
        UPDATE messages SET role = ?, actual_content = ?, thinking = ?, created_at = ?, model = ?
        WHERE id = ?
        '''
        return self.execute(query, (role, actual_content, thinking, created_at, model, message_id))
    
    def delete_messages_by_chat_id(self, chat_id):
        """根据对话ID删除所有消息"""
        query = "DELETE FROM messages WHERE chat_id = ?"
        return self.execute(query, (chat_id,))
    
    def delete_all_messages(self):
        """删除所有消息"""
        query = "DELETE FROM messages"
        return self.execute(query)
