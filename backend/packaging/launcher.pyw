"""
launcher.pyw — double-clicked by the Desktop shortcut / Start Menu entry.

.pyw (not .py) so Windows runs it via pythonw.exe with no console window
popping up — the user just sees a browser tab open, nothing else.
"""
import os
import sys
import threading
import time
import webbrowser

APP_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(APP_DIR)
sys.path.insert(0, APP_DIR)

PORT = 8501


def open_browser_when_ready():
    time.sleep(10)
    webbrowser.open(f"http://localhost:{PORT}")


def main():
    bundled_tesseract = os.path.join(APP_DIR, "tesseract", "tesseract.exe")
    if os.path.exists(bundled_tesseract):
        os.environ["CIVICVERIFY_TESSERACT_CMD"] = bundled_tesseract

    bundled_model = os.path.join(APP_DIR, "models", "model.Q4_K_M.gguf")
    if os.path.exists(bundled_model):
        os.environ["CIVICVERIFY_MODEL_PATH"] = bundled_model

    threading.Thread(target=open_browser_when_ready, daemon=True).start()

    from streamlit.web import cli as stcli

    sys.argv = [
        "streamlit", "run", os.path.join(APP_DIR, "streamlit_app.py"),
        "--server.headless=true",
        f"--server.port={PORT}",
        "--server.address=localhost",
        "--browser.gatherUsageStats=false",
    ]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()