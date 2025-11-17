"""
Test de l'UI avec focus sur le bouton B
Lance l'UI en mode standalone pour tester le toggle
"""

import tkinter as tk
import sys
from pathlib import Path

# Ajouter le dossier racine au path
root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path))

from ui.gamepad_controls_ui import ModernGamepadUI

def main():
    print("=" * 70)
    print("TEST UI - BOUTON B (MODE TOGGLE)")
    print("=" * 70)
    print("\nInstructions:")
    print("  1. Connectez votre manette")
    print("  2. Appuyez sur le bouton B (bouton 1)")
    print("  3. Vérifiez que le message apparaît en bas de l'UI")
    print("  4. Rappuyez sur B pour désactiver")
    print("\nLes messages de debug s'afficheront dans cette console.")
    print("=" * 70)
    print()

    root = tk.Tk()
    config_path = root_path / "config" / "voice_config.json"
    app = ModernGamepadUI(root, config_path=str(config_path))

    def on_closing():
        print("\nFermeture de l'UI...")
        app.cleanup()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    print("UI lancée ! Testez le bouton B...\n")
    root.mainloop()

    print("\n" + "=" * 70)
    print("Test terminé!")
    print("=" * 70)


if __name__ == "__main__":
    main()
