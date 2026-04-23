"""
Step 6: 邮件推送模块
验证方法: python email_sender.py
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
import database as db
from config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD

class EmailSender:
    """邮件发送器"""
    
    def __init__(self):
        self.server = SMTP_SERVER
        self.port = SMTP_PORT
        self.username = SMTP_USERNAME
        self.password = SMTP_PASSWORD
    
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return bool(self.server and self.username and self.password)
    
    def send_alert(self, to_emails: List[str], student_name: str, 
                   risk_level: str, crisis_content: str, 
                   session_id: int = None) -> dict:
        """
        发送危机预警邮件
        to_emails: 收件人列表
        student_name: 学生姓名
        risk_level: 风险等级 high/medium/low
        crisis_content: 危机内容
        session_id: 会话ID
        返回: dict 发送结果
        """
        if not self.is_configured():
            return {"success": False, "error": "邮件未配置"}
        
        # 风险等级颜色
        colors = {
            "high": "#dc3545",    # 红色
            "medium": "#ffc107",  # 黄色
            "low": "#28a745"      # 绿色
        }
        color = colors.get(risk_level, "#6c757d")
        
        # 邮件内容
        subject = f"⚠️ 心灵伙伴 - 学生危机预警 [{risk_level.upper()}]"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">🫂 心灵伙伴 - 危机预警</h1>
            </div>
            
            <div style="padding: 30px; background: #fff; border: 1px solid #ddd; border-top: none;">
                <div style="background: {color}; color: white; padding: 10px 20px; border-radius: 5px; display: inline-block; margin-bottom: 20px;">
                    <strong>风险等级: {risk_level.upper()}</strong>
                </div>
                
                <h2 style="color: #333; margin-top: 0;">学生信息</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>姓名</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{student_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>风险等级</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">
                            <span style="background: {color}; color: white; padding: 2px 8px; border-radius: 3px;">{risk_level.upper()}</span>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>会话ID</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{session_id or 'N/A'}</td>
                    </tr>
                </table>
                
                <h2 style="color: #333;">危机内容</h2>
                <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid {color}; border-radius: 5px;">
                    <p style="margin: 0; color: #333;">{crisis_content}</p>
                </div>
                
                <h2 style="color: #333;">建议处理</h2>
                <ul style="color: #666;">
                    <li>尽快与学生进行一对一沟通</li>
                    <li>关注学生的情绪状态变化</li>
                    <li>必要时联系心理咨询专业人士</li>
                    <li>记录处理过程和结果</li>
                </ul>
                
                <p style="color: #999; font-size: 12px; margin-top: 30px;">
                    此邮件由心灵伙伴系统自动发送。请及时处理。<br>
                    系统时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </div>
            
            <div style="background: #f8f9fa; padding: 15px; text-align: center; border-radius: 0 0 10px 10px; border: 1px solid #ddd; border-top: none;">
                <a href="#" style="color: #667eea; text-decoration: none;">查看详细档案</a>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        🫂 心灵伙伴 - 危机预警通知
        
        学生: {student_name}
        风险等级: {risk_level.upper()}
        会话ID: {session_id or 'N/A'}
        
        危机内容:
        {crisis_content}
        
        建议处理:
        1. 尽快与学生进行一对一沟通
        2. 关注学生的情绪状态变化
        3. 必要时联系心理咨询专业人士
        4. 记录处理过程和结果
        
        系统时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = ', '.join(to_emails)
            
            # 添加纯文本和HTML两种格式
            msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # 发送邮件
            with smtplib.SMTP(self.server, self.port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.username, to_emails, msg.as_string())
            
            return {"success": True, "sent_to": to_emails}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_test(self, to_email: str) -> dict:
        """发送测试邮件"""
        return self.send_alert(
            to_emails=[to_email],
            student_name="测试学生",
            risk_level="low",
            crisis_content="这是一封测试邮件，用于验证邮件配置是否正确。",
            session_id=0
        )


def send_pending_alerts():
    """发送所有待处理的预警邮件"""
    sender = EmailSender()
    
    if not sender.is_configured():
        print("⚠️ 邮件未配置，跳过发送")
        return
    
    # 获取所有未处理的预警
    alerts = db.get_pending_alerts()
    
    if not alerts:
        print("✅ 没有待处理的预警")
        return
    
    print(f"📤 开始发送 {len(alerts)} 封预警邮件...")
    
    for alert in alerts:
        student_name = alert.get('student_name', '未知')
        risk_level = alert.get('risk_level', 'low')
        sensitive_word = alert.get('sensitive_word', '')
        
        # 获取会话消息
        session_id = alert.get('session_id')
        messages = db.get_session_messages(session_id) if session_id else []
        
        # 提取对话内容
        crisis_content = "\n".join([
            f"{'学生' if m['role']=='user' else 'AI'}: {m['content']}"
            for m in messages[-5:]  # 最近5条
        ])
        
        # 获取管理员邮箱
        admin_email = db.get_config("admin_email") or db.get_config("ADMIN_EMAIL")
        recipients = [admin_email] if admin_email else []
        
        if not recipients:
            print(f"⚠️ 预警 {alert['id']} 没有配置收件人")
            continue
        
        result = sender.send_alert(
            to_emails=recipients,
            student_name=student_name,
            risk_level=risk_level,
            crisis_content=crisis_content,
            session_id=session_id
        )
        
        if result["success"]:
            db.mark_alert_notified(alert['id'])
            print(f"  ✅ 已发送预警 {alert['id']} -> {recipients}")
        else:
            print(f"  ❌ 预警 {alert['id']} 发送失败: {result['error']}")
    
    print("📤 预警邮件发送完成")


# ===== 验证测试 =====
if __name__ == "__main__":
    print("=== Email Sender 验证测试 ===\n")
    
    sender = EmailSender()
    
    # 检查配置
    if sender.is_configured():
        print("✅ 邮件已配置")
        
        # 发送测试
        print("\n📧 发送测试邮件...")
        # result = sender.send_test("test@example.com")
        # print(f"结果: {result}")
        print("（测试邮件已跳过，避免无效发送）")
    else:
        print("⚠️ 邮件未配置，使用模拟模式")
    
    print("\n=== 预警处理测试 ===")
    send_pending_alerts()
    
    print("\n✅ Email Sender 模块验证完成！")
