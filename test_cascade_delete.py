import os
import sqlite3

# 模拟数据库连接和操作
user_data_dir = os.path.expanduser('~') + '\AppData\Roaming\NeoVAI'
db_path = os.path.join(user_data_dir, 'config', 'neovai.db')

if os.path.exists(db_path):
    # 连接数据库并启用外键
    conn = sqlite3.connect(db_path)
    conn.execute('PRAGMA foreign_keys = ON')
    cursor = conn.cursor()
    
    # 插入测试数据
    print('插入测试数据...')
    cursor.execute("INSERT INTO chats (id, title, preview, created_at, updated_at) VALUES (?, ?, ?, ?, ?)", 
                  ('test_chat_123', '测试对话', '测试预览', '2025-01-01T00:00:00', '2025-01-01T00:00:00'))
    cursor.execute("INSERT INTO messages (id, chat_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)", 
                  ('test_msg_1', 'test_chat_123', 'user', '测试消息1', '2025-01-01T00:00:00'))
    cursor.execute("INSERT INTO messages (id, chat_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)", 
                  ('test_msg_2', 'test_chat_123', 'assistant', '测试回复1', '2025-01-01T00:00:00'))
    conn.commit()
    
    # 检查数据插入情况
    cursor.execute("SELECT COUNT(*) FROM chats WHERE id = 'test_chat_123'")
    chat_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM messages WHERE chat_id = 'test_chat_123'")
    msg_count = cursor.fetchone()[0]
    print(f'插入后 - 对话数: {chat_count}, 消息数: {msg_count}')
    
    # 删除对话
    print('删除对话...')
    cursor.execute("DELETE FROM chats WHERE id = 'test_chat_123'")
    conn.commit()
    
    # 检查级联删除结果
    cursor.execute("SELECT COUNT(*) FROM chats WHERE id = 'test_chat_123'")
    chat_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM messages WHERE chat_id = 'test_chat_123'")
    msg_count = cursor.fetchone()[0]
    print(f'删除后 - 对话数: {chat_count}, 消息数: {msg_count}')
    
    if chat_count == 0 and msg_count == 0:
        print('✅ 级联删除测试成功！')
    else:
        print('❌ 级联删除测试失败！')