"""API路由模块"""

# 导入路由模块
from app.api.chats import router as chats_router
from app.api.models import router as models_router
from app.api.mcp import router as mcp_router
from app.api.rag import router as rag_router
from app.api.settings import router as settings_router

__all__ = ['register_routes']


def register_routes(app):
    """注册所有FastAPI路由"""
    # 直接在应用实例上添加健康检查端点
    @app.get('/api/health')
    def health_check():
        """健康检查端点"""
        return {"status": "ok"}
    
    app.include_router(chats_router, tags=['chats'])
    app.include_router(models_router, tags=['models'])
    app.include_router(mcp_router, tags=['mcp'])
    app.include_router(rag_router, tags=['rag'])
    app.include_router(settings_router, tags=['settings'])