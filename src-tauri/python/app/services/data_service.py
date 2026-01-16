"""数据服务层 - 封装内存数据管理和脏标记机制"""
from app.core.data_manager import db, save_data, set_dirty_flag, get_db_connection
from app.services.base_service import BaseService

class DataService(BaseService):
    """数据服务类，封装所有数据相关的操作"""
    
    @staticmethod
    def begin_transaction():
        """开始事务"""
        conn = get_db_connection()
        conn.execute("BEGIN TRANSACTION")
        return conn
    
    @staticmethod
    def commit_transaction(conn):
        """提交事务"""
        conn.commit()
        conn.close()
    
    @staticmethod
    def rollback_transaction(conn):
        """回滚事务"""
        conn.rollback()
        conn.close()
    
    @staticmethod
    def get_chats():
        """获取所有对话"""
        return db['chats']
    
    @staticmethod
    def get_models():
        """获取所有模型"""
        return db['models']
    
    @staticmethod
    def get_settings():
        """获取所有设置"""
        return db['settings']
    
    @staticmethod
    def set_dirty_flag(data_type, is_dirty=True):
        """设置脏标记"""
        set_dirty_flag(data_type, is_dirty)
    
    @staticmethod
    def save_data():
        """保存数据"""
        save_data()
    
    @staticmethod
    def get_chat_by_id(chat_id):
        """根据ID获取对话"""
        return next((c for c in db['chats'] if c['id'] == chat_id), None)
    
    @staticmethod
    def get_model_by_name(model_name):
        """根据名称获取模型"""
        return next((m for m in db['models'] if m['name'] == model_name), None)
    
    @staticmethod
    def add_chat(chat):
        """添加对话"""
        db['chats'].insert(0, chat)
        DataService.set_dirty_flag('chats')
    
    @staticmethod
    def remove_chat(chat_id):
        """移除对话"""
        chat_index = next((i for i, c in enumerate(db['chats']) if c['id'] == chat_id), None)
        if chat_index is not None:
            db['chats'].pop(chat_index)
            DataService.set_dirty_flag('chats')
    
    @staticmethod
    def clear_chats():
        """清空对话"""
        db['chats'] = []
        DataService.set_dirty_flag('chats')
    
    @staticmethod
    def update_model(model_name, updated_model):
        """更新模型"""
        model = DataService.get_model_by_name(model_name)
        if model:
            model.update(updated_model)
            DataService.set_dirty_flag('models')
    
    @staticmethod
    def update_setting(key, value):
        """更新设置"""
        db['settings'][key] = value
        DataService.set_dirty_flag('settings')
