"""
Serveur de developpement avec hot reload pour JARVIS V2
Lance le projet et le relance automatiquement a chaque changement de fichier
Port: 5500
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileModifiedEvent
except ImportError:
    print("Installation de watchdog...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "watchdog"])
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileModifiedEvent

# Configuration
PROJECT_ROOT = Path(__file__).parent
WATCH_EXTENSIONS = {'.py', '.json'}
IGNORE_PATTERNS = {'__pycache__', '.git', '.venv', 'venv', 'env', '.pyc'}
DEBOUNCE_SECONDS = 1.0
PORT = 5500


class Colors:
    """Couleurs ANSI pour le terminal"""
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'


class JarvisDevServer:
    """Serveur de developpement avec hot reload"""

    def __init__(self):
        self.process = None
        self.observer = None
        self.last_reload_time = 0
        self.lock = threading.Lock()
        self.running = True

    def print_banner(self):
        """Affiche la banniere du serveur"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}   JARVIS V2 - Serveur de Developpement{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.GREEN}   Port: {PORT}{Colors.RESET}")
        print(f"{Colors.GREEN}   Hot Reload: ACTIF{Colors.RESET}")
        print(f"{Colors.GREEN}   Extensions surveillees: {', '.join(WATCH_EXTENSIONS)}{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")

    def start_jarvis(self):
        """Demarre le processus JARVIS V2"""
        if self.process:
            self.stop_jarvis()

        print(f"{Colors.YELLOW}[DEV] Demarrage de JARVIS V2...{Colors.RESET}")

        # Lancer main.py
        self.process = subprocess.Popen(
            [sys.executable, str(PROJECT_ROOT / "main.py")],
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True
        )

        # Thread pour afficher la sortie en temps reel
        def read_output():
            try:
                for line in iter(self.process.stdout.readline, ''):
                    if line:
                        print(f"{Colors.RESET}{line}", end='')
            except:
                pass

        output_thread = threading.Thread(target=read_output, daemon=True)
        output_thread.start()

        print(f"{Colors.GREEN}[DEV] JARVIS V2 demarre (PID: {self.process.pid}){Colors.RESET}\n")

    def stop_jarvis(self):
        """Arrete le processus JARVIS V2"""
        if self.process:
            print(f"\n{Colors.YELLOW}[DEV] Arret de JARVIS V2 (PID: {self.process.pid})...{Colors.RESET}")
            try:
                # Terminer proprement
                self.process.terminate()
                try:
                    self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    # Force kill si necessaire
                    self.process.kill()
                    self.process.wait()
            except Exception as e:
                print(f"{Colors.RED}[DEV] Erreur lors de l'arret: {e}{Colors.RESET}")
            finally:
                self.process = None

    def reload(self, changed_file: str = None):
        """Recharge le projet"""
        current_time = time.time()

        with self.lock:
            # Debounce pour eviter les reloads multiples
            if current_time - self.last_reload_time < DEBOUNCE_SECONDS:
                return
            self.last_reload_time = current_time

        if changed_file:
            rel_path = Path(changed_file).relative_to(PROJECT_ROOT)
            print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.YELLOW}[HOT RELOAD] Fichier modifie: {rel_path}{Colors.RESET}")
            print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")

        self.start_jarvis()

    def run(self):
        """Lance le serveur de developpement"""
        self.print_banner()

        # Creer le handler pour les evenements de fichiers
        event_handler = FileChangeHandler(self)

        # Creer l'observateur
        self.observer = Observer()
        self.observer.schedule(event_handler, str(PROJECT_ROOT), recursive=True)
        self.observer.start()

        print(f"{Colors.GREEN}[DEV] Surveillance des fichiers activee{Colors.RESET}")
        print(f"{Colors.BLUE}[DEV] Appuyez sur Ctrl+C pour arreter{Colors.RESET}\n")

        # Demarrer JARVIS
        self.start_jarvis()

        try:
            while self.running:
                time.sleep(0.5)
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}[DEV] Arret du serveur...{Colors.RESET}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Nettoie les ressources"""
        self.running = False
        self.stop_jarvis()
        if self.observer:
            self.observer.stop()
            self.observer.join()
        print(f"{Colors.GREEN}[DEV] Serveur arrete proprement{Colors.RESET}\n")


class FileChangeHandler(FileSystemEventHandler):
    """Handler pour les changements de fichiers"""

    def __init__(self, server: JarvisDevServer):
        self.server = server
        super().__init__()

    def should_ignore(self, path: str) -> bool:
        """Verifie si le fichier doit etre ignore"""
        path_obj = Path(path)

        # Ignorer les patterns
        for part in path_obj.parts:
            if part in IGNORE_PATTERNS:
                return True

        # Verifier l'extension
        if path_obj.suffix not in WATCH_EXTENSIONS:
            return True

        return False

    def on_modified(self, event):
        """Appele quand un fichier est modifie"""
        if event.is_directory:
            return

        if self.should_ignore(event.src_path):
            return

        self.server.reload(event.src_path)

    def on_created(self, event):
        """Appele quand un fichier est cree"""
        if event.is_directory:
            return

        if self.should_ignore(event.src_path):
            return

        self.server.reload(event.src_path)


def main():
    """Point d'entree principal"""
    server = JarvisDevServer()

    # Gerer le signal SIGINT (Ctrl+C)
    def signal_handler(sig, frame):
        server.running = False

    signal.signal(signal.SIGINT, signal_handler)

    server.run()


if __name__ == "__main__":
    main()
