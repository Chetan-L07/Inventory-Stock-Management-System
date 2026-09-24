import subprocess
import sys
import time
import os

def main():
    print("=" * 60)
    print("🚀 STARTING INVENTORY STOCK MANAGEMENT SYSTEM")
    print("=" * 60)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    python_exe = sys.executable

    print("\n[1/2] Starting Flask Backend Server on http://127.0.0.1:5001...")
    backend_app = os.path.join(base_dir, "backend", "app.py")
    backend_proc = subprocess.Popen(
        [python_exe, backend_app],
        cwd=os.path.join(base_dir, "backend")
    )

    time.sleep(2.5)

    print("\n[2/2] Launching Streamlit UI on http://localhost:8501...")
    frontend_ui = os.path.join(base_dir, "Frontend", "ui.py")
    frontend_proc = subprocess.Popen(
        [python_exe, "-m", "streamlit", "run", frontend_ui, "--server.port=8501"],
        cwd=os.path.join(base_dir, "Frontend")
    )

    print("\n" + "=" * 60)
    print("✨ Both Flask Backend & Streamlit UI are running!")
    print("🌐 Streamlit UI URL:        http://localhost:8501")
    print("🔗 Flask Swagger API Docs:  http://127.0.0.1:5001/swagger")
    print("=" * 60)
    print("Press Ctrl+C to terminate both applications.\n")

    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nTerminating background services...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Successfully stopped all services.")

if __name__ == "__main__":
    main()
