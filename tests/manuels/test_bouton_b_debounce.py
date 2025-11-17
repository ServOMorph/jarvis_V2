"""
Test du debounce pour le bouton B
Simule ce qui se passe avec les appuis multiples
"""

class MockToggleHandler:
    """Simule le gestionnaire de toggle avec debounce"""

    def __init__(self):
        self.toggle_state = False
        self.button_pressed_flags = {}
        self.press_count = 0
        self.toggle_count = 0

    def on_button_press(self, button_id):
        """Simule _on_button_press avec debounce"""
        self.press_count += 1

        # Éviter les déclenchements multiples
        if self.button_pressed_flags.get(button_id, False):
            print(f"  [IGNORE] Appui #{self.press_count} ignoré (déjà pressé)")
            return

        self.button_pressed_flags[button_id] = True
        print(f"  [ACCEPT] Appui #{self.press_count} accepté")

        # Toggle l'état
        self.toggle_state = not self.toggle_state
        self.toggle_count += 1
        print(f"  [TOGGLE] État: {self.toggle_state}")

    def on_button_release(self, button_id):
        """Simule _on_button_release"""
        self.button_pressed_flags[button_id] = False
        print(f"  [RELEASE] Bouton relâché")


print("=" * 70)
print("TEST DU DEBOUNCE - BOUTON B")
print("=" * 70)

handler = MockToggleHandler()

# Simulation 1: Appui normal
print("\n--- Simulation 1: Appui normal ---")
handler.on_button_press(1)
handler.on_button_release(1)
print(f"État final: {handler.toggle_state} (devrait être True)")

# Simulation 2: Appuis multiples rapides (bug)
print("\n--- Simulation 2: Appuis multiples rapides (simule le bug) ---")
handler.on_button_press(1)
handler.on_button_press(1)  # Déclenchement multiple - devrait être ignoré
handler.on_button_press(1)  # Déclenchement multiple - devrait être ignoré
handler.on_button_release(1)
print(f"État final: {handler.toggle_state} (devrait rester True)")

# Simulation 3: Plusieurs appuis normaux
print("\n--- Simulation 3: Plusieurs appuis normaux ---")
for i in range(5):
    print(f"\nAppui {i+1}:")
    handler.on_button_press(1)
    handler.on_button_release(1)

print("\n" + "=" * 70)
print(f"RÉSUMÉ:")
print(f"  Appuis détectés: {handler.press_count}")
print(f"  Toggles effectués: {handler.toggle_count}")
print(f"  État final: {handler.toggle_state}")
print("=" * 70)
