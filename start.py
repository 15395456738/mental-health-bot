"""
心灵伙伴 - 启动脚本
"""
import subprocess
import sys
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    print("=" * 50)
    print("🫂 心灵伙伴 - 启动中...")
    print("=" * 50)
    
    # 检查端口
    port = 8000
    while True:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('', port))
            sock.close()
            break
        except OSError:
            port += 1
            if port > 8100:
                print("无法找到可用端口")
                return
    
    # 初始化数据库
    if not os.path.exists(os.path.join(BASE_DIR, "mental_health.db")):
        print("📦 初始化数据库...")
        try:
            import database as db
            db.init_db()
            print("✅ 数据库就绪")
        except Exception as e:
            print(f"⚠️ 数据库初始化: {e}")
    
    # 启动服务
    print(f"\n🚀 启动服务 (端口 {port})...")
    os.chdir(BASE_DIR)
    sys.path.insert(0, BASE_DIR)
    
    subprocess.run([
        sys.executable, "-m", "uvicorn", "api:app",
        "--host", "0.0.0.0",
        "--port", str(port)
    ])

if __name__ == "__main__":
    main()
