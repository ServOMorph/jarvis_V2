"""
JARVIS V2 - Lanceur
"""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    main_path = Path(__file__).parent / "main.py"
    subprocess.run([sys.executable, str(main_path)])
