"""模型数据访问类"""
from app.repositories.base_repository import BaseRepository

class ModelRepository(BaseRepository):
    """模型数据访问类，处理模型相关的数据访问"""
    
    def get_all_models(self):
        """获取所有模型"""
        query = "SELECT * FROM models"
        return self.fetch_all(query)
    
    def get_model_by_name(self, model_name):
        """根据名称获取模型"""
        query = "SELECT * FROM models WHERE name = ?"
        return self.fetch_one(query, (model_name,))
    
    def create_model(self, name, description, configured, enabled, icon_class, icon_bg, icon_color, icon_url, icon_blob):
        """创建新模型"""
        query = '''
        INSERT INTO models (name, description, configured, enabled, icon_class, icon_bg, icon_color, icon_url, icon_blob)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        return self.execute(query, (name, description, configured, enabled, icon_class, icon_bg, icon_color, icon_url, icon_blob))
    
    def update_model(self, name, description, configured, enabled, icon_class, icon_bg, icon_color, icon_url, icon_blob):
        """更新模型"""
        query = '''
        UPDATE models SET description = ?, configured = ?, enabled = ?, 
        icon_class = ?, icon_bg = ?, icon_color = ?, icon_url = ?, icon_blob = ?
        WHERE name = ?
        '''
        return self.execute(query, (description, configured, enabled, icon_class, icon_bg, icon_color, icon_url, icon_blob, name))
    
    def get_model_versions(self, model_id):
        """获取模型的所有版本"""
        query = "SELECT * FROM model_versions WHERE model_id = ?"
        return self.fetch_all(query, (model_id,))
    
    def get_model_version(self, model_id, version_name):
        """获取特定版本的模型"""
        query = "SELECT * FROM model_versions WHERE model_id = ? AND version_name = ?"
        return self.fetch_one(query, (model_id, version_name))
    
    def create_model_version(self, model_id, version_name, custom_name, api_key, api_base_url, streaming_config):
        """创建新模型版本"""
        query = '''
        INSERT INTO model_versions (model_id, version_name, custom_name, api_key, api_base_url, streaming_config)
        VALUES (?, ?, ?, ?, ?, ?)
        '''
        return self.execute(query, (model_id, version_name, custom_name, api_key, api_base_url, streaming_config))
    
    def update_model_version(self, model_id, version_name, custom_name, api_key, api_base_url, streaming_config):
        """更新模型版本，不存在则创建"""
        query = '''
        INSERT OR REPLACE INTO model_versions (model_id, version_name, custom_name, api_key, api_base_url, streaming_config)
        VALUES (?, ?, ?, ?, ?, ?)
        '''
        return self.execute(query, (model_id, version_name, custom_name, api_key, api_base_url, streaming_config))
    
    def delete_model_version(self, model_id, version_name):
        """删除模型版本"""
        query = "DELETE FROM model_versions WHERE model_id = ? AND version_name = ?"
        return self.execute(query, (model_id, version_name))
    
    def get_model_icon(self, model_name):
        """根据模型名称获取图标"""
        query = "SELECT icon_blob FROM models WHERE name = ?"
        return self.fetch_one(query, (model_name,))
