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


def init_rag():
    """初始化RAG系统"""
    # 从配置中读取RAG参数
    if config_manager.get('rag.enabled', False):
        try:
            from app.services.vector_store_service import VectorStoreService
            
            # 使用标准的用户数据目录
            user_data_dir = config_manager.get_user_data_dir()
            data_dir = os.path.join(user_data_dir, 'Retrieval-Augmented Generation', 'files')  # 文档目录
            
            # 确保目录存在
            os.makedirs(data_dir, exist_ok=True)
            
            # 使用配置文件中的向量数据库路径
            vector_db_path = config_manager.get('rag.vector_db_path', 
                                           os.path.join(user_data_dir, 'Retrieval-Augmented Generation', 'vectorDb'))
            # 获取嵌入模型配置
            embedder_model = config_manager.get('rag.embedder_model', 'qwen3-embedding-0.6b')
            
            # 创建向量存储服务实例
            vector_service = VectorStoreService(vector_db_path, embedder_model)
            
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
    debug = config_manager.get('app.debug', True)
    host = config_manager.get('app.host', '0.0.0.0')
    port = config_manager.get('app.port', 5000)
    
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