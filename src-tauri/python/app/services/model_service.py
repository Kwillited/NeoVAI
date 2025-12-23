"""模型服务层，处理模型相关的业务逻辑"""

# 依赖数据管理模块
from app.core.data_manager import db, save_data
from app.services.base_service import BaseService


class ModelService(BaseService):
    """模型服务类，封装所有模型相关的业务逻辑"""

    @staticmethod
    def get_all_models():
        """获取所有模型供应商以及模型版本"""
        # 返回模型数据，过滤掉icon_blob字段，避免JSON序列化错误
        models = []
        for model in db['models']:
            # 复制模型字典，排除icon_blob字段
            filtered_model = {k: v for k, v in model.items() if k != 'icon_blob'}
            models.append(filtered_model)
        return models

    @staticmethod
    def configure_model(model_name, data):
        """
        配置特定模型
        
        Args:
            model_name: 模型名称
            data: 配置数据
            
        Returns:
            元组: (成功标志, 消息, 模型对象)
        """
        # 查找匹配名称的模型
        model = next((m for m in db['models'] if m['name'] == model_name), None)
        if not model:
            return False, '模型不存在', None
        
        # 确保模型有versions数组
        if 'versions' not in model:
            model['versions'] = []
        
        # 获取要配置的版本名称（如果指定了特定版本）
        target_version_name = data.get('version_name', '')
        
        # 查找匹配的版本
        version = next((v for v in model['versions'] if v.get('version_name') == target_version_name), None)
        
        # 如果找不到匹配的版本，创建一个新的版本对象
        if not version:
            version = {}  # 初始化为空对象，只添加必要的字段
            if target_version_name:  # 只有当version_name有值时才添加
                version['version_name'] = target_version_name
            model['versions'].append(version)
        
        # 将配置信息写入到该版本中，只添加必要的字段
        if target_version_name:  # 确保version_name存在
            version['version_name'] = target_version_name
        
        # 只更新必要的配置字段
        if 'custom_name' in data:
            version['custom_name'] = data['custom_name']
        if 'api_key' in data:
            version['api_key'] = data['api_key']
        if 'api_base_url' in data:
            version['api_base_url'] = data['api_base_url']
        version['streaming_config'] = data.get('streaming_config', False)  # 流式配置
    
        
        # 更新模型的顶级配置字段
        # 对于首次配置的模型，默认设置为启用状态
        is_first_configuration = not model.get('configured')
        model.update({
            'configured': True,
            'enabled': True if is_first_configuration else data.get('enabled', model.get('enabled', True))
        })
        
        # 额外确保首次配置时的enabled状态为True
        if is_first_configuration:
            model['enabled'] = True
        
        # 此处只更新模型的基本配置信息
        save_data()
        # 过滤掉icon_blob字段，避免JSON序列化错误
        filtered_model = {k: v for k, v in model.items() if k != 'icon_blob'}
        return True, f'模型 {model_name} 已配置', filtered_model

    @staticmethod
    def delete_model(model_name):
        """
        删除特定模型配置
        
        Args:
            model_name: 模型名称
            
        Returns:
            元组: (成功标志, 消息)
        """
        # 查找匹配名称的模型
        model = next((m for m in db['models'] if m['name'] == model_name), None)
        if not model:
            return False, '模型不存在'
        
        # 清空versions数组
        if 'versions' in model:
            model['versions'] = []
        
        # 重置模型的顶级配置字段
        model.update({
            'configured': False,
            'enabled': False
        })
        
        save_data()
        return True, f'模型 {model_name} 配置已删除'

    @staticmethod
    def update_model_enabled(model_name, enabled):
        """
        更新模型启用状态
        
        Args:
            model_name: 模型名称
            enabled: 是否启用
            
        Returns:
            元组: (成功标志, 消息)
        """
        # 查找匹配名称的模型
        model = next((m for m in db['models'] if m['name'] == model_name), None)
        if not model:
            return False, '模型不存在'
        
        # 更新模型启用状态
        model['enabled'] = enabled
        
        save_data()
        return True, f'模型 {model_name} 启用状态已更新'

    @staticmethod
    def delete_version(model_name, version_name):
        """
        删除特定模型的特定版本
        
        Args:
            model_name: 模型名称
            version_name: 版本名称
            
        Returns:
            元组: (成功标志, 消息, 模型对象)
        """
        # 查找匹配名称的模型
        model = next((m for m in db['models'] if m['name'] == model_name), None)
        if not model:
            return False, '模型不存在', None
        
        # 检查模型是否有versions数组
        if 'versions' not in model or not model['versions']:
            return False, '该模型没有版本信息', None
        
        # 查找匹配的版本
        version_index = next((i for i, v in enumerate(model['versions']) if v['version_name'] == version_name), None)
        if version_index is None:
            return False, '版本不存在', None
        
        # 从versions数组中删除该版本
        del model['versions'][version_index]

        # 如果模型没有版本了，设置为未配置
        if not model['versions']:
            model['configured'] = False
            model['enabled'] = False
        
        save_data()
        # 过滤掉icon_blob字段，避免JSON序列化错误
        filtered_model = {k: v for k, v in model.items() if k != 'icon_blob'}
        return True, f'版本 {version_name} 已成功删除', filtered_model