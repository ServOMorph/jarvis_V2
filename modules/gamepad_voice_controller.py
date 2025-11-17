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
from typing import Optional
import time


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

        # État de l'enregistrement vocal
        self.voice_button_pressed = False

        # État du mode ClaudeIA
        self.claude_mode_active = False

    def handle_button(self, button_id: int, pressed: bool):
        """
        Surcharge pour gérer les boutons spéciaux (bouton 1 et 3)

        Args:
            button_id: ID du bouton
            pressed: True si pressé, False si relâché
        """
        # Bouton 1 : Toggle mode ClaudeIA (appui unique)
        if button_id == 1:
            if pressed and button_id not in self.button_states:
                # Toggle le mode ClaudeIA
                self.claude_mode_active = not self.claude_mode_active
                status = "ACTIVE" if self.claude_mode_active else "DESACTIVE"
                print(f"\n[CLAUDE IA] Mode VSCode Auto: {status}")
                # Marquer le bouton comme pressé
                self.button_states[button_id] = True

            elif not pressed and button_id in self.button_states:
                # Bouton relâché
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
    - Joystick droit (Y) : Scroll
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
            3: GamepadActions.mouse_scroll(sensitivity=2.0),
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
        print("Joystick droit (Y) : Scroll")
        print("\n" + "=" * 60)
        print("💡 ASTUCE : Maintenez le bouton 3 et parlez,")
        print("            relâchez pour coller le texte reconnu")
        print("=" * 60 + "\n")

        # Lancer la boucle principale
        controller.run()

    else:
        print("❌ Impossible de se connecter à la manette.")
