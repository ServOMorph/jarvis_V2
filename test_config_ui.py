"""
Script de test pour la fenêtre de configuration de la souris
Teste le scrollbar, le bouton Reset et le bouton Appliquer
"""
import tkinter as tk
from ui.gamepad_controls_ui import MouseConfigWindow

class MockController:
    """Contrôleur simulé pour le test"""
    def __init__(self):
        class MockMouse:
            def __init__(self):
                self.sensitivity = 20.0
                self.max_sensitivity = 60.0
                self.acceleration_curve = 2.0
                self.smoothing = 0.3
                self.precision_divider = 3.0
                self.deadzone = 0.15

        self.smooth_mouse = MockMouse()
        print("[Test] Contrôleur simulé créé")
        print(f"  - Sensibilité initiale: {self.smooth_mouse.sensitivity}")

def main():
    """Fonction principale"""
    print("=== Test de la fenêtre de configuration ===")
    print("Fonctionnalités à tester:")
    print("  1. Scrollbar (molette de la souris)")
    print("  2. Bouton 🔄 Réinitialiser (valeurs par défaut)")
    print("  3. Bouton ✓ Appliquer (sauvegarde dans config.py)")
    print("  4. Bouton Fermer")
    print("=" * 45)

    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale

    # Créer le contrôleur simulé
    controller = MockController()

    # Ouvrir la fenêtre de configuration
    config_window = MouseConfigWindow(root, controller)

    # Lancer la boucle principale
    root.mainloop()

    print("\n[Test] Fenêtre fermée")
    print(f"[Test] Sensibilité finale du contrôleur: {controller.smooth_mouse.sensitivity}")

if __name__ == "__main__":
    main()
