"""文件操作工具函数"""
import os
import shutil
from werkzeug.utils import secure_filename


def ensure_directory_exists(directory_path):
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory_path: 目录路径
    
    Returns:
        bool: 是否成功创建或已存在
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        print(f"创建目录失败: {e}")
        return False


def get_files_in_directory(directory_path, skip_hidden=True, skip_thumbs=True):
    """
    获取目录中的所有文件
    
    Args:
        directory_path: 目录路径
        skip_hidden: 是否跳过隐藏文件
        skip_thumbs: 是否跳过Thumbs.db文件
    
    Returns:
        list: 文件列表
    """
    files = []
    if not os.path.exists(directory_path):
        return files
    
    for file in os.listdir(directory_path):
        if os.path.isfile(os.path.join(directory_path, file)):
            if (skip_hidden and file.startswith('.')) or \
               (skip_thumbs and file == 'Thumbs.db'):
                continue
            files.append(file)
    return files


def get_directories(directory_path, skip_hidden=True, skip_thumbs=True):
    """
    获取目录中的所有子目录
    
    Args:
        directory_path: 目录路径
        skip_hidden: 是否跳过隐藏目录
        skip_thumbs: 是否跳过Thumbs.db目录
    
    Returns:
        list: 目录信息列表
    """
    ensure_directory_exists(directory_path)
    
    directories = []
    if not os.path.exists(directory_path):
        return directories
    
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isdir(item_path):
            if (skip_hidden and item.startswith('.')) or \
               (skip_thumbs and item == 'Thumbs.db'):
                continue
            directories.append({
                'name': item,
                'path': item_path
            })
    return directories


def secure_file_operation(filename, folder_name=None, base_dir=None, operation='check'):
    """
    安全的文件操作辅助函数
    
    Args:
        filename: 文件名
        folder_name: 文件夹名称
        base_dir: 基础目录路径
        operation: 操作类型 ('check', 'delete')
    
    Returns:
        dict: 操作结果
    
    Raises:
        ValueError: 参数验证失败时抛出
    """
    # 参数验证
    if not filename:
        raise ValueError('文件名不能为空')
    
    if not base_dir or not os.path.exists(base_dir):
        raise ValueError('基础目录不存在')
    
    # 安全验证文件名
    filename = secure_filename(filename)
    
    # 构建文件路径
    if folder_name:
        folder_name = secure_filename(folder_name)
        folder_path = os.path.join(base_dir, folder_name)
        file_path = os.path.join(folder_path, filename)
    else:
        file_path = os.path.join(base_dir, filename)
    
    # 检查文件是否存在
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise ValueError('文件不存在')
    
    if operation == 'delete':
        # 删除文件
        os.remove(file_path)
        return {
            'deleted_file': filename,
            'folder': folder_name,
            'message': f'文件 {filename} 已成功删除'
        }
    
    # 默认为检查操作，返回文件路径
    return {'file_path': file_path}


def search_files(directory_path, query, search_content=True):
    """
    在目录中搜索文件
    
    Args:
        directory_path: 要搜索的目录路径
        query: 搜索关键词
        search_content: 是否搜索文件内容（仅对文本文件）
    
    Returns:
        list: 搜索结果列表
    """
    if not query or not query.strip():
        raise ValueError('搜索关键词不能为空')
    
    results = []
    query = query.strip().lower()
    
    # 递归遍历目录中的所有文件
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.startswith('.') or file == 'Thumbs.db':
                continue
            
            file_path = os.path.join(root, file)
            
            # 至少检查文件名
            if query in file.lower():
                results.append({
                    'file': file,
                    'path': file_path,
                    'folder': os.path.relpath(root, directory_path)
                })
                continue
            
            # 如果启用内容搜索，尝试读取文本文件内容
            if search_content and file.lower().endswith(('.txt', '.md', '.csv')):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if query in content.lower():
                            results.append({
                                'file': file,
                                'path': file_path,
                                'folder': os.path.relpath(root, directory_path)
                            })
                except Exception as e:
                    print(f"读取文件 {file} 时出错: {e}")
    
    return results


def get_file_details(file_path):
    """
    获取文件详细信息
    
    Args:
        file_path: 文件路径
    
    Returns:
        dict: 文件信息字典
    
    Raises:
        ValueError: 文件不存在时抛出
    """
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise ValueError('文件不存在')
    
    # 获取文件详情
    file_stats = os.stat(file_path)
    file_name = os.path.basename(file_path)
    
    return {
        'id': file_name,
        'name': file_name,
        'path': file_path,
        'size': file_stats.st_size,
        'created_at': file_stats.st_ctime,
        'modified_at': file_stats.st_mtime,
        'folder': os.path.dirname(file_path)
    }


def delete_directory(directory_path):
    """
    删除目录及其所有内容
    
    Args:
        directory_path: 要删除的目录路径
    
    Returns:
        dict: 删除结果
    
    Raises:
        ValueError: 目录不存在或不是目录时抛出
    """
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        raise ValueError('目录不存在')
    
    # 删除目录及其所有内容
    shutil.rmtree(directory_path)
    
    return {
        'deleted_directory': os.path.basename(directory_path),
        'message': f'目录 {os.path.basename(directory_path)} 已成功删除'
    }