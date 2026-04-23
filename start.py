"""
心灵伙伴 - 一键启动脚本
PyInstaller 兼容版
"""
import subprocess
import sys
import os
import time
import threading

def get_base_path():
    """获取程序根目录，兼容PyInstaller打包"""
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后的exe
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def run_api():
    """启动API服务"""
    base_path = get_base_path()
    os.chdir(base_path)
    # 添加当前目录到Python路径
    if base_path not in sys.path:
        sys.path.insert(0, base_path)
    subprocess.run([sys.executable, "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])

def run_frontend():
    """启动前端服务"""
    base_path = get_base_path()
    frontend_dir = os.path.join(base_path, "frontend")
    os.chdir(frontend_dir)
    subprocess.run([sys.executable, "-m", "http.server", "8080"])

if __name__ == "__main__":
    print("=" * 50)
    print("🫂 心灵伙伴 - 启动中...")
    print("=" * 50)
    
    # 启动API服务
    print("\n📡 启动API服务 (端口8000)...")
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # 启动前端服务
    print("🌐 启动前端服务 (端口8080)...")
    frontend_thread = threading.Thread(target=run_frontend, daemon=True)
    frontend_thread.start()
    
    # 等待服务启动
    time.sleep(4)
    
    print("\n" + "=" * 50)
    print("✅ 服务已就绪!")
    print("=" * 50)
    print("📝 学生端: http://localhost:8080")
    print("📝 管理端: http://localhost:8080/admin/index.html")
    print("📝 API文档: http://localhost:8000/docs")
    print("=" * 50)
    print("\n🎉 祝使用愉快！")
    print("\n按 Ctrl+C 停止服务\n")
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 已停止服务")
