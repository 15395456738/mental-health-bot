# 心灵伙伴 - 学生心理语音对话系统

## 项目概述

面向小学生的AI心理陪伴语音对话系统，支持纯语音交互、危机干预、心理档案管理。

**目标用户：** 小学生（6-12岁）
**适用场景：** 学校心理健康教育、心理疏导、危机预警

## 功能特性

### 学生端 🧒
- ✅ 账号密码登录
- ✅ 文字对话
- ✅ 语音对话（WebRTC）
- ✅ 心情选择（开心/一般/有点低落/很难过）
- ✅ 独立会话存储
- ✅ 危机热线提示

### 管理端 👨‍🏫
- ✅ 管理员登录
- ✅ 学生信息管理（录入/编辑）
- ✅ 预警中心（高/中/低风险）
- ✅ 对话记录查看
- ✅ 学生心理档案
- ✅ 邮件推送配置

### 危机干预 🚨
- ✅ 敏感词自动检测
- ✅ AI温暖心理开导（倾听风格，不给建议）
- ✅ 高/中风险自动预警
- ✅ 显示心理援助热线（400-161-9995）
- ✅ 邮件通知老师

## 技术栈

- **后端：** Python FastAPI
- **数据库：** SQLite
- **AI：** MiniMax M2.5 API
- **前端：** 原生 HTML/CSS/JavaScript
- **打包：** PyInstaller

## 系统架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  学生端     │────▶│  API服务    │────▶│  MiniMax   │
│  (浏览器)   │◀────│  (FastAPI)  │◀────│  AI API    │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │   SQLite     │
                    │   数据库      │
                    └─────────────┘
```

## 数据库结构

### students（学生表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| username | TEXT | 登录账号 |
| password_hash | TEXT | 密码哈希 |
| name | TEXT | 姓名 |
| grade | TEXT | 年级 |
| class_name | TEXT | 班级 |
| created_at | DATETIME | 注册时间 |

### sessions（会话表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| student_id | INTEGER | 外键 |
| started_at | DATETIME | 开始时间 |
| ended_at | DATETIME | 结束时间 |
| summary | TEXT | 对话总结 |
| risk_level | TEXT | 风险等级 |
| status | TEXT | 状态 |

### messages（消息表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| session_id | INTEGER | 外键 |
| role | TEXT | 角色 |
| content | TEXT | 内容 |
| audio_url | TEXT | 音频 |
| created_at | DATETIME | 时间 |

### alerts（预警表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| session_id | INTEGER | 外键 |
| student_id | INTEGER | 外键 |
| risk_level | TEXT | 风险等级 |
| sensitive_word | TEXT | 触发词 |
| notified | BOOLEAN | 已通知 |
| created_at | DATETIME | 时间 |

## AI对话设计

### 系统提示词原则
1. **温暖倾听** - 用简单、小学生能理解的语言
2. **简短回复** - 控制在50字以内
3. **鼓励表达** - 引导学生表达感受
4. **不评判** - 不批评、不给建议

### 危机干预流程
1. 温和询问（不急于给建议）
2. 表达关心（"我很担心你"）
3. 倾听理解
4. 给予支持（"你很重要"）
5. 引导求助热线

### 风险等级
- **HIGH** - 检测到自杀/自残相关词汇
- **MEDIUM** - 检测到消极情绪表达
- **LOW** - 正常对话

## 界面设计

### 学生端
- 渐变色主题（紫蓝渐变）
- 心情选择按钮
- 危机热线Banner
- 动画效果

### 管理端
- 卡片式布局
- 标签页切换
- 数据表格
- 预警高亮显示

## 部署方式

### 开发环境
```bash
pip install fastapi uvicorn requests python-dotenv
python -m uvicorn api:app --port 8000
```

### Windows exe
1. 下载 release 版本
2. 解压
3. 同目录创建 .env 配置API密钥
4. 运行 心灵伙伴.exe

## 配置文件

`.env` 文件示例：
```
MINIMAX_API_KEY=你的API密钥
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

## 更新日志

### v2.0 (2026-04-23)
- ✨ 精美UI（渐变色、动画）
- ✨ 心情选择功能
- ✨ 危机热线提示
- ✨ AI对话优化（倾听风格）
- ✨ GitHub Actions 自动构建exe
