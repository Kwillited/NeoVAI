"""数据处理工具函数"""
import json
import time
from datetime import datetime
import uuid


def generate_unique_id(prefix=None, length=8):
    """
    生成唯一ID
    
    Args:
        prefix: ID前缀
        length: 随机部分长度
    
    Returns:
        str: 唯一ID
    """
    random_part = str(uuid.uuid4()).replace('-', '')[:length]
    if prefix:
        return f"{prefix}-{random_part}"
    return random_part


def format_timestamp(timestamp=None, format_str='%Y-%m-%d %H:%M:%S'):
    """
    格式化时间戳
    
    Args:
        timestamp: 时间戳（如果为None则使用当前时间）
        format_str: 时间格式字符串
    
    Returns:
        str: 格式化后的时间字符串
    """
    if timestamp is None:
        timestamp = time.time()
    return datetime.fromtimestamp(timestamp).strftime(format_str)


def serialize_to_json(data, pretty=False, ensure_ascii=False):
    """
    序列化数据为JSON字符串
    
    Args:
        data: 要序列化的数据
        pretty: 是否使用缩进美化输出
        ensure_ascii: 是否确保ASCII编码（False允许中文等非ASCII字符）
    
    Returns:
        str: JSON字符串
    
    Raises:
        ValueError: 序列化失败时抛出
    """
    try:
        if pretty:
            return json.dumps(data, indent=2, ensure_ascii=ensure_ascii)
        return json.dumps(data, ensure_ascii=ensure_ascii)
    except Exception as e:
        raise ValueError(f'JSON序列化失败: {str(e)}')


def deserialize_from_json(json_str):
    """
    从JSON字符串反序列化数据
    
    Args:
        json_str: JSON字符串
    
    Returns:
        any: 反序列化后的数据
    
    Raises:
        ValueError: 反序列化失败时抛出
    """
    if not json_str:
        raise ValueError('JSON字符串不能为空')
    
    try:
        return json.loads(json_str)
    except Exception as e:
        raise ValueError(f'JSON反序列化失败: {str(e)}')


def normalize_path(path):
    """
    标准化路径，处理不同操作系统的路径分隔符
    
    Args:
        path: 原始路径
    
    Returns:
        str: 标准化后的路径
    """
    import os
    return os.path.normpath(path)


def format_bytes(bytes_value):
    """
    将字节数格式化为人类可读的大小
    
    Args:
        bytes_value: 字节数
    
    Returns:
        str: 格式化后的大小字符串（如 '1.5 MB'）
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def flatten_dict(nested_dict, parent_key='', sep='_'):
    """
    展平嵌套字典
    
    Args:
        nested_dict: 嵌套字典
        parent_key: 父键
        sep: 键分隔符
    
    Returns:
        dict: 展平后的字典
    """
    items = []
    for k, v in nested_dict.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def merge_dicts(dict1, dict2, deep=True):
    """
    合并两个字典
    
    Args:
        dict1: 第一个字典（基础字典）
        dict2: 第二个字典（更新字典）
        deep: 是否深度合并（递归合并嵌套字典）
    
    Returns:
        dict: 合并后的字典
    """
    result = dict1.copy()
    
    if deep:
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_dicts(result[key], value, deep=True)
            else:
                result[key] = value
    else:
        result.update(dict2)
    
    return result


def sanitize_filename(filename):
    """
    清理文件名，移除或替换不允许的字符
    
    Args:
        filename: 原始文件名
    
    Returns:
        str: 清理后的文件名
    """
    import re
    # 移除或替换不允许的字符（保留字母数字、下划线、横线、点）
    safe_filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    # 确保文件名不为空
    if not safe_filename or safe_filename == '.':
        safe_filename = 'unnamed_file'
    # 去除开头和结尾的点和下划线
    return safe_filename.strip('._')


def create_pagination_metadata(page, page_size, total_items):
    """
    创建分页元数据
    
    Args:
        page: 当前页码（从1开始）
        page_size: 每页大小
        total_items: 总项目数
    
    Returns:
        dict: 分页元数据字典
    """
    total_pages = (total_items + page_size - 1) // page_size  # 向上取整
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        'page': page,
        'page_size': page_size,
        'total_items': total_items,
        'total_pages': total_pages,
        'has_next': has_next,
        'has_prev': has_prev,
        'next_page': page + 1 if has_next else None,
        'prev_page': page - 1 if has_prev else None
    }


def paginate_list(items, page=1, page_size=10):
    """
    对列表进行分页
    
    Args:
        items: 完整的项目列表
        page: 当前页码（从1开始）
        page_size: 每页大小
    
    Returns:
        tuple: (分页后的项目列表, 分页元数据)
    """
    # 参数验证
    page = max(1, int(page))
    page_size = max(1, min(int(page_size), 100))  # 限制最大页面大小
    
    # 计算偏移量
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    
    # 获取分页后的项目
    paginated_items = items[start_index:end_index]
    
    # 创建分页元数据
    pagination_metadata = create_pagination_metadata(page, page_size, len(items))
    
    return paginated_items, pagination_metadata