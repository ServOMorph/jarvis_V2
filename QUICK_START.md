# Guide de Démarrage Rapide - JARVIS V2

## 🚀 Démarrage

```bash
python main.py
```

## 🎮 Contrôles de Base

### Boutons
- **A (Bouton 0)** : Clic gauche 🖱️
- **B (Bouton 1)** : Toggle recherche image yes.png
- **Y (Bouton 2)** : Clic droit 🖱️
- **X (Bouton 3)** : Dictée vocale (maintenir) 🎤

### Joysticks
- **Joystick gauche** : Déplacer la souris
- **Joystick droit (Y)** : Scroll haut/bas

### Autres
- **RB/R1** : Mode précision (maintenir)

## ⚙️ Configuration de la Souris

1. Dans l'interface, cliquer sur **"⚙️ Configuration Souris"**
2. Ajuster les paramètres avec les sliders
3. **Fermer la fenêtre** → Les réglages sont sauvegardés automatiquement
4. Au prochain démarrage, vos réglages seront chargés automatiquement

### Boutons de la fenêtre de config
- **🔄 Réinitialiser** : Revenir aux valeurs par défaut
- **✓ Appliquer** : Sauvegarder dans config.py ET mouse_settings.json
- **Fermer** : Sauvegarder dans mouse_settings.json et fermer

## 📝 Fichiers Importants

- `config/voice_config.json` : Configuration des boutons
- `config/mouse_settings.json` : Sauvegarde automatique des réglages
- `config.py` : Valeurs par défaut du code

## 🔧 Modifier les Boutons

Éditer `config/voice_config.json` :

```json
{
  "button_mapping": {
    "0": {
      "action": "mouse_click_left",
      "description": "Clic gauche"
    },
    "2": {
      "action": "mouse_click_right",
      "description": "Clic droit"
    }
  }
}
```

Actions disponibles :
- `mouse_click_left` / `mouse_click_right`
- `key_press_enter` / `key_press_esc`
- `alt_tab` / `ctrl_w`
- `volume_down` / `volume_up`

## 🎯 Préréglages Souris

Dans la fenêtre de configuration :
- **🎮 Jeu** : Sensibilité élevée, réactivité maximale
- **💼 Bureautique** : Sensibilité modérée, confort
- **🎯 Précis** : Sensibilité basse, contrôle précis

## ❓ Problèmes Courants

### La manette n'est pas détectée
- Vérifier que la manette est branchée
- Sous Windows : Panneau de configuration → "Périphériques de jeu"
- Essayer de débrancher/rebrancher

### Les clics ne fonctionnent pas
- Vérifier `config/voice_config.json`
- S'assurer que les boutons 0 et 2 sont bien configurés

### Les réglages ne sont pas sauvegardés
- Vérifier que le dossier `config/` existe
- Fermer la fenêtre de config (ne pas forcer la fermeture)

## 📚 Documentation Complète

- [CONFIGURATION_RESUME.md](CONFIGURATION_RESUME.md) : Détails de la configuration
- [UI_CONFIG_README.md](UI_CONFIG_README.md) : Interface de configuration
- [CHANGELOG_UI.md](CHANGELOG_UI.md) : Historique des modifications
