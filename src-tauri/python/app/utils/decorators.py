"""装饰器工具函数"""
from functools import wraps
from app.services.base_service import BaseService


def handle_exception(func):
    """
    统一异常处理装饰器
    
    Args:
        func: 被装饰的函数
    
    Returns:
        装饰后的函数
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            BaseService.log_error(f"{func.__name__} 失败: {str(e)}")
            return {'error': str(e)}, 500
    return wrapper
