"""API路由模块"""

# 导入路由模块
from app.api.chats import chat_bp
from app.api.models import model_bp
from app.api.mcp import mcp_bp
from app.api.rag import rag_bp

__all__ = ['chat_bp', 'model_bp', 'mcp_bp', 'rag_bp']