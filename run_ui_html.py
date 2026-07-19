import subprocess
import sys
import webbrowser
import time
from pathlib import Path

ROOT_DIR = Path(__file__).parent
SERVER_SCRIPT = ROOT_DIR / "server" / "websocket_server.py"
UI_PATH = ROOT_DIR / "web" / "index.html"


def main():
    print("Demarrage du serveur WebSocket...")
    server_process = subprocess.Popen(
        [sys.executable, str(SERVER_SCRIPT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    time.sleep(1)

    print(f"Ouverture de l'interface: {UI_PATH}")
    webbrowser.open(UI_PATH.as_uri())

    print("Serveur actif. Ctrl+C pour arreter.\n")

    try:
        for line in server_process.stdout:
            print(line, end="")
    except KeyboardInterrupt:
        print("\nArret du serveur...")
        server_process.terminate()
        server_process.wait()
        print("Serveur arrete.")


if __name__ == "__main__":
    main()
