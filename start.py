"""
心灵伙伴 - 一键启动脚本
"""
import subprocess
import sys
import os

def main():
    base_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_path)
    sys.path.insert(0, base_path)
    
    print("=" * 50)
    print("🫂 心灵伙伴 - 启动中...")
    print("=" * 50)
    print("\n📡 API服务: http://localhost:8000")
    print("📝 学生端: http://localhost:8000/")
    print("📝 管理端: http://localhost:8000/admin/")
    print("📝 API文档: http://localhost:8000/docs")
    print("=" * 50)
    print("\n按 Ctrl+C 停止服务\n")
    
    # 启动uvicorn
    subprocess.run([sys.executable, "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"])

if __name__ == "__main__":
    main()
