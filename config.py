"""
心灵伙伴 - 学生心理语音对话系统
配置文件
"""
import os
from dotenv import load_dotenv

load_dotenv()

# MiniMax API 配置（请在 .env 文件中设置，不要直接写在代码里）
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_API_URL = "https://api.minimax.chat/v1"

# 服务器配置
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8080))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# 数据库
DATABASE = os.getenv("DATABASE", "mental_health.db")

# 邮件配置
SMTP_SERVER = os.getenv("SMTP_SERVER", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# 敏感词列表
SENSITIVE_WORDS = [
    "自杀", "轻生", "不想活", "活着没意思", "死了算了",
    "想死", "不想活了", "人生没意义", "自我了断", "结束生命"
]

# 风险等级阈值
RISK_THRESHOLDS = {
    "high": 5,      # 敏感词出现5次以上
    "medium": 2,    # 敏感词出现2-4次
    "low": 0        # 其他
}

# AI 模型模式
AI_MODE = os.getenv("AI_MODE", "minimax")  # minimax / local