"""
心灵伙伴 - API接口模块
"""
import os
import sys

# PyInstaller兼容：获取正确的路径
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import hashlib

import database as db
from ai_handler import AIHandler
from config import ADMIN_USERNAME, ADMIN_PASSWORD

# ===== 初始化 =====
app = FastAPI(title="心灵伙伴 API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai = AIHandler()

# 静态文件目录
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
ADMIN_DIR = os.path.join(BASE_DIR, "admin")

def safe_file_response(path):
    """安全的文件响应"""
    if os.path.exists(path):
        return FileResponse(path)
    return HTTPException(status_code=404, detail=f"File not found: {path}")

# ===== 静态文件服务 =====
@app.get("/")
def root():
    return safe_file_response(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/admin/")
@app.get("/admin")
def admin_page():
    return safe_file_response(os.path.join(ADMIN_DIR, "index.html"))
    return HTTPException(status_code=404, detail="Not Found")

# 简单token存储（生产环境应用JWT）
TOKEN_STUDENT = {}  # token -> student_id
TOKEN_ADMIN = {}    # token -> True

def hash_password(pwd: str) -> str:
    return hashlib.md5(pwd.encode()).hexdigest()

# ===== 数据模型 =====

class StudentLogin(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    session_id: Optional[int] = None
    audio_data: Optional[str] = None
    text: Optional[str] = None

class AdminLogin(BaseModel):
    username: str
    password: str

class StudentCreate(BaseModel):
    username: str
    password: str
    name: str
    grade: str
    class_name: str

class AlertUpdate(BaseModel):
    handled: bool

class ConfigUpdate(BaseModel):
    email_host: Optional[str] = None
    email_port: Optional[int] = None
    email_user: Optional[str] = None
    email_password: Optional[str] = None
    alert_recipients: Optional[List[str]] = None

# ===== 辅助函数 =====

def create_student_token(student_id: int) -> str:
    token = f"student_{student_id}_{datetime.now().timestamp()}"
    TOKEN_STUDENT[token] = student_id
    return token

def get_student_from_token(token: str) -> Optional[dict]:
    if token not in TOKEN_STUDENT:
        return None
    student_id = TOKEN_STUDENT[token]
    return db.get_student_by_username(None, student_id)

def verify_admin_token(token: str) -> bool:
    return token in TOKEN_ADMIN

# ===== 学生端接口 =====

@app.post("/api/student/login")
def student_login(data: StudentLogin):
    """学生登录"""
    student = db.get_student_by_username(data.username)
    if not student or student['password_hash'] != hash_password(data.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    token = create_student_token(student['id'])
    return {
        "code": 0,
        "data": {
            "token": token,
            "student": {
                "id": student["id"],
                "name": student["name"],
                "grade": student["grade"],
                "class_name": student["class_name"]
            }
        }
    }

@app.post("/api/student/logout")
def student_logout(token: str = None):
    """学生登出"""
    if token and token in TOKEN_STUDENT:
        del TOKEN_STUDENT[token]
    return {"code": 0, "message": "登出成功"}

@app.post("/api/chat")
def chat(data: ChatRequest, token: str = None):
    """对话接口"""
    if not token or token not in TOKEN_STUDENT:
        raise HTTPException(status_code=401, detail="未登录")
    
    student_id = TOKEN_STUDENT[token]
    
    # 处理输入
    if data.audio_data:
        import base64
        audio_bytes = base64.b64decode(data.audio_data)
        user_text = ai.speech_to_text(audio_bytes)
    elif data.text:
        user_text = data.text
    else:
        raise HTTPException(status_code=400, detail="请提供audio_data或text")
    
    # 危机检测
    crisis = ai.detect_crisis(user_text)
    
    # 创建/获取会话
    if not data.session_id:
        session_id = db.create_session(student_id)
    else:
        session_id = data.session_id
    
    # 生成回复
    if crisis["triggered"]:
        reply_text = ai.crisis_intervention(user_text, crisis["words"])
        risk_level = crisis["level"]
    else:
        reply_text = ai.chat(f"session_{session_id}", user_text)
        risk_level = "low"
    
    # 存储消息
    db.add_message(session_id, "user", user_text)
    db.add_message(session_id, "assistant", reply_text)
    
    # 更新风险等级
    if risk_level != "low":
        db.end_session(session_id, "", risk_level)
        db.create_alert(session_id, student_id, risk_level)
    
    return {
        "code": 0,
        "data": {
            "session_id": session_id,
            "reply": reply_text,
            "risk_level": risk_level,
            "crisis_triggered": crisis["triggered"]
        }
    }

@app.get("/api/chat/history")
def chat_history(session_id: int, token: str = None):
    """获取对话历史"""
    if not token or token not in TOKEN_STUDENT:
        raise HTTPException(status_code=401, detail="未登录")
    
    messages = db.get_session_messages(session_id)
    return {"code": 0, "data": {"messages": messages}}

# ===== 管理端接口 =====

@app.post("/api/admin/login")
def admin_login(data: AdminLogin):
    """管理员登录"""
    if data.username != ADMIN_USERNAME or data.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = "admin_token_123"
    TOKEN_ADMIN[token] = True
    return {"code": 0, "data": {"token": token}}

@app.post("/api/admin/student")
def create_student(data: StudentCreate, token: str = None):
    """录入学生"""
    if not verify_admin_token(token):
        raise HTTPException(status_code=401, detail="未授权")
    
    student_id = db.add_student(
        username=data.username,
        password_hash=hash_password(data.password),
        name=data.name,
        grade=data.grade,
        class_name=data.class_name
    )
    
    if student_id is None:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    return {"code": 0, "data": {"student_id": student_id}}

@app.get("/api/admin/students")
def list_students(token: str = None):
    """学生列表"""
    if not verify_admin_token(token):
        raise HTTPException(status_code=401, detail="未授权")
    
    students = db.get_all_students()
    return {"code": 0, "data": {"students": students}}

@app.get("/api/admin/sessions")
def list_sessions(student_id: Optional[int] = None, token: str = None):
    """会话列表"""
    if not verify_admin_token(token):
        raise HTTPException(status_code=401, detail="未授权")
    
    if student_id:
        sessions = db.get_student_sessions(student_id)
    else:
        sessions = []
    
    return {"code": 0, "data": {"sessions": sessions}}

@app.get("/api/admin/session/{session_id}")
def get_session(session_id: int, token: str = None):
    """会话详情"""
    if not verify_admin_token(token):
        raise HTTPException(status_code=401, detail="未授权")
    
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    messages = db.get_session_messages(session_id)
    return {"code": 0, "data": {"session": session, "messages": messages}}

@app.get("/api/admin/profile/{student_id}")
def get_profile(student_id: int, token: str = None):
    """心理档案"""
    if not verify_admin_token(token):
        raise HTTPException(status_code=401, detail="未授权")
    
    sessions = db.get_student_sessions(student_id)
    alerts = db.get_pending_alerts()
    
    # 过滤该学生的预警
    student_alerts = [a for a in alerts if a['student_id'] == student_id]
    
    risk_stats = {"high": 0, "medium": 0, "low": 0}
    for s in sessions:
        level = s.get("risk_level", "low")
        if level in risk_stats:
            risk_stats[level] += 1
    
    return {
        "code": 0,
        "data": {
            "sessions": sessions,
            "alerts": student_alerts,
            "risk_stats": risk_stats
        }
    }

@app.get("/api/admin/alerts")
def list_alerts(token: str = None):
    """预警列表"""
    if not verify_admin_token(token):
        raise HTTPException(status_code=401, detail="未授权")
    
    alerts = db.get_pending_alerts()
    return {"code": 0, "data": {"alerts": alerts}}

@app.patch("/api/admin/alert/{alert_id}")
def update_alert(alert_id: int, data: AlertUpdate, token: str = None):
    """标记预警已处理"""
    if not verify_admin_token(token):
        raise HTTPException(status_code=401, detail="未授权")
    
    if data.handled:
        db.mark_alert_notified(alert_id)
    return {"code": 0, "message": "更新成功"}

@app.get("/api/admin/config")
def get_config(token: str = None):
    """获取配置"""
    if not verify_admin_token(token):
        raise HTTPException(status_code=401, detail="未授权")
    
    config = {
        "email_host": db.get_config("email_host", ""),
        "email_port": int(db.get_config("email_port", "587") or "587"),
        "email_user": db.get_config("email_user", ""),
        "email_password": db.get_config("email_password", ""),
    }
    return {"code": 0, "data": config}

@app.patch("/api/admin/config")
def update_config(data: ConfigUpdate, token: str = None):
    """更新配置"""
    if not verify_admin_token(token):
        raise HTTPException(status_code=401, detail="未授权")
    
    if data.email_host is not None:
        db.set_config("email_host", data.email_host)
    if data.email_port is not None:
        db.set_config("email_port", str(data.email_port))
    if data.email_user is not None:
        db.set_config("email_user", data.email_user)
    if data.email_password is not None:
        db.set_config("email_password", data.email_password)
    
    return {"code": 0, "message": "配置已更新"}

# ===== 健康检查 =====

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/")
def root():
    return {"message": "心灵伙伴 API v1.0.0"}
