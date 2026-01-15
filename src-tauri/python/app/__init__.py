"""Chato应用主包"""

# Flask应用实例
def create_app():
    """创建Flask应用实例"""
    from flask import Flask
    from flask_cors import CORS
    
    app = Flask(__name__)
    # 配置CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 注册蓝图
    from app.api import chat_bp, model_bp, mcp_bp, rag_bp, settings_bp
    app.register_blueprint(chat_bp)
    app.register_blueprint(model_bp)
    app.register_blueprint(mcp_bp)
    app.register_blueprint(rag_bp)
    app.register_blueprint(settings_bp)
    
    # 添加健康检查端点
    @app.route('/api/health')
    def health_check():
        """健康检查端点"""
        return app.response_class(
            response='{"status": "healthy", "message": "Chato backend service is running"}',
            status=200,
            mimetype='application/json'
        )
    
    return app