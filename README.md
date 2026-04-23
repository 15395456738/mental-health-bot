# 心灵伙伴 - 学生心理语音对话系统

面向小学生的AI心理陪伴对话系统，支持纯语音交互、危机检测与预警、心理档案管理。

---

## 功能特性

### 学生端
- ✅ 账号密码登录
- ✅ 文字/语音对话
- ✅ 危机敏感词检测
- ✅ AI温暖心理陪伴
- ✅ 独立会话存储

### 管理端
- ✅ 学生信息管理（录入/查看）
- ✅ 预警中心（高/中/低风险）
- ✅ 对话记录查看
- ✅ 学生心理档案
- ✅ 邮件推送配置

### 危机干预
- 🚨 自杀/轻生等敏感词自动检测
- 🚨 AI先进行心理开导（不给技术建议）
- 🚨 高/中风险自动邮件通知老师

---

## 快速启动

### 1. 安装依赖

```bash
pip install fastapi uvicorn requests python-dotenv
```

### 2. 启动API服务

```bash
cd mental-health-bot
python3 -m uvicorn api:app --host 0.0.0.0 --port 8000
```

### 3. 启动前端（可选）

```bash
# 学生端
cd frontend
python3 -m http.server 8080

# 管理端
cd admin
python3 -m http.server 8081
```

### 4. 访问地址

| 服务 | 地址 |
|------|------|
| API服务 | http://localhost:8000 |
| API文档 | http://localhost:8000/docs |
| 学生端 | http://localhost:8080 |
| 管理端 | http://localhost:8081 |

---

## 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |

**注意**：学生账号需要通过管理端录入。

---

## 项目结构

```
mental-health-bot/
├── SPEC.md              # 需求规格文档
├── README.md            # 本文档
├── config.py            # 配置文件
├── requirements.txt     # Python依赖
├── database.py          # 数据库模块
├── ai_handler.py        # AI对话处理
├── api.py               # FastAPI接口
├── email_sender.py      # 邮件推送
├── frontend/
│   └── index.html       # 学生端界面
├── admin/
│   └── index.html       # 管理后台
└── mental_health.db     # SQLite数据库（自动生成）
```

---

## 配置说明

### 配置文件：config.py

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| MINIMAX_API_KEY | MiniMax API密钥 | 测试Key |
| ADMIN_USERNAME | 管理员用户名 | admin |
| ADMIN_PASSWORD | 管理员密码 | admin123 |
| SMTP_SERVER | 邮件SMTP服务器 | 空 |
| SMTP_PORT | 邮件端口 | 587 |
| SMTP_USERNAME | 邮件账号 | 空 |
| SMTP_PASSWORD | 邮件密码 | 空 |
| ADMIN_EMAIL | 管理员邮箱（预警收件人） | 空 |

### 敏感词配置

在 `config.py` 的 `SENSITIVE_WORDS` 列表中配置，默认包含：
- 自杀、轻生、不想活、活着没意思、死了算了、想死、不想活了、人生没意义、自我了断、结束生命

---

## API接口

### 学生端

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/student/login | 学生登录 |
| POST | /api/student/logout | 学生登出 |
| POST | /api/chat | 发送对话 |
| GET | /api/chat/history | 获取历史 |

### 管理端

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/admin/login | 管理员登录 |
| POST | /api/admin/student | 录入学生 |
| GET | /api/admin/students | 学生列表 |
| GET | /api/admin/sessions | 会话列表 |
| GET | /api/admin/session/{id} | 会话详情 |
| GET | /api/admin/profile/{id} | 心理档案 |
| GET | /api/admin/alerts | 预警列表 |
| PATCH | /api/admin/alert/{id} | 处理预警 |
| GET/PATCH | /api/admin/config | 邮箱配置 |

---

## 数据库

SQLite数据库（`mental_health.db`），包含以下表：

- **students** - 学生信息
- **sessions** - 对话会话
- **messages** - 消息记录
- **alerts** - 危机预警
- **config** - 系统配置

---

## 部署注意事项

1. **API服务**需要保持运行，建议使用supervisor或systemd管理
2. **邮件配置**需要填写有效SMTP信息才能发送预警邮件
3. **学生端**和**管理端**必须通过HTTP服务器访问，不能直接双击打开HTML文件
4. **生产环境**建议使用nginx反向代理到8000端口

---

## 技术栈

- 后端：Python FastAPI
- 数据库：SQLite
- AI：MiniMax M2.5 API
- 前端：原生HTML/CSS/JavaScript

---

*最后更新：2026-04-23*
