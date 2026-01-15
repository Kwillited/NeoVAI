"""数据管理模块"""
import json
import os
import sqlite3
from datetime import datetime
from app.core.config import config_manager

# 1. 初始化内存数据库（全局唯一）
db = {
    'chats': [],  # 存储所有对话
    'models': [],  # 存储所有模型信息，后续从SQLite加载
    'settings': {}
}

# 脏标记，用于跟踪哪些数据需要保存
dirty_flags = {
    'chats': False,
    'models': False,
    'settings': False
}

# 加载默认设置
for key, value in config_manager._config.items():
    db['settings'][key] = value

# 获取数据库连接（线程安全）
def get_db_connection():
    """获取数据库连接（为每个线程创建独立连接）"""
    user_data_dir = ensure_data_dir()
    # 将数据库文件名从neovai.db改为chato.db
    db_path = os.path.join(user_data_dir, 'config', 'chato.db')
    # 创建新的数据库连接
    conn = sqlite3.connect(db_path)
    # 启用外键约束
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

# --------------------------
# 2. 数据目录管理（确保data目录存在）
# --------------------------
def ensure_data_dir():
    """确保数据目录存在"""
    user_data_dir = config_manager.get_user_data_dir()
    return user_data_dir

# --------------------------
# 3. SQLite数据库初始化
# --------------------------
def init_db():
    """初始化SQLite数据库，创建表结构"""
    user_data_dir = ensure_data_dir()
    # 将数据库文件名从neovai.db改为chato.db
    db_path = os.path.join(user_data_dir, 'config', 'chato.db')
    
    # 确保config目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    # 启用外键约束
    conn.execute('PRAGMA foreign_keys = ON')
    cursor = conn.cursor()
    
    # 创建模型表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS models (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        configured BOOLEAN DEFAULT FALSE,
        enabled BOOLEAN DEFAULT FALSE,
        icon_class TEXT,
        icon_bg TEXT,
        icon_color TEXT,
        icon_url TEXT,
        icon_blob BLOB
    )
    ''')
    
    # 创建模型版本表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS model_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_id INTEGER NOT NULL,
        version_name TEXT NOT NULL,
        custom_name TEXT,
        api_key TEXT,
        api_base_url TEXT,
        streaming_config BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (model_id) REFERENCES models (id) ON DELETE CASCADE,
        UNIQUE(model_id, version_name)
    )
    ''')
    
    # 创建对话表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chats (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        preview TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    ''')
    
    # 创建消息表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        chat_id TEXT NOT NULL,
        role TEXT NOT NULL,
        actual_content TEXT NOT NULL,
        thinking TEXT,
        created_at TEXT NOT NULL,
        model TEXT,
        FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
    )
    ''')
    
    # 创建设置表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ SQLite数据库初始化成功，数据库文件: {db_path}")

# --------------------------
# 4. 数据加载（从SQLite数据库到内存DB）
# --------------------------
def load_chats_from_db():
    """从SQLite数据库加载对话数据"""
    global db
    
    # 清空内存中的对话数据
    db['chats'] = []
    
    try:
        # 获取数据库连接
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取所有对话
        cursor.execute("SELECT * FROM chats")
        chats = cursor.fetchall()
        
        for chat_row in chats:
            # 处理可能的字段缺失情况
            chat_id = chat_row[0]
            title = chat_row[1] if len(chat_row) > 1 else '未命名对话'
            preview = chat_row[2] if len(chat_row) > 2 else ''
            created_at = chat_row[3] if len(chat_row) > 3 else datetime.now().isoformat()
            updated_at = chat_row[4] if len(chat_row) > 4 else datetime.now().isoformat()
            
            # 获取对话的所有消息
            cursor.execute("SELECT * FROM messages WHERE chat_id = ? ORDER BY created_at", (chat_id,))
            messages = cursor.fetchall()
            
            # 构建消息列表
            message_list = []
            for msg_row in messages:
                msg_id = msg_row[0]
                role = msg_row[2] if len(msg_row) > 2 else 'user'
                actual_content = msg_row[3] if len(msg_row) > 3 else ''
                thinking = msg_row[4] if len(msg_row) > 4 else None
                msg_created_at = msg_row[5] if len(msg_row) > 5 else datetime.now().isoformat()
                model = msg_row[6] if len(msg_row) > 6 else None
                
                message_list.append({
                    'id': msg_id,
                    'role': role,
                    'content': actual_content,
                    'thinking': thinking,
                    'createdAt': msg_created_at,
                    'model': model
                })
            
            # 添加对话到内存数据库
            db['chats'].append({
                'id': chat_id,
                'title': title,
                'preview': preview,
                'createdAt': created_at,
                'updatedAt': updated_at,
                'messages': message_list
            })
        
        # 关闭数据库连接
        conn.close()
        
        print(f"✅ 从SQLite数据库加载了 {len(db['chats'])} 个对话")
        return len(db['chats']) > 0
    except Exception as e:
        print(f"❌ 从SQLite数据库加载对话数据失败: {str(e)}")
        return False



def load_data():
    """加载数据"""
    global db
    user_data_dir = ensure_data_dir()  # 先确保目录存在
    
    try:
        # 初始化数据库
        init_db()
        
        # 获取数据库连接
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查模型表是否为空
        cursor.execute("SELECT COUNT(*) FROM models")
        if cursor.fetchone()[0] == 0:
            # 数据库为空，插入默认模型数据
            insert_default_models()
        else:
            # 从SQLite加载模型数据
            load_models_from_db()
        
        conn.close()
        
        # 从SQLite加载对话数据
        load_chats_from_db()
        
        # 从SQLite加载设置数据
        load_settings_from_db()
        
        print("✅ 所有数据加载成功")
    except Exception as e:
        print(f"❌ 加载数据时出错: {str(e)}")

# 插入默认模型数据
def insert_default_models():
    """插入默认模型数据到SQLite数据库"""
    print("🔄 正在插入默认模型数据...")
    
    # 默认模型列表
    default_models = [
        {
            'name': 'OpenAI',
            'description': 'OpenAI的AI模型，性价比高',
            'configured': False,
            'enabled': False,
            'icon_class': 'fa-comment-o',
            'icon_bg': 'bg-blue-100',
            'icon_color': 'text-blue-500',
            'icon_url': '/api/models/icons/OpenAI.png',
            'versions': []
        },
        {
            'name': 'Anthropic',
            'description': 'Anthropic的Claude模型',
            'configured': False,
            'enabled': False,
            'icon_class': 'fa-comments',
            'icon_bg': 'bg-purple-100',
            'icon_color': 'text-purple-600',
            'icon_url': '/api/models/icons/Anthropic.png',
            'versions': []
        },
        {
            'name': 'Ollama',
            'description': '本地运行的Ollama模型',
            'configured': False,
            'enabled': False,
            'icon_class': 'fa-server',
            'icon_bg': 'bg-green-100',
            'icon_color': 'text-green-600',
            'icon_url': '/api/models/icons/Ollama.png',
            'versions': []
        },
        {
            'name': 'GitHubModel',
            'description': 'GitHub的AI模型',
            'configured': False,
            'enabled': False,
            'icon_class': 'fa-github',
            'icon_bg': 'bg-gray-100',
            'icon_color': 'text-gray-600',
            'versions': []
        },
        {
            'name': 'Deepseek',
            'description': '深度求索的Deepseek模型',
            'configured': False,
            'enabled': False,
            'icon_class': 'fa-code',
            'icon_bg': 'bg-orange-100',
            'icon_color': 'text-orange-600',
            'icon_url': '/api/models/icons/Deepseek.png',
            'versions': []
        },
        {
            'name': 'Doubao',
            'description': '字节跳动的豆包模型',
            'configured': False,
            'enabled': False,
            'icon_class': 'fa-robot',
            'icon_bg': 'bg-red-100',
            'icon_color': 'text-red-600',
            'icon_url': '/api/models/icons/Doubao.png',
            'versions': []
        },
        {
            'name': 'GoogleAI',
            'description': 'Google的AI模型',
            'configured': False,
            'enabled': False,
            'icon_class': 'fa-google',
            'icon_bg': 'bg-blue-100',
            'icon_color': 'text-blue-600',
            'icon_url': '/api/models/icons/GoogleAI.png',
            'versions': []
        },
        {
            'name': 'Huggingface',
            'description': 'Hugging Face的开源模型',
            'configured': False,
            'enabled': False,
            'icon_class': 'fa-hug',
            'icon_bg': 'bg-blue-100',
            'icon_color': 'text-blue-600',
            'icon_url': '/api/models/icons/Huggingface.png',
            'versions': []
        },
        {
            'name': 'Qwen',
            'description': '阿里巴巴的通义千问模型',
            'configured': False,
            'enabled': False,
            'icon_class': 'fa-comment-alt',
            'icon_bg': 'bg-orange-100',
            'icon_color': 'text-orange-600',
            'icon_url': '/api/models/icons/Qwen.png',
            'versions': []
        },
        {
            'name': '文心一言',
            'description': '百度的文心一言模型',
            'configured': False,
            'enabled': False,
            'icon_class': 'fa-comment-dots',
            'icon_bg': 'bg-red-100',
            'icon_color': 'text-red-600',
            'icon_url': '/api/models/icons/文心一言.png',
            'versions': []
        }
    ]
    
    # 获取数据库连接
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 将模型数据插入到SQLite数据库
    for model in default_models:
        # 插入模型
        cursor.execute('''
        INSERT OR REPLACE INTO models (name, description, configured, enabled, icon_class, icon_bg, icon_color, icon_url, icon_blob)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            model['name'],
            model['description'],
            model['configured'],
            model['enabled'],
            model['icon_class'],
            model['icon_bg'],
            model['icon_color'],
            model.get('icon_url', ''),
            model.get('icon_blob', None)
        ))
        
        # 获取模型ID
        model_id = cursor.lastrowid
        
        # 插入模型版本
        for version in model.get('versions', []):
            cursor.execute('''
            INSERT INTO model_versions (model_id, version_name, custom_name, api_key, api_base_url, streaming_config)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                model_id,
                version['version_name'],
                version.get('custom_name', ''),
                version.get('api_key', ''),
                version.get('api_base_url', ''),
                version.get('streaming_config', False)
            ))
    
    conn.commit()
    conn.close()
    print("✅ 默认模型数据插入完成")
    
    # 从数据库加载数据到内存
    load_models_from_db()

# 从SQLite数据库加载模型数据到内存
def load_models_from_db():
    """从SQLite数据库加载模型数据到内存"""
    global db
    
    # 清空内存中的模型数据
    db['models'] = []
    
    try:
        # 获取数据库连接
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取所有模型
        cursor.execute("SELECT * FROM models")
        models = cursor.fetchall()
        
        for model_row in models:
            # 处理可能的字段缺失，确保icon_blob字段被正确读取
            if len(model_row) == 9:
                model_id, name, description, configured, enabled, icon_class, icon_bg, icon_color, icon_url = model_row
                icon_blob = None
            elif len(model_row) >= 10:
                model_id, name, description, configured, enabled, icon_class, icon_bg, icon_color, icon_url, icon_blob = model_row
            
            # 获取模型的所有版本
            cursor.execute("SELECT * FROM model_versions WHERE model_id = ?", (model_id,))
            versions = cursor.fetchall()
            
            # 构建版本列表
            version_list = []
            for version_row in versions:
                _, _, version_name, custom_name, api_key, api_base_url, streaming_config = version_row
                version_list.append({
                    'version_name': version_name,
                    'custom_name': custom_name,
                    'api_key': api_key,
                    'api_base_url': api_base_url,
                    'streaming_config': streaming_config
                })
            
            # 添加模型到内存数据库
            db['models'].append({
                'name': name,
                'description': description,
                'configured': bool(configured),
                'enabled': bool(enabled),
                'icon_class': icon_class,
                'icon_bg': icon_bg,
                'icon_color': icon_color,
                'icon_url': icon_url,
                'icon_blob': icon_blob,
                'versions': version_list
            })
        
        conn.close()
        print(f"✅ 从SQLite数据库加载了 {len(db['models'])} 个模型")
    except Exception as e:
        print(f"❌ 从SQLite数据库加载模型数据失败: {str(e)}")

# 从SQLite数据库加载设置数据到内存
def load_settings_from_db():
    """从SQLite数据库加载设置数据到内存"""
    global db
    
    try:
        # 获取数据库连接
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取所有设置
        cursor.execute("SELECT * FROM settings")
        settings = cursor.fetchall()
        
        # 加载设置到内存
        for setting in settings:
            key, value = setting
            try:
                # 尝试将JSON字符串转换为字典
                setting_value = json.loads(value)
                db['settings'][key] = setting_value
            except json.JSONDecodeError:
                # 如果不是JSON格式，直接保存为字符串
                db['settings'][key] = value
        
        conn.close()
        print(f"✅ 从SQLite数据库加载了 {len(settings)} 个设置")
    except Exception as e:
        print(f"❌ 从SQLite数据库加载设置数据失败: {str(e)}")
        # 保持现有设置不变

# 将设置数据保存到SQLite数据库
def save_settings_to_db(conn):
    """将设置数据保存到SQLite数据库"""
    global db
    
    try:
        cursor = conn.cursor()
        
        # 保存所有设置
        for key, value in db['settings'].items():
            try:
                # 将设置值转换为JSON字符串
                value_json = json.dumps(value)
                cursor.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                    (key, value_json)
                )
            except Exception as e:
                print(f"❌ 保存设置 '{key}' 失败: {str(e)}")
        
        print("✅ 设置数据已保存到SQLite数据库")
    except Exception as e:
        print(f"❌ 保存设置数据到SQLite失败: {str(e)}")
        raise

# --------------------------
# 5. 数据保存（从内存DB到SQLite和JSON文件）
# --------------------------
def save_chats_to_db(conn):
    """将对话数据保存到SQLite数据库"""
    global db
    
    try:
        cursor = conn.cursor()
        
        # 使用INSERT OR REPLACE保存对话和消息，只更新或插入需要的记录
        for chat in db['chats']:
            chat_id = chat['id']
            title = chat['title']
            preview = chat.get('preview', '')
            created_at = chat['createdAt']
            updated_at = chat['updatedAt']
            
            # 使用INSERT OR REPLACE插入或更新对话
            cursor.execute('''
            INSERT OR REPLACE INTO chats (id, title, preview, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ''', (chat_id, title, preview, created_at, updated_at))
            
            # 保存对话中的消息
            for msg in chat.get('messages', []):
                msg_id = msg['id']
                role = msg['role']
                content = msg['content']
                thinking = msg.get('thinking', None)
                # 确保createdAt有值，即使键存在但值为None也使用默认值
                msg_created_at = msg.get('createdAt') or datetime.now().isoformat()
                model = msg.get('model', None)
                
                cursor.execute('''
                INSERT OR REPLACE INTO messages (id, chat_id, role, actual_content, thinking, created_at, model)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (msg_id, chat_id, role, content, thinking, msg_created_at, model))
        
        print("✅ 对话数据已保存到SQLite数据库")
    except Exception as e:
        print(f"❌ 保存对话数据到SQLite失败: {str(e)}")
        raise

def set_dirty_flag(data_type, is_dirty=True):
    """设置数据脏标记
    
    参数:
        data_type: 数据类型，可选值: 'chats', 'models', 'settings'
        is_dirty: 是否为脏数据，默认为True
    """
    if data_type in dirty_flags:
        dirty_flags[data_type] = is_dirty


def save_data():
    """保存数据到SQLite数据库，只保存有脏标记的数据"""
    conn = None
    try:
        # 使用单个数据库连接执行所有保存操作，避免数据库锁定
        conn = get_db_connection()
        
        # 记录需要保存的数据类型
        saved_types = []
        
        # 只保存有脏标记的数据
        if dirty_flags['chats']:
            save_chats_to_db(conn)
            saved_types.append('chats')
            dirty_flags['chats'] = False
        
        if dirty_flags['models']:
            save_models_to_db(conn)
            saved_types.append('models')
            dirty_flags['models'] = False
        
        if dirty_flags['settings']:
            save_settings_to_db(conn)
            saved_types.append('settings')
            dirty_flags['settings'] = False
        
        # 提交事务
        conn.commit()
        
        if saved_types:
            print(f"✅ 数据已保存到SQLite: {', '.join(saved_types)}")
        else:
            print("ℹ️  没有数据需要保存")
            
    except Exception as e:
        print(f"❌ 保存数据时出错: {str(e)}")
        # 回滚事务
        if conn:
            conn.rollback()
    finally:
        # 确保连接关闭
        if conn:
            conn.close()

# 将模型数据保存到SQLite数据库
def save_models_to_db(conn):
    """将模型数据保存到SQLite数据库"""
    try:
        cursor = conn.cursor()
        
        for model in db['models']:
            # 使用INSERT OR REPLACE插入或更新模型
            cursor.execute('''
            INSERT OR REPLACE INTO models (name, description, configured, enabled, icon_class, icon_bg, icon_color, icon_url, icon_blob)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                model['name'],
                model['description'],
                model['configured'],
                model['enabled'],
                model['icon_class'],
                model['icon_bg'],
                model['icon_color'],
                model.get('icon_url', ''),
                model.get('icon_blob', None)
            ))
            
            # 获取模型ID
            cursor.execute("SELECT id FROM models WHERE name = ?", (model['name'],))
            model_id = cursor.fetchone()[0]
            
            # 获取现有版本名称列表
            cursor.execute("SELECT version_name FROM model_versions WHERE model_id = ?", (model_id,))
            existing_versions = set(row[0] for row in cursor.fetchall())
            
            # 要保存的版本名称集合
            new_versions = set(version['version_name'] for version in model.get('versions', []))
            
            # 删除不再存在的版本
            versions_to_delete = existing_versions - new_versions
            for version_name in versions_to_delete:
                cursor.execute("DELETE FROM model_versions WHERE model_id = ? AND version_name = ?", (model_id, version_name))
            
            # 插入或更新版本
            for version in model.get('versions', []):
                cursor.execute('''
                INSERT OR REPLACE INTO model_versions (model_id, version_name, custom_name, api_key, api_base_url, streaming_config)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    model_id,
                    version['version_name'],
                    version.get('custom_name', ''),
                    version.get('api_key', ''),
                    version.get('api_base_url', ''),
                    version.get('streaming_config', False)
                ))
        
        print("✅ 模型数据已保存到SQLite数据库")
    except Exception as e:
        print(f"❌ 保存模型数据到SQLite失败: {str(e)}")
        raise