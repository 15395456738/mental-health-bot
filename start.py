"""
心灵伙伴 - 启动器（GUI版本）
"""
import subprocess
import sys
import os
import socket
import time
import threading
import tkinter as tk
from tkinter import messagebox

# ===== 配置 =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
ADMIN_DIR = os.path.join(BASE_DIR, "admin")
DB_FILE = os.path.join(BASE_DIR, "mental_health.db")
DEFAULT_PORTS = [8000, 8001, 8002, 8003]

# ===== 工具函数 =====
def find_available_port(start_port=8000):
    for port in range(start_port, start_port + 10):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('', port))
            sock.close()
            return port
        except OSError:
            continue
    return None

def check_port_in_use(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('', port))
        sock.close()
        return False
    except OSError:
        return True

def init_database():
    if not os.path.exists(DB_FILE):
        try:
            import database as db
            db.init_db()
            return True
        except:
            return False
    return True

# ===== GUI应用 =====
class LauncherApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🫂 心灵伙伴")
        self.root.geometry("450x300")
        self.root.resizable(False, False)
        
        # 居中
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 450) // 2
        y = (self.root.winfo_screenheight() - 300) // 2
        self.root.geometry(f"450x300+{x}+{y}")
        
        self.port = None
        self.server_process = None
        
        self.create_widgets()
        self.start_server()
    
    def create_widgets(self):
        # 标题
        title = tk.Label(self.root, text="🫂 心灵伙伴", font=("Microsoft YaHei", 24, "bold"))
        title.pack(pady=20)
        
        # 副标题
        subtitle = tk.Label(self.root, text="学生心理陪伴系统", font=("Microsoft YaHei", 12))
        subtitle.pack()
        
        # 状态文本框
        self.status_text = tk.Text(self.root, height=8, width=50, font=("Consolas", 10))
        self.status_text.pack(pady=15)
        self.status_text.config(state='disabled')
        
        # 底部按钮
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        self.open_btn = tk.Button(btn_frame, text="打 开 浏 览 器", font=("Microsoft YaHei", 12),
                                   command=self.open_browser, state='disabled')
        self.open_btn.pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="退 出", font=("Microsoft YaHei", 12),
                 command=self.quit_app).pack(side=tk.LEFT, padx=10)
    
    def log(self, msg):
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, msg + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')
        self.root.update()
    
    def start_server(self):
        thread = threading.Thread(target=self._start_server_thread)
        thread.daemon = True
        thread.start()
    
    def _start_server_thread(self):
        self.log("🚀 正在启动服务...")
        
        # 检查端口
        self.port = DEFAULT_PORTS[0]
        if check_port_in_use(self.port):
            self.log(f"⚠️ 端口 {self.port} 被占用，尝试其他端口...")
            self.port = find_available_port()
            if self.port:
                self.log(f"✅ 找到可用端口: {self.port}")
            else:
                self.log("❌ 无法找到可用端口")
                return
        
        # 初始化数据库
        self.log("📦 检查数据库...")
        if init_database():
            self.log("✅ 数据库就绪")
        else:
            self.log("⚠️ 数据库初始化失败")
        
        # 检查静态文件
        if not os.path.exists(FRONTEND_DIR):
            self.log("⚠️ 前端文件未找到")
        
        # 启动服务
        self.log(f"🌐 启动API服务 (端口 {self.port})...")
        
        try:
            os.chdir(BASE_DIR)
            sys.path.insert(0, BASE_DIR)
            
            self.server_process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "api:app",
                 "--host", "0.0.0.0", "--port", str(self.port)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            
            time.sleep(2)
            
            if self.server_process.poll() is None:
                self.log("✅ 服务启动成功!")
                self.log("")
                self.log("=" * 40)
                self.log("📝 访问地址:")
                self.log(f"   学生端: http://localhost:{self.port}/")
                self.log(f"   管理端: http://localhost:{self.port}/admin/")
                self.log("=" * 40)
                self.log("")
                self.log("📝 管理员账号: admin / admin123")
                self.log("")
                self.log("💡 点击下方「打开浏览器」开始使用")
                self.open_btn.config(state='normal')
            else:
                self.log("❌ 服务启动失败")
                
        except Exception as e:
            self.log(f"❌ 启动错误: {e}")
    
    def open_browser(self):
        if self.port:
            import webbrowser
            webbrowser.open(f"http://localhost:{self.port}/")
    
    def quit_app(self):
        if self.server_process:
            self.server_process.terminate()
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.root.mainloop()

# ===== 主程序 =====
if __name__ == "__main__":
    try:
        app = LauncherApp()
        app.run()
    except Exception as e:
        print(f"启动错误: {e}")
        input("按回车键退出...")
