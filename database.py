"""
Step 3: 数据库模块
验证方法: 运行 python database.py 应该无报错
"""

import sqlite3
from datetime import datetime
from config import DATABASE

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库表"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 学生表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            grade TEXT,
            class_name TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 会话表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            ended_at DATETIME,
            summary TEXT,
            risk_level TEXT DEFAULT 'low',
            status TEXT DEFAULT 'active',
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)
    
    # 消息表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT,
            audio_url TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)
    
    # 预警表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            sensitive_word TEXT,
            notified BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id),
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)
    
    # 系统配置表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")

# ===== 学生操作 =====
def add_student(username, password_hash, name, grade="", class_name=""):
    """添加学生"""
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO students (username, password_hash, name, grade, class_name)
            VALUES (?, ?, ?, ?, ?)
        """, (username, password_hash, name, grade, class_name))
        conn.commit()
        student_id = cursor.lastrowid
        conn.close()
        return student_id
    except sqlite3.IntegrityError:
        conn.close()
        return None  # 用户名已存在

def get_student_by_username(username):
    """根据用户名获取学生"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE username = ?", (username,))
    student = cursor.fetchone()
    conn.close()
    return dict(student) if student else None

def get_all_students():
    """获取所有学生"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students ORDER BY created_at DESC")
    students = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return students

# ===== 会话操作 =====
def create_session(student_id):
    """创建新会话"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sessions (student_id, started_at)
        VALUES (?, ?)
    """, (student_id, datetime.now().isoformat()))
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    return session_id

def end_session(session_id, summary, risk_level):
    """结束会话"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE sessions 
        SET ended_at = ?, summary = ?, risk_level = ?, status = 'ended'
        WHERE id = ?
    """, (datetime.now().isoformat(), summary, risk_level, session_id))
    conn.commit()
    conn.close()

def get_session(session_id):
    """获取会话"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    session = cursor.fetchone()
    conn.close()
    return dict(session) if session else None

def get_student_sessions(student_id, limit=10):
    """获取学生的会话历史"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM sessions 
        WHERE student_id = ?
        ORDER BY started_at DESC
        LIMIT ?
    """, (student_id, limit))
    sessions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return sessions

# ===== 消息操作 =====
def add_message(session_id, role, content, audio_url=None):
    """添加消息"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (session_id, role, content, audio_url, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, role, content, audio_url, datetime.now().isoformat()))
    conn.commit()
    message_id = cursor.lastrowid
    conn.close()
    return message_id

def get_session_messages(session_id):
    """获取会话的所有消息"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM messages 
        WHERE session_id = ?
        ORDER BY created_at ASC
    """, (session_id,))
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return messages

# ===== 预警操作 =====
def create_alert(session_id, student_id, risk_level, sensitive_word=""):
    """创建预警"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alerts (session_id, student_id, risk_level, sensitive_word, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, student_id, risk_level, sensitive_word, datetime.now().isoformat()))
    conn.commit()
    alert_id = cursor.lastrowid
    conn.close()
    return alert_id

def get_pending_alerts():
    """获取未处理的预警"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, s.name as student_name, s.grade, s.class_name
        FROM alerts a
        JOIN students s ON a.student_id = s.id
        WHERE a.notified = FALSE
        ORDER BY a.created_at DESC
    """)
    alerts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return alerts

def mark_alert_notified(alert_id):
    """标记预警已通知"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE alerts SET notified = TRUE WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()

# ===== 配置操作 =====
def set_config(key, value):
    """设置配置"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO config (key, value)
        VALUES (?, ?)
    """, (key, value))
    conn.commit()
    conn.close()

def get_config(key, default=None):
    """获取配置"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row['value'] if row else default

# 初始化数据库
if __name__ == "__main__":
    init_db()
    
    # 验证测试
    print("\n=== 验证测试 ===")
    
    # 测试添加学生
    sid = add_student("test001", "hash123", "张三", "三年级", "1班")
    print(f"✅ 添加学生: ID={sid}")
    
    # 测试获取学生
    student = get_student_by_username("test001")
    print(f"✅ 查询学生: {student['name']}")
    
    # 测试创建会话
    sess_id = create_session(student['id'])
    print(f"✅ 创建会话: ID={sess_id}")
    
    # 测试添加消息
    msg_id = add_message(sess_id, "user", "我心情不好")
    print(f"✅ 添加消息: ID={msg_id}")
    
    # 测试创建预警
    alert_id = create_alert(sess_id, student['id'], "medium", "心情不好")
    print(f"✅ 创建预警: ID={alert_id}")
    
    # 测试获取未处理预警
    alerts = get_pending_alerts()
    print(f"✅ 未处理预警数: {len(alerts)}")
    
    print("\n✅ 数据库模块验证通过！")