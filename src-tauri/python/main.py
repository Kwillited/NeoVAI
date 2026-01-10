"""Chato应用入口"""
import os
from app import create_app
from app.core.config import ConfigManager
from app.core.data_manager import load_data

# 获取配置管理器单例实例
config_manager = ConfigManager.get_instance()
# 导入路由模块
from app.api.chats import chat_bp
from app.api.models import model_bp
from app.api.rag import rag_bp
from app.api.mcp import mcp_bp

# 导入RAG实例管理函数
from app.services.rag_service import set_rag_instance

def get_config_value(config_manager, key_path, default=None):
    """安全地获取配置值
    
    Args:
        config_manager: 配置管理器实例
        key_path: 配置键路径，如 'rag.enabled'
        default: 默认值
        
    Returns:
        配置值或默认值
    """
    try:
        # 尝试访问_config属性
        if hasattr(config_manager, '_config'):
            config = config_manager._config
            keys = key_path.split('.')
            for key in keys:
                if isinstance(config, dict) and key in config:
                    config = config[key]
                else:
                    return default
            return config
        return default
    except Exception:
        return default

def init_rag():
    """初始化RAG系统"""
    # 从配置中读取RAG参数
    if get_config_value(config_manager, 'rag.enabled', False):
        try:
            from app.services.vector_store_service import VectorStoreService
            from app.services.rag_service import set_rag_instance, get_vector_store_service
            
            # 使用标准的用户数据目录
            user_data_dir = config_manager.get_user_data_dir()
            data_dir = os.path.join(user_data_dir, 'Retrieval-Augmented Generation', 'files')  # 文档目录
            
            # 确保目录存在
            os.makedirs(data_dir, exist_ok=True)
            
            # 使用配置文件中的向量数据库路径
            vector_db_path = get_config_value(config_manager, 'rag.vector_db_path', 
                                           os.path.join(user_data_dir, 'Retrieval-Augmented Generation', 'vectorDb'))
            # 获取嵌入模型配置
            embedder_model = get_config_value(config_manager, 'rag.embedder_model', 'qwen3-embedding-0.6b')
            
            # 创建向量存储服务实例
            vector_service = VectorStoreService(vector_db_path, embedder_model)
            
            # 通过兼容接口设置实例
            set_rag_instance(None)  # 不再需要旧的rag_instance
            
            print(f"✅ RAG系统初始化成功: 模型={embedder_model}, 向量库={vector_db_path}")
            return True
        except Exception as e:
            print(f"❌ RAG系统初始化失败: {e}")
            return False
    return False

# 创建应用实例
app = create_app()

def setup():
    """应用初始化"""
    # 加载初始数据
    load_data()
    # 初始化RAG
    init_rag()

if __name__ == '__main__':
    # 从配置中获取应用设置
    debug = get_config_value(config_manager, 'app.debug', True)
    host = get_config_value(config_manager, 'app.host', '0.0.0.0')
    port = get_config_value(config_manager, 'app.port', 5000)
    
    # 仅在作为主程序运行时执行初始化
    # 这样可以避免Flask调试模式下初始化被执行两次
    if not debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        setup()
    
    # 启动服务
    app.run(
        debug=debug,
        host=host,
        port=port
    )