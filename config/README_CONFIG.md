# Configuration JARVIS V2

## Fichier de configuration : `voice_config.json`

Ce fichier contient toute la configuration de JARVIS V2, y compris les mappings des boutons de la manette.

## Structure du fichier

### Section `button_mapping`

Cette section définit les actions pour chaque bouton de la manette.

#### Exemple actuel :
```json
"button_mapping": {
  "3": {
    "action": "voice_input",
    "params": null,
    "description": "Dictée vocale (maintenir)"
  }
}
```

#### Boutons disponibles (Manette Xbox)

| Numéro | Bouton |
|--------|--------|
| 0 | A |
| 1 | B |
| 2 | Y |
| 3 | X |
| 4 | LB |
| 5 | RB |
| 6 | Back |
| 7 | Start |
| 8 | L3 (clic stick gauche) |
| 9 | R3 (clic stick droit) |

#### Actions prédéfinies

| Action | Description | Exemple d'utilisation |
|--------|-------------|----------------------|
| `voice_input` | Dictée vocale (maintenir le bouton) | Bouton 3 actuel |
| `mouse_click_left` | Clic gauche de la souris | Bouton 0 |
| `mouse_click_right` | Clic droit de la souris | Bouton 1 |
| `key_press_enter` | Appuyer sur Entrée | Bouton 2 |
| `key_press_esc` | Appuyer sur Échap | Bouton 3 |
| `alt_tab` | Alt + Tab (changer de fenêtre) | Bouton 4 |
| `ctrl_w` | Ctrl + W (fermer onglet) | Bouton 5 |
| `volume_down` | Baisser le volume | Bouton 6 |
| `volume_up` | Augmenter le volume | Bouton 7 |

### Exemple de configuration complète

```json
{
  "voice": {
    "language": "fr-FR",
    "engine": "google",
    "max_duration": 10.0,
    "auto_paste": true,
    "feedback": true
  },
  "audio": {
    "sample_rate": 16000,
    "channels": 1,
    "chunk_size": 1024,
    "device_index": null
  },
  "gamepad": {
    "voice_button": 3,
    "deadzone": 0.15,
    "mouse_sensitivity": 15.0,
    "scroll_sensitivity": 2.0
  },
  "button_mapping": {
    "0": {
      "action": "mouse_click_left",
      "params": null,
      "description": "Clic gauche"
    },
    "1": {
      "action": "mouse_click_right",
      "params": null,
      "description": "Clic droit"
    },
    "2": {
      "action": "key_press_enter",
      "params": null,
      "description": "Entrée"
    },
    "3": {
      "action": "voice_input",
      "params": null,
      "description": "Dictée vocale (maintenir)"
    },
    "4": {
      "action": "alt_tab",
      "params": null,
      "description": "Changer de fenêtre"
    }
  }
}
```

## Interface graphique

L'interface graphique affiche **uniquement** les boutons et axes configurés dans `voice_config.json`.

- Si vous ajoutez un nouveau bouton dans `button_mapping`, il apparaîtra automatiquement dans l'UI
- Si vous retirez un bouton, il disparaîtra de l'UI
- Les axes (joysticks) sont affichés selon les paramètres `mouse_sensitivity` et `scroll_sensitivity` de la section `gamepad`

## Configuration actuelle

Les boutons suivants sont configurés :

- **Bouton 1 (B)** : Mode ClaudeIA VSCode Auto (toggle on/off)
  - Action: `toggle_claude_mode`
  - Permet d'activer/désactiver le mode ClaudeIA
  - Le statut s'affiche dans l'interface graphique
  - Chaque appui inverse l'état (on → off → on)

- **Bouton 3 (X)** : Dictée vocale (maintenir)
  - Action: `voice_input`
  - Permet d'utiliser la reconnaissance vocale
  - Maintenez le bouton, parlez, relâchez

Pour ajouter d'autres boutons, ajoutez simplement de nouvelles entrées dans la section `button_mapping`.
