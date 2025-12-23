#!/usr/bin/env python3
"""
更新数据库模式的脚本
"""
import os
import sqlite3
from app.core.config import config_manager

# 获取数据库路径
def get_db_path():
    """获取数据库路径"""
    user_data_dir = config_manager.get_user_data_dir()
    return os.path.join(user_data_dir, 'config', 'neovai.db')

# 更新数据库模式
def update_db_schema():
    """
    更新数据库模式，添加缺少的列
    """
    db_path = get_db_path()
    print(f"📦 连接数据库: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.execute('PRAGMA foreign_keys = ON')
        cursor = conn.cursor()
        
        # 检查并添加icon_blob列到models表
        cursor.execute("PRAGMA table_info(models)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'icon_blob' not in columns:
            print("🔄 添加icon_blob列到models表...")
            cursor.execute("ALTER TABLE models ADD COLUMN icon_blob BLOB")
            print("✅ 成功添加icon_blob列")
        else:
            print("✅ icon_blob列已存在")
        
        conn.commit()
        conn.close()
        
        print("✅ 数据库模式更新完成")
        return True
    except Exception as e:
        print(f"❌ 更新数据库模式失败: {str(e)}")
        return False

# 主函数
if __name__ == "__main__":
    update_db_schema()