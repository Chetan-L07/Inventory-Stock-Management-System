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

    # -----------------------------
    # 1. Start Flask Backend
    # -----------------------------
    print("\n[1/2] Starting Flask Backend Server...")
    print("URL: http://127.0.0.1:5001")

    backend_app = os.path.join(base_dir, "backend", "app.py")

    backend_proc = subprocess.Popen(
        [python_exe, backend_app],
        cwd=os.path.join(base_dir, "backend")
    )

    time.sleep(2.5)

    # Check whether Flask crashed
    if backend_proc.poll() is not None:
        print("\n❌ Flask Backend failed to start.")
        print("Please check the Flask error above.")
        return

    print("✅ Flask Backend started successfully.")

    # -----------------------------
    # 2. Start Streamlit UI
    # -----------------------------
    print("\n[2/2] Starting Streamlit UI...")
    print("URL: http://localhost:8501")

    frontend_ui = os.path.join(
        base_dir,
        "Frontend",
        "ui.py"
    )

    frontend_proc = subprocess.Popen(
        [
            python_exe,
            "-m",
            "streamlit",
            "run",
            frontend_ui,
            "--server.port=8501"
        ],
        cwd=os.path.join(base_dir, "Frontend")
    )

    time.sleep(2.5)

    # Check whether Streamlit crashed
    if frontend_proc.poll() is not None:
        print("\n❌ Streamlit UI failed to start.")
        print("Please check the Streamlit error above.")

        backend_proc.terminate()
        return

    print("✅ Streamlit UI started successfully.")

    # -----------------------------
    # Both running
    # -----------------------------
    print("\n" + "=" * 60)
    print("✨ INVENTORY STOCK MANAGEMENT SYSTEM IS RUNNING")
    print("=" * 60)
    print("🌐 Streamlit UI:      http://localhost:8501")
    print("🔗 Flask API:         http://127.0.0.1:5001")
    print("📚 Swagger:           http://127.0.0.1:5001/swagger")
    print("=" * 60)
    print("Press Ctrl+C to stop both services.\n")

    try:
        while True:
            # Check if either process stops
            if backend_proc.poll() is not None:
                print("\n❌ Flask Backend stopped.")
                break

            if frontend_proc.poll() is not None:
                print("\n❌ Streamlit UI stopped.")
                break

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n🛑 Stopping services...")

    finally:
        if backend_proc.poll() is None:
            backend_proc.terminate()

        if frontend_proc.poll() is None:
            frontend_proc.terminate()

        print("✅ All services stopped.")


if __name__ == "__main__":
    main()