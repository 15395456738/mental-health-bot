"""
心灵伙伴 - 启动脚本
自动初始化 + 端口检测 + 启动反馈
"""
import subprocess
import sys
import os
import socket
import time
import shutil
import zipfile

# ===== 配置 =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
ADMIN_DIR = os.path.join(BASE_DIR, "admin")
DB_FILE = os.path.join(BASE_DIR, "mental_health.db")

DEFAULT_PORTS = [8000, 8001, 8002, 8003]  # 备用端口

# ===== 工具函数 =====
def find_available_port(start_port=8000):
    """查找可用端口"""
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
    """检查端口是否被占用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('', port))
        sock.close()
        return False
    except OSError:
        return True

def init_database():
    """初始化数据库"""
    if not os.path.exists(DB_FILE):
        print(f"\n📦 首次启动，正在初始化数据库...")
        try:
            import database as db
            db.init_db()
            print("✅ 数据库初始化完成")
        except Exception as e:
            print(f"⚠️ 数据库初始化失败: {e}")
    else:
        print(f"✅ 数据库已就绪")

def check_and_extract_static():
    """检查并提取静态文件"""
    # 检查frontend目录
    if not os.path.exists(FRONTEND_DIR) or not os.listdir(FRONTEND_DIR):
        print(f"\n📂 正在检查静态文件...")
        # exe模式下静态文件可能在临时目录
        if getattr(sys, 'frozen', False):
            temp_dir = sys._MEIPASS
            src_frontend = os.path.join(temp_dir, "frontend")
            src_admin = os.path.join(temp_dir, "admin")
            
            if os.path.exists(src_frontend):
                shutil.copytree(src_frontend, FRONTEND_DIR, dirs_exist_ok=True)
            if os.path.exists(src_admin):
                shutil.copytree(src_admin, ADMIN_DIR, dirs_exist_ok=True)
            print("✅ 静态文件已提取")

def print_banner():
    """打印启动画面"""
    print("=" * 60)
    print("🫂 心灵伙伴 - 学生心理陪伴系统")
    print("=" * 60)

def main():
    print_banner()
    
    # 检查端口
    port = DEFAULT_PORTS[0]
    if check_port_in_use(port):
        print(f"\n⚠️ 端口 {port} 已被占用，正在查找可用端口...")
        port = find_available_port()
        if port:
            print(f"✅ 找到可用端口: {port}")
        else:
            print("❌ 无法找到可用端口，请关闭其他程序后重试")
            input("按回车键退出...")
            return
    
    # 初始化
    print(f"\n📍 工作目录: {BASE_DIR}")
    init_database()
    check_and_extract_static()
    
    # 启动服务
    print(f"\n🚀 正在启动服务...")
    print("-" * 60)
    
    # 启动uvicorn
    server_cmd = [
        sys.executable, "-m", "uvicorn", "api:app",
        "--host", "0.0.0.0",
        "--port", str(port)
    ]
    
    try:
        subprocess.Popen(server_cmd, cwd=BASE_DIR)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        input("按回车键退出...")
        return
    
    # 等待服务启动
    time.sleep(2)
    
    # 输出结果
    print("\n" + "=" * 60)
    print("✅ 服务启动成功!")
    print("=" * 60)
    print(f"\n🌐 访问地址:")
    print(f"   学生端: http://localhost:{port}/")
    print(f"   管理端: http://localhost:{port}/admin/")
    print(f"   API文档: http://localhost:{port}/docs")
    print("\n" + "-" * 60)
    print("📝 管理员账号: admin / admin123")
    print("-" * 60)
    print("\n💡 首次使用请先在管理端录入学生账号")
    print("\n按 Ctrl+C 停止服务")
    print("=" * 60)
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 已停止服务")

if __name__ == "__main__":
    main()
