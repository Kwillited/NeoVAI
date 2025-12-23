import os
import sqlite3
from app.core.config import config_manager

# 获取数据库路径
user_data_dir = config_manager.get_user_data_dir()
db_path = os.path.join(user_data_dir, 'config', 'neovai.db')
print(f'DB path: {db_path}')
print(f'DB exists: {os.path.exists(db_path)}')

# 如果数据库存在，检查表结构
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print('\nChats table structure:')
    cursor.execute('PRAGMA table_info(chats)')
    chats_info = cursor.fetchall()
    for col in chats_info:
        print(col)
    
    # 检查是否有model列
    has_model_col = any(col[1] == 'model' for col in chats_info)
    print(f'\nHas model column: {has_model_col}')
    
    conn.close()