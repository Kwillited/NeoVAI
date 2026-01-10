"""配置管理工具函数"""
import os
import json
import sys


def get_user_data_dir(app_name='Chato', roaming=True):
    """
    获取用户数据目录，适配不同操作系统
    
    Args:
        app_name: 应用程序名称
        roaming: 在Windows上是否使用漫游目录
    
    Returns:
        str: 用户数据目录路径
    """
    if sys.platform == 'win32':
        if roaming:
            base_dir = os.path.expandvars(r'%APPDATA%')
        else:
            base_dir = os.path.expandvars(r'%LOCALAPPDATA%')
        return os.path.join(base_dir, app_name)
    elif sys.platform.startswith('darwin'):  # macOS
        return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', app_name)
    else:  # Linux 和其他 Unix-like 系统
        # 遵循 XDG Base Directory 规范
        base_dir = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
        return os.path.join(base_dir, app_name)


def get_app_config_dir(app_name='Chato'):
    """
    获取应用配置目录，适配不同操作系统
    
    Args:
        app_name: 应用程序名称
    
    Returns:
        str: 配置目录路径
    """
    if sys.platform == 'win32':
        return os.path.join(os.path.expandvars(r'%APPDATA%'), app_name)
    elif sys.platform.startswith('darwin'):
        return os.path.join(os.path.expanduser('~'), 'Library', 'Preferences', app_name)
    else:
        # 遵循 XDG Base Directory 规范
        config_dir = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
        return os.path.join(config_dir, app_name)


def get_app_cache_dir(app_name='Chato'):
    """
    获取应用缓存目录，适配不同操作系统
    
    Args:
        app_name: 应用程序名称
    
    Returns:
        str: 缓存目录路径
    """
    if sys.platform == 'win32':
        return os.path.join(os.path.expandvars(r'%LOCALAPPDATA%'), app_name, 'Cache')
    elif sys.platform.startswith('darwin'):
        return os.path.join(os.path.expanduser('~'), 'Library', 'Caches', app_name)
    else:
        # 遵循 XDG Base Directory 规范
        cache_dir = os.environ.get('XDG_CACHE_HOME', os.path.expanduser('~/.cache'))
        return os.path.join(cache_dir, app_name)


def load_json_config(config_file, default_config=None):
    """
    从JSON文件加载配置
    
    Args:
        config_file: 配置文件路径
        default_config: 默认配置（如果文件不存在或加载失败时使用）
    
    Returns:
        dict: 配置字典
    """
    if default_config is None:
        default_config = {}
    
    if not os.path.exists(config_file):
        return default_config
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 确保返回的是字典类型
            if not isinstance(config, dict):
                return default_config
            return config
    except Exception as e:
        print(f"加载配置文件失败 {config_file}: {e}")
        return default_config


def save_json_config(config_file, config):
    """
    将配置保存到JSON文件
    
    Args:
        config_file: 配置文件路径
        config: 要保存的配置字典
    
    Returns:
        bool: 是否成功保存
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"保存配置文件失败 {config_file}: {e}")
        return False


def get_environment_variable(name, default=None, required=False):
    """
    获取环境变量值
    
    Args:
        name: 环境变量名称
        default: 默认值（如果环境变量不存在）
        required: 是否为必需的环境变量
    
    Returns:
        str: 环境变量值
    
    Raises:
        ValueError: 当环境变量为必需但不存在时抛出
    """
    value = os.environ.get(name)
    
    if required and value is None:
        raise ValueError(f'必需的环境变量 {name} 不存在')
    
    return value if value is not None else default


def validate_config(config, required_keys=None, optional_keys=None):
    """
    验证配置字典
    
    Args:
        config: 配置字典
        required_keys: 必需的键列表
        optional_keys: 可选的键列表
    
    Returns:
        dict: 验证后的配置字典
    
    Raises:
        ValueError: 配置验证失败时抛出
    """
    if not isinstance(config, dict):
        raise ValueError('配置必须是字典类型')
    
    # 验证必需键
    if required_keys:
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise ValueError(f'配置缺少必需的键: {missing_keys}')
    
    # 验证可选键（如果指定了，则不允许其他键）
    if optional_keys is not None:
        all_allowed_keys = set(required_keys or []) | set(optional_keys)
        invalid_keys = [key for key in config if key not in all_allowed_keys]
        if invalid_keys:
            raise ValueError(f'配置包含无效的键: {invalid_keys}')
    
    return config


def update_config(config_file, updates, merge=True):
    """
    更新配置文件
    
    Args:
        config_file: 配置文件路径
        updates: 要更新的配置字典
        merge: 是否合并现有配置（True）或完全替换（False）
    
    Returns:
        bool: 是否成功更新
    """
    if not merge:
        return save_json_config(config_file, updates)
    
    # 合并模式：先加载现有配置，然后应用更新
    current_config = load_json_config(config_file)
    current_config.update(updates)
    return save_json_config(config_file, current_config)


def get_config_value(config, key_path, default=None):
    """
    从嵌套配置中获取值
    
    Args:
        config: 配置字典
        key_path: 键路径，例如 "database.host" 或 ["database", "host"]
        default: 默认值（如果键不存在）
    
    Returns:
        any: 配置值或默认值
    """
    # 将字符串路径转换为列表
    if isinstance(key_path, str):
        key_path = key_path.split('.')
    
    current = config
    try:
        for key in key_path:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default


def set_config_value(config, key_path, value):
    """
    设置嵌套配置中的值
    
    Args:
        config: 配置字典
        key_path: 键路径，例如 "database.host" 或 ["database", "host"]
        value: 要设置的值
    
    Returns:
        dict: 更新后的配置字典
    """
    # 将字符串路径转换为列表
    if isinstance(key_path, str):
        key_path = key_path.split('.')
    
    current = config
    # 遍历键路径，直到倒数第二个键
    for key in key_path[:-1]:
        if key not in current:
            current[key] = {}
        elif not isinstance(current[key], dict):
            raise ValueError(f'路径 {key_path} 中的键 {key} 不是字典')
        current = current[key]
    
    # 设置最终值
    current[key_path[-1]] = value
    return config