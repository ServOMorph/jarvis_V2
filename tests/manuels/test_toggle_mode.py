"""
Test du mode toggle pour le bouton B (ClaudeIA mode)
"""

import json
from pathlib import Path

# Charger la configuration
config_path = Path(__file__).parent.parent.parent / "config" / "voice_config.json"
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

print("=" * 60)
print("TEST DU MODE TOGGLE - BOUTON B")
print("=" * 60)

# Simuler les états du toggle
toggle_state = False

button_mapping = config.get('button_mapping', {})

# Trouver le bouton 1 (B)
btn_1_config = button_mapping.get('1', None)

if btn_1_config:
    print(f"\nBouton 1 (B) configuré:")
    print(f"  Description: {btn_1_config['description']}")
    print(f"  Action: {btn_1_config['action']}")

    print("\n" + "-" * 60)
    print("SIMULATION DU TOGGLE")
    print("-" * 60)

    # Simulation de 5 appuis
    for i in range(5):
        toggle_state = not toggle_state
        print(f"\nAppui #{i+1} sur le bouton B")

        if toggle_state:
            print("  ✅ Mode ClaudeIA dans VSCode Auto activé")
        else:
            print("  ❌ Mode ClaudeIA désactivé")
else:
    print("\n❌ Bouton 1 (B) non configuré!")

print("\n" + "=" * 60)
print("Test terminé!")
print("=" * 60)
