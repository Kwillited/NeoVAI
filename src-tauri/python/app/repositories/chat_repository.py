"""对话数据访问类"""
from app.repositories.base_repository import BaseRepository

class ChatRepository(BaseRepository):
    """对话数据访问类，处理对话相关的数据访问"""
    
    def get_all_chats(self):
        """获取所有对话"""
        query = "SELECT * FROM chats ORDER BY updated_at DESC"
        return self.fetch_all(query)
    
    def get_chat_by_id(self, chat_id):
        """根据ID获取对话"""
        query = "SELECT * FROM chats WHERE id = ?"
        return self.fetch_one(query, (chat_id,))
    
    def create_chat(self, chat_id, title, preview, created_at, updated_at):
        """创建新对话"""
        query = '''
        INSERT INTO chats (id, title, preview, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        '''
        return self.execute(query, (chat_id, title, preview, created_at, updated_at))
    
    def update_chat(self, chat_id, title, preview, updated_at, pinned=0):
        query = """
        UPDATE chats SET title = ?, preview = ?, updated_at = ?, pinned = ?
        WHERE id = ?
        """
        return self.execute(query, (title, preview, updated_at, pinned, chat_id))
    
    def delete_chat(self, chat_id):
        """删除对话"""
        query = "DELETE FROM chats WHERE id = ?"
        return self.execute(query, (chat_id,))
    
    def delete_all_chats(self):
        """删除所有对话"""
        query = "DELETE FROM chats"
        return self.execute(query)
