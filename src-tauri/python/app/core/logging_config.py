"""日志配置模块"""
import logging
import os
from logging.handlers import RotatingFileHandler

# 初始日志级别，后续会根据配置更新
LOG_LEVEL = logging.INFO

# 初始日志目录，后续会根据配置更新
LOG_DIR = os.path.join(os.getcwd(), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# 日志文件路径
LOG_FILE = os.path.join(LOG_DIR, 'chato.log')

# 创建日志记录器
logger = logging.getLogger('chato')
logger.setLevel(LOG_LEVEL)

# 防止重复添加处理器
if not logger.handlers:
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    
    # 创建文件处理器，支持日志轮转
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,  # 保留5个备份
        encoding='utf-8'
    )
    file_handler.setLevel(LOG_LEVEL)
    
    # 创建日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    # 设置处理器格式
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # 添加处理器到记录器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def update_log_config(config_manager):
    """根据配置更新日志设置"""
    global LOG_LEVEL, LOG_DIR, LOG_FILE
    
    # 更新日志级别
    LOG_LEVEL = logging.INFO
    if config_manager.get('app.debug', True):
        LOG_LEVEL = logging.DEBUG
    
    # 更新日志目录
    LOG_DIR = os.path.join(config_manager.get_user_data_dir(), 'logs')
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # 更新日志文件路径
    LOG_FILE = os.path.join(LOG_DIR, 'chato.log')
    
    # 更新日志记录器级别
    logger.setLevel(LOG_LEVEL)
    
    # 更新处理器
    for handler in logger.handlers:
        handler.setLevel(LOG_LEVEL)
        # 如果是文件处理器，更新文件路径
        if isinstance(handler, RotatingFileHandler):
            # 关闭旧的处理器
            logger.removeHandler(handler)
            handler.close()
            # 创建新的文件处理器
            new_handler = RotatingFileHandler(
                LOG_FILE,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,  # 保留5个备份
                encoding='utf-8'
            )
            new_handler.setLevel(LOG_LEVEL)
            new_handler.setFormatter(formatter)
            logger.addHandler(new_handler)

# 导出日志记录器
__all__ = ['logger']
