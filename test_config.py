"""Test de la configuration"""
import json

with open('config/voice_config.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== CONFIGURATION DES BOUTONS ===\n')
for btn_id in sorted([int(k) for k in data['button_mapping'].keys()]):
    btn = data['button_mapping'][str(btn_id)]
    print(f'Bouton {btn_id}: {btn["description"]}')

print('\n=== SAUVEGARDE DES REGLAGES ===')
print('Les reglages de la souris seront sauvegardes dans:')
print('  config/mouse_settings.json')
print('\nCe fichier sera charge automatiquement au demarrage.')
