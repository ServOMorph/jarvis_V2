"""
Test direct du bouton 1 (B) avec le contrôleur
"""

import sys
from pathlib import Path

# Ajouter le dossier racine au path
root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path))

from modules.gamepad_voice_controller import GamepadVoiceController, get_voice_gamepad_config
from modules.copier_coller import VoiceConfig


class TestController(GamepadVoiceController):
    """Contrôleur de test pour simuler les appuis"""

    def __init__(self):
        config = get_voice_gamepad_config()
        voice_config = VoiceConfig()
        super().__init__(config, voice_config)

        # Initialiser button_states si nécessaire
        if not hasattr(self, 'button_states'):
            self.button_states = {}

    def simulate_button_press(self, button_id):
        """Simule un appui de bouton"""
        print(f"\n[SIMULATION] Appui sur le bouton {button_id}")
        self.handle_button(button_id, pressed=True)

    def simulate_button_release(self, button_id):
        """Simule un relâchement de bouton"""
        print(f"[SIMULATION] Relâchement du bouton {button_id}")
        self.handle_button(button_id, pressed=False)


def main():
    print("=" * 70)
    print("TEST DU BOUTON 1 (B) - MODE CLAUDEIA")
    print("=" * 70)

    controller = TestController()

    print("\nÉtat initial du mode ClaudeIA:", controller.claude_mode_active)

    # Test 1: Premier appui (activation)
    print("\n--- Test 1: Premier appui ---")
    controller.simulate_button_press(1)
    controller.simulate_button_release(1)
    print(f"État du mode: {controller.claude_mode_active}")
    assert controller.claude_mode_active == True, "Le mode devrait être activé"

    # Test 2: Deuxième appui (désactivation)
    print("\n--- Test 2: Deuxième appui ---")
    controller.simulate_button_press(1)
    controller.simulate_button_release(1)
    print(f"État du mode: {controller.claude_mode_active}")
    assert controller.claude_mode_active == False, "Le mode devrait être désactivé"

    # Test 3: Troisième appui (réactivation)
    print("\n--- Test 3: Troisième appui ---")
    controller.simulate_button_press(1)
    controller.simulate_button_release(1)
    print(f"État du mode: {controller.claude_mode_active}")
    assert controller.claude_mode_active == True, "Le mode devrait être réactivé"

    # Test 4: Appuis multiples (debounce)
    print("\n--- Test 4: Appuis multiples rapides ---")
    initial_state = controller.claude_mode_active
    controller.simulate_button_press(1)
    controller.simulate_button_press(1)  # Devrait être ignoré
    controller.simulate_button_press(1)  # Devrait être ignoré
    controller.simulate_button_release(1)
    print(f"État du mode: {controller.claude_mode_active}")
    # Un seul toggle devrait avoir eu lieu
    expected = not initial_state
    assert controller.claude_mode_active == expected, f"Le mode devrait être {expected}"

    print("\n" + "=" * 70)
    print("✅ TOUS LES TESTS PASSENT !")
    print("=" * 70)


if __name__ == "__main__":
    main()
