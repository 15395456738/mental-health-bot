"""
心灵伙伴 - 启动脚本
"""
import subprocess
import sys
import os
import socket

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def is_port_free(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('', port))
        sock.close()
        return True
    except:
        return False

def find_free_port(start=8000):
    for port in range(start, start + 100):
        if is_port_free(port):
            return port
    return None

def main():
    base_dir = get_base_dir()
    os.chdir(base_dir)
    sys.path.insert(0, base_dir)
    
    # 端口检测
    port = find_free_port(8000)
    if not port:
        print("错误：无法找到可用端口")
        input("按回车退出...")
        return
    
    # 数据库初始化
    db_file = os.path.join(base_dir, "mental_health.db")
    if not os.path.exists(db_file):
        print("首次启动，初始化数据库...")
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("database", os.path.join(base_dir, "database.py"))
            db_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(db_mod)
            db_mod.init_db()
            print("数据库就绪")
        except Exception as e:
            print(f"数据库初始化失败: {e}")
    
    print("=" * 50)
    print("心灵伙伴启动中...")
    print(f"端口: {port}")
    print("=" * 50)
    
    # 启动
    try:
        subprocess.Popen([
            sys.executable, "-m", "uvicorn", "api:app",
            "--host", "0.0.0.0",
            "--port", str(port),
            "--app-dir", base_dir
        ], cwd=base_dir)
    except Exception as e:
        print(f"启动失败: {e}")
        input("按回车退出...")
        return
    
    import time
    time.sleep(2)
    
    print("\n启动成功!")
    print(f"\n学生端: http://localhost:{port}/")
    print(f"管理端: http://localhost:{port}/admin/")
    print(f"管理员: admin / admin123")
    print("\n按 Ctrl+C 停止")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n已停止")

if __name__ == "__main__":
    main()
