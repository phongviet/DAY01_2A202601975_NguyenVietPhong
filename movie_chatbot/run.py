import os
import sys
import subprocess

def main():
    print("==================================================")
    print("🎬 KHỞI CHẠY CINEBRAIN AI - STREAMLIT MOVIE CHATBOT")
    print("==================================================")
    
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)

    print("Đang khởi chạy Streamlit server tại: http://localhost:8501")
    print("Nhấn Ctrl+C để dừng server.\n")

    cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port=8501", "--server.headless=false"]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nĐã dừng Streamlit server.")

if __name__ == "__main__":
    main()
