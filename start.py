"""
心灵伙伴 - 启动脚本（单例版本）
"""
import subprocess
import sys
import os
import socket
import time
import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "mental_health.db")
LOCK_FILE = os.path.join(BASE_DIR, ".launcher.lock")
API_PORT = 8000

def is_port_in_use(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('', port))
        sock.close()
        return False
    except OSError:
        return True

def find_available_port(start=8000, end=8100):
    for port in range(start, end):
        if not is_port_in_use(port):
            return port
    return None

def write_pid():
    """写入PID，防止重复启动"""
    try:
        with open(LOCK_FILE, 'w') as f:
            f.write(str(os.getpid()))
        return True
    except:
        return False

def cleanup_lock():
    """清理锁文件"""
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    except:
        pass

def init_db():
    """初始化数据库"""
    if not os.path.exists(DB_FILE):
        print("📦 首次使用，正在初始化数据库...")
        try:
            # 导入并初始化
            sys.path.insert(0, BASE_DIR)
            import importlib.util
            spec = importlib.util.spec_from_file_location("database", os.path.join(BASE_DIR, "database.py"))
            db = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(db)
            db.init_db()
            print("✅ 数据库初始化完成")
        except Exception as e:
            print(f"⚠️ 数据库初始化失败: {e}")

def main():
    # 清理旧的锁文件
    cleanup_lock()
    
    # 检查是否已运行
    if is_port_in_use(API_PORT):
        print(f"⚠️ 心灵伙伴已在运行中！")
        print(f"请访问: http://localhost:{API_PORT}/")
        input("\n按回车键退出...")
        return
    
    # 写入PID
    write_pid()
    
    # 查找可用端口
    port = API_PORT
    if is_port_in_use(port):
        port = find_available_port()
        if not port:
            print("❌ 无法找到可用端口")
            return
    
    print("=" * 50)
    print("🫂 心灵伙伴 - 学生心理陪伴系统")
    print("=" * 50)
    print(f"\n📍 工作目录: {BASE_DIR}")
    
    # 初始化数据库
    init_db()
    
    print(f"\n🚀 启动服务 (端口 {port})...")
    print("-" * 50)
    
    # 切换到工作目录
    os.chdir(BASE_DIR)
    sys.path.insert(0, BASE_DIR)
    
    # 启动uvicorn
    try:
        subprocess.Popen([
            sys.executable, "-m", "uvicorn", "api:app",
            "--host", "0.0.0.0",
            "--port", str(port)
        ], stdout=sys.stdout, stderr=subprocess.STDOUT)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        cleanup_lock()
        return
    
    # 等待服务就绪
    time.sleep(2)
    
    print("\n" + "=" * 50)
    print("✅ 服务启动成功!")
    print("=" * 50)
    print(f"\n🌐 访问地址:")
    print(f"   学生端: http://localhost:{port}/")
    print(f"   管理端: http://localhost:{port}/admin/")
    print(f"   API文档: http://localhost:{port}/docs")
    print("\n" + "-" * 50)
    print(f"📝 管理员账号: admin / admin123")
    print("-" * 50)
    print("\n💡 首次使用请先在管理端录入学生账号")
    print("\n按 Ctrl+C 停止服务")
    print("=" * 50)
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 已停止服务")
    finally:
        cleanup_lock()

if __name__ == "__main__":
    main()
