"""
Step 4: AI对话处理模块
验证方法: python ai_handler.py (需设置MINIMAX_API_KEY环境变量)
"""

import os
import json
import base64
import requests
from config import MINIMAX_API_KEY, MINIMAX_API_URL, AI_MODE, SENSITIVE_WORDS

class AIHandler:
    """AI对话处理器"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or MINIMAX_API_KEY
        self.mode = AI_MODE  # minimax / local
        self.conversation_history = {}  # session_id -> messages
    
    # ===== 语音识别 (STT) =====
    def speech_to_text(self, audio_data, format="mp3"):
        """
        将语音转换为文字
        audio_data: 音频二进制数据
        返回: str 识别出的文字
        """
        if not self.api_key:
            print("⚠️ 未设置API Key，使用模拟识别")
            return "模拟识别结果：今天心情不好"
        
        try:
            # MiniMax 语音识别API
            url = f"{MINIMAX_API_URL}/asr"
            files = {
                'file': ('audio.mp3', audio_data, f'audio/{format}')
            }
            data = {
                'model': 'speech-01-turbo',
                'language_boost': 'zh'
            }
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = requests.post(url, files=files, data=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('text', '')
            else:
                print(f"❌ STT API错误: {response.status_code} {response.text}")
                return ""
        except Exception as e:
            print(f"❌ STT异常: {e}")
            return ""
    
    # ===== 对话生成 =====
    def chat(self, session_id, user_input, context=None):
        """
        处理用户对话
        session_id: 会话ID (用于维护历史)
        user_input: 用户输入文字
        context: 额外上下文
        返回: str AI回复
        """
        # 初始化会话历史
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        # 添加用户消息
        self.conversation_history[session_id].append({
            "role": "user",
            "content": user_input
        })
        
        # 构建prompt
        system_prompt = self._build_system_prompt(context)
        messages = [{"role": "system", "content": system_prompt}] + \
                   self.conversation_history[session_id][-10:]  # 保留最近10轮
        
        if self.mode == "minimax":
            reply = self._minimax_chat(messages)
        else:
            reply = self._local_chat(messages)
        
        # 添加AI回复
        self.conversation_history[session_id].append({
            "role": "assistant", 
            "content": reply
        })
        
        return reply
    
    def _build_system_prompt(self, context=None):
        """构建系统提示词"""
        base_prompt = """你是一个温暖、有爱心的心理陪伴助手，名字叫"心灵伙伴"。
专为小学生提供心理支持和陪伴。

核心原则：
1. 用温暖、耐心的态度回应
2. 用简单、小学生能理解的语言
3. 不给任何技术性建议或解决方案
4. 不评判、不批评、始终保持关爱
5. 如果学生表达自杀/轻生念头，立即进行危机干预和心理开导

危机干预话术：当学生提到自杀、轻生等想法时，要：
- 表达关心"我很担心你，你现在安全吗？"
- 倾听理解"愿意和我聊聊发生了什么吗？"
- 给予支持"你很重要，我会陪着你"
- 引导求助"我们可以一起想办法帮助你"
"""

        if context:
            base_prompt += f"\n\n当前背景：{context}"
        
        return base_prompt
    
    def _minimax_chat(self, messages):
        """MiniMax API对话"""
        try:
            url = f"{MINIMAX_API_URL}/text/chatcompletion_v2"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            data = {
                "model": "MiniMax-M2.5",
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.8
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"❌ MiniMax API错误: {response.status_code} {response.text}")
                return "抱歉，我现在有点状况，我们稍后再聊好吗？"
        except Exception as e:
            print(f"❌ MiniMax对话异常: {e}")
            return "抱歉，网络有点问题，我们稍后再聊好吗？"
    
    def _local_chat(self, messages):
        """本地模型对话（预留接口）"""
        # TODO: 实现本地模型调用
        print("⚠️ 本地模型模式未实现，使用MiniMax备用")
        return self._minimax_chat(messages)
    
    # ===== 语音合成 (TTS) =====
    def text_to_speech(self, text, output_path="response.mp3"):
        """
        将文字转换为语音
        text: 要转换的文字
        output_path: 输出文件路径
        返回: str 音频文件路径
        """
        if not self.api_key:
            print("⚠️ 未设置API Key，使用模拟TTS")
            return output_path
        
        try:
            url = f"{MINIMAX_API_URL}/t2a_v2"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            data = {
                "model": "speech-02-turbo",
                "text": text,
                "stream": False
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                # 返回的是音频URL或base64
                audio_url = result.get('data', {}).get('audio_url', '')
                return audio_url
            else:
                print(f"❌ TTS API错误: {response.status_code}")
                return ""
        except Exception as e:
            print(f"❌ TTS异常: {e}")
            return ""
    
    # ===== 对话总结 =====
    def summarize_session(self, session_id):
        """
        总结会话形成心理档案
        返回: dict 包含summary和risk_level
        """
        if session_id not in self.conversation_history:
            return {"summary": "", "risk_level": "low"}
        
        messages = self.conversation_history[session_id]
        
        # 构建总结prompt
        summary_prompt = f"""请分析以下对话，总结学生心理状态：

"""
        for msg in messages:
            role = "学生" if msg['role'] == 'user' else "AI助手"
            summary_prompt += f"{role}: {msg['content']}\n"
        
        summary_prompt += """
请输出：
1. 对话总结（100字内）
2. 风险等级：high/medium/low
3. 关注要点

只输出JSON格式：
{"summary": "...", "risk_level": "low", "concerns": ["..."]}
"""
        
        try:
            url = f"{MINIMAX_API_URL}/text/chatcompletion_v2"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            data = {
                "model": "MiniMax-M2.5",
                "messages": [{"role": "user", "content": summary_prompt}],
                "max_tokens": 300
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # 解析JSON
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    return {"summary": content, "risk_level": "low", "concerns": []}
            else:
                return {"summary": "总结生成失败", "risk_level": "medium"}
        except Exception as e:
            print(f"❌ 总结生成异常: {e}")
            return {"summary": "总结生成异常", "risk_level": "low"}
    
    # ===== 敏感词检测 =====
    def detect_crisis(self, text):
        """
        检测敏感词和危机
        返回: dict {triggered: bool, words: [], level: str}
        """
        text_lower = text.lower()
        found_words = []
        
        for word in SENSITIVE_WORDS:
            if word in text_lower:
                found_words.append(word)
        
        if not found_words:
            return {"triggered": False, "words": [], "level": "safe"}
        
        # 根据敏感词数量判断风险等级
        count = len(found_words)
        if count >= 3:
            level = "high"
        elif count >= 1:
            level = "medium"
        else:
            level = "low"
        
        return {
            "triggered": True,
            "words": found_words,
            "level": level,
            "message": f"检测到敏感词: {', '.join(found_words)}"
        }
    
    # ===== 危机干预回复 =====
    def crisis_intervention(self, user_input, detected_words):
        """
        生成危机干预回复
        当检测到自杀/轻生相关词汇时调用
        """
        crisis_prompt = f"""学生说了："{user_input}"
检测到敏感词：{', '.join(detected_words)}

你是"心灵伙伴"，一个温暖的心理陪伴助手。
学生正处于心理危机状态，请立即进行危机干预：

要求：
1. 表达真诚的关心
2. 让学生感受到被理解
3. 温和地引导但不强迫
4. 强调学生的价值和求助的重要性
5. 回复要简短温暖（100字以内）

只输出安慰和引导的话术。"""

        try:
            url = f"{MINIMAX_API_URL}/text/chatcompletion_v2"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            data = {
                "model": "MiniMax-M2.5",
                "messages": [{"role": "user", "content": crisis_prompt}],
                "max_tokens": 300,
                "temperature": 0.8
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                # 默认危机话术
                return "我听到你了，你现在很重要。如果你愿意，可以告诉我发生了什么，我会陪着你。我们一起想办法，好吗？"
        except Exception as e:
            print(f"❌ 危机干预异常: {e}")
            return "我听到你了，你现在很重要。如果你愿意，可以告诉我发生了什么，我会陪着你。"
    
    def clear_history(self, session_id):
        """清除会话历史"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]


# ===== 验证测试 =====
if __name__ == "__main__":
    print("=== AI Handler 验证测试 ===\n")
    
    handler = AIHandler()
    
    # 测试1: 敏感词检测
    print("📝 测试1: 敏感词检测")
    test_texts = [
        "我今天心情不好",
        "活着真没意思",
        "我不想活了，想自杀"
    ]
    for text in test_texts:
        result = handler.detect_crisis(text)
        print(f"  输入: {text}")
        print(f"  结果: triggered={result['triggered']}, level={result['level']}")
        print()
    
    # 测试2: 正常对话
    print("💬 测试2: 正常对话")
    reply = handler.chat("test_session_001", "我今天考试没考好")
    print(f"  AI回复: {reply[:100]}...")
    print()
    
    # 测试3: 危机干预
    print("🚨 测试3: 危机干预")
    crisis_reply = handler.crisis_intervention("我不想活了", ["不想活了", "自杀"])
    print(f"  危机回复: {crisis_reply[:100]}...")
    print()
    
    print("✅ AI Handler 模块验证完成！")