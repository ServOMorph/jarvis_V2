"""
Module pour contrôler le PC avec la manette + reconnaissance vocale
Combine GamepadController et VoiceCopyPaste
"""

import sys
import os

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.gamepad_controller import GamepadController, GamepadConfig, GamepadActions
from modules.copier_coller import VoiceCopyPaste, VoiceConfig
from outils.speech_recognizer import RecognitionEngine
from outils.auto_clicker import AutoClicker
from typing import Optional
import time
import threading


class GamepadVoiceController(GamepadController):
    """Extension de GamepadController avec support de la dictée vocale"""

    def __init__(self, gamepad_config: Optional[GamepadConfig] = None, voice_config: Optional[VoiceConfig] = None):
        """
        Initialise le contrôleur manette + voix

        Args:
            gamepad_config: Configuration de la manette
            voice_config: Configuration de la reconnaissance vocale
        """
        # Initialiser le contrôleur de manette de base
        super().__init__(gamepad_config)

        # Initialiser le système de dictée vocale
        self.voice_paste = VoiceCopyPaste(voice_config or VoiceConfig())

        # Initialiser le clicker automatique
        self.auto_clicker = AutoClicker(confidence=0.8)

        # État de l'enregistrement vocal
        self.voice_button_pressed = False

        # État du mode ClaudeIA
        self.claude_mode_active = False

        # État du bouton B (recherche continue en mode toggle)
        self.search_active = False  # État de la recherche (activée ou non)
        self.button_b_thread = None
        self.button_b_stop_event = threading.Event()

        # Chemin de l'image yes.png
        self.yes_image_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "images", "yes.png"
        )

    def _click_yes_image_continuous(self):
        """
        Recherche et clique en continu sur l'image yes.png tant que le bouton est pressé
        """
        print(f"\n[BOUTON B] 🔍 Recherche continue ACTIVÉE\n")

        click_count = 0

        while not self.button_b_stop_event.is_set():
            success = self.auto_clicker.click_on_image(
                self.yes_image_path,
                button='left',
                clicks=1
            )

            if success:
                click_count += 1
                print(f"[BOUTON B] ✅ Clic #{click_count} effectué")

            # Petite pause avant la prochaine recherche (évite de surcharger le CPU)
            # Utiliser wait() au lieu de sleep() pour pouvoir être interrompu rapidement
            if self.button_b_stop_event.wait(timeout=0.3):
                break

        print(f"\n[BOUTON B] ⏹️ Recherche ARRÊTÉE - {click_count} clic(s) effectué(s)\n")

    def handle_button(self, button_id: int, pressed: bool):
        """
        Surcharge pour gérer les boutons spéciaux (bouton 1 et 3)

        Args:
            button_id: ID du bouton
            pressed: True si pressé, False si relâché
        """
        # Bouton 1 (B) : Toggle recherche continue de yes.png
        if button_id == 1:
            # Détecter uniquement l'appui (pas le relâchement)
            if pressed and button_id not in self.button_states:
                # Marquer le bouton comme pressé
                self.button_states[button_id] = True

                # Toggle le mode ClaudeIA
                self.claude_mode_active = not self.claude_mode_active
                status = "ACTIVE" if self.claude_mode_active else "DESACTIVE"
                print(f"\n[CLAUDE IA] Mode VSCode Auto: {status}")

                # Toggle la recherche continue
                if not self.search_active:
                    # Démarrer la recherche
                    self.search_active = True
                    self.button_b_stop_event.clear()

                    print(f"[BOUTON B] ▶️  Démarrage de la recherche continue...")

                    # Lancer la recherche continue dans un thread séparé
                    self.button_b_thread = threading.Thread(
                        target=self._click_yes_image_continuous,
                        daemon=True
                    )
                    self.button_b_thread.start()

                else:
                    # Arrêter la recherche
                    self.search_active = False
                    print(f"[BOUTON B] ⏸️  Arrêt de la recherche continue...")
                    self.button_b_stop_event.set()

                    # Attendre que le thread se termine (avec timeout)
                    if self.button_b_thread and self.button_b_thread.is_alive():
                        self.button_b_thread.join(timeout=1.0)

            elif not pressed and button_id in self.button_states:
                # Bouton relâché : nettoyer l'état
                del self.button_states[button_id]

        # Bouton 3 : Dictée vocale (maintenir pour enregistrer)
        elif button_id == 3:
            if pressed and not self.voice_button_pressed:
                # Bouton pressé : démarrer l'enregistrement
                self.voice_button_pressed = True
                self.voice_paste.start_voice_input()

            elif not pressed and self.voice_button_pressed:
                # Bouton relâché : arrêter et reconnaître
                self.voice_button_pressed = False
                self.voice_paste.stop_voice_input()

        # Bouton 5 (RB/R1) : Mode précision de la souris (maintenir)
        elif button_id == 5:
            if pressed:
                # Activer le mode précision
                self.smooth_mouse.set_precision_mode(True)
                print("[MODE PRÉCISION] Vitesse de la souris réduite")
            else:
                # Désactiver le mode précision
                self.smooth_mouse.set_precision_mode(False)
                print("[MODE NORMAL] Vitesse de la souris normale")

        else:
            # Laisser le contrôleur de base gérer les autres boutons
            super().handle_button(button_id, pressed)

    def cleanup(self):
        """Nettoie les ressources (manette + voix)"""
        self.voice_paste.cleanup()
        super().disconnect()


def get_voice_gamepad_config() -> GamepadConfig:
    """
    Retourne une configuration par défaut avec le bouton 3 pour la voix

    Mapping :
    - Bouton 0 (A/X) : Clic gauche
    - Bouton 1 (B/O) : Clic droit
    - Bouton 2 (X/□) : Entrée
    - Bouton 3 (Y/△) : 🎤 DICTÉE VOCALE (maintenir)
    - Bouton 4 (LB/L1) : Alt+Tab
    - Bouton 5 (RB/R1) : Ctrl+W
    - Joystick gauche : Déplacer la souris
    - Joystick droit (X) : Scroll horizontal
    - Joystick droit (Y) : Scroll vertical
    """
    return GamepadConfig(
        button_mappings={
            0: GamepadActions.mouse_click('left'),
            1: GamepadActions.mouse_click('right'),
            2: GamepadActions.key_press('enter'),
            # Bouton 3 géré spécialement pour la voix
            4: GamepadActions.key_combination('alt', 'tab'),
            5: GamepadActions.key_combination('ctrl', 'w'),
            6: GamepadActions.key_press('volumedown'),
            7: GamepadActions.key_press('volumeup'),
        },
        axis_mappings={
            0: GamepadActions.mouse_move(sensitivity=15.0),
            1: GamepadActions.mouse_move_vertical(sensitivity=15.0),
            2: GamepadActions.mouse_scroll_horizontal(sensitivity=5.0),
            3: GamepadActions.mouse_scroll(sensitivity=5.0),
        },
        deadzone=0.15,
        mouse_sensitivity=15.0,
        scroll_sensitivity=2.0
    )


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🎮 CONTRÔLEUR MANETTE + VOIX")
    print("=" * 60)

    # Configuration
    gamepad_config = get_voice_gamepad_config()
    voice_config = VoiceConfig(
        language="fr-FR",
        engine=RecognitionEngine.GOOGLE,
        auto_paste=True,
        feedback=True
    )

    # Créer le contrôleur
    controller = GamepadVoiceController(gamepad_config, voice_config)

    # Connecter la manette
    if controller.connect():
        print("\n=== CONFIGURATION ===")
        print("Bouton 0 (A/X) : Clic gauche")
        print("Bouton 1 (B/O) : Clic droit")
        print("Bouton 2 (X/□) : Entrée")
        print("Bouton 3 (Y/△) : 🎤 DICTÉE VOCALE (maintenir le bouton)")
        print("Bouton 4 (LB/L1) : Alt+Tab")
        print("Bouton 5 (RB/R1) : Ctrl+W (fermer)")
        print("Bouton 6 (Back) : Volume -")
        print("Bouton 7 (Start) : Volume +")
        print("\nJoystick gauche : Déplacer la souris")
        print("Joystick droit (X) : Scroll horizontal (gauche/droite)")
        print("Joystick droit (Y) : Scroll vertical (haut/bas)")
        print("\n" + "=" * 60)
        print("💡 ASTUCE : Maintenez le bouton 3 et parlez,")
        print("            relâchez pour coller le texte reconnu")
        print("=" * 60 + "\n")

        # Lancer la boucle principale
        controller.run()

    else:
        print("❌ Impossible de se connecter à la manette.")
