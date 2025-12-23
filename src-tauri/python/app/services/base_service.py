"""服务基类，提供公共功能"""


class BaseService:
    """所有服务类的基类，封装公共方法"""

    @staticmethod
    def get_version_config(model, version_id):
        """
        从模型的versions数组中获取特定版本的配置信息
        
        参数:
            model: 模型对象
            version_id: 版本ID或名称（支持version_name和custom_name）
            
        返回:
            版本配置字典
        """
        # 如果model没有versions数组或version_id为空，返回空字典
        if not model.get('versions') or not version_id:
            return {}
        
        # 查找匹配的版本，支持version_name和custom_name
        version = next((v for v in model['versions'] 
                      if v.get('version_name') == version_id or v.get('custom_name') == version_id), None)
        
        # 返回版本的配置信息（如果找到），否则返回空字典
        return version if version else {}