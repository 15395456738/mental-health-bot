# 心灵伙伴 - 学生心理语音对话系统

## 项目概述
面向小学生的AI心理陪伴语音对话系统，支持纯语音交互、危机干预、心理档案管理。

## 技术栈
- **后端**: Python FastAPI
- **数据库**: SQLite (心理档案存储)
- **AI**: MiniMax API (语音识别 + 对话 + 语音合成)
- **前端**: 极简Web语音界面 (HTML+JS)
- **邮件**: SMTP (危机通知)

## 核心功能

### 1. 学生端
- [x] 账号密码登录
- [x] 纯语音对话 (WebRTC / Audio API)
- [x] 独立会话 (每个学生对话独立存储)

### 2. 老师管理端
- [x] 学生信息录入
- [x] 查看对话记录
- [x] 查看心理档案
- [x] 风险等级查看 (高/中/低)
- [x] 邮箱配置

### 3. AI对话
- [x] 语音识别 (MiniMax ASR)
- [x] 对话生成 (MiniMax Chat)
- [x] 语音合成 (MiniMax TTS)
- [x] 双模式切换 (云端API / 本地模型)

### 4. 危机干预
- [x] 敏感词监测 (自杀/轻生等)
- [x] AI先进行心理开导 (不给技术建议)
- [x] 风险分级 (高/中/低)
- [x] 高/中风险 → 邮件推送老师

### 5. 心理档案
- [x] 对话结束自动总结
- [x] 形成学生心理档案
- [x] 历史追溯

## 数据库结构

### students
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| username | TEXT | 登录账号 |
| password_hash | TEXT | 密码 |
| name | TEXT | 姓名 |
| grade | TEXT | 年级 |
| class_name | TEXT | 班级 |
| created_at | DATETIME | 创建时间 |

### sessions
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| student_id | INTEGER | 外键 |
| started_at | DATETIME | 开始时间 |
| ended_at | DATETIME | 结束时间 |
| summary | TEXT | 对话总结 |
| risk_level | TEXT | 风险等级 (high/medium/low) |
| status | TEXT | 处理状态 |

### messages
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| session_id | INTEGER | 外键 |
| role | TEXT | user/assistant |
| content | TEXT | 对话内容 |
| audio_url | TEXT | 音频URL |
| created_at | DATETIME | 时间 |

### alerts
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| session_id | INTEGER | 外键 |
| student_id | INTEGER | 外键 |
| risk_level | TEXT | 风险等级 |
| notified | BOOLEAN | 是否已通知 |
| created_at | DATETIME | 时间 |

## API接口

### 学生端
- POST /api/student/login
- POST /api/student/logout
- POST /api/chat (对话)
- GET /api/chat/history

### 管理端
- POST /api/admin/student (录入学生)
- GET /api/admin/students (学生列表)
- GET /api/admin/sessions (会话列表)
- GET /api/admin/session/:id (会话详情)
- GET /api/admin/profile/:student_id (心理档案)
- PATCH /api/admin/alert/:id (标记已处理)

### 配置
- GET/PATCH /api/admin/config (邮箱等配置)

## 部署
- 开发测试: MiniMax 云端API
- 正式环境: 本地大模型 (其他机器)