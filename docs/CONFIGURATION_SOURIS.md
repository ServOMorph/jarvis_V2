# 🖱️ Configuration du mouvement de la souris

## 📋 Vue d'ensemble

Le système de mouvement de la souris a été amélioré pour offrir :
- ✅ **Mouvement fluide** sans saccades
- ✅ **Accélération progressive** (plus vous inclinez le joystick, plus c'est rapide)
- ✅ **Lissage adaptatif** pour réduire les tremblements
- ✅ **Haute fréquence de mise à jour** (~125 FPS par défaut)
- ✅ **Configuration centralisée** dans `config.py`

## ⚙️ Fichier de configuration

Tous les paramètres sont dans le fichier **`config.py`** à la racine du projet.

### 🎯 Paramètres principaux

```python
class MouseConfig:
    # Sensibilité de base
    SENSITIVITY = 30.0  # Augmenter pour aller plus vite

    # Sensibilité maximale (joystick à fond)
    MAX_SENSITIVITY = 60.0

    # Accélération (1.0 = linéaire, 2.0 = accélération progressive)
    ACCELERATION_CURVE = 2.0

    # Fréquence de mise à jour (plus petit = plus fluide)
    UPDATE_INTERVAL = 0.008  # ~125 FPS

    # Lissage (0.0 = aucun, 1.0 = maximum)
    SMOOTHING = 0.3

    # Zone morte du joystick
    DEADZONE = 0.15
```

## 🚀 Scénarios d'utilisation

### Souris PLUS RAPIDE
```python
SENSITIVITY = 50.0
MAX_SENSITIVITY = 100.0
ACCELERATION_CURVE = 2.5
```

### Souris PLUS FLUIDE
```python
UPDATE_INTERVAL = 0.005  # ~200 FPS
SMOOTHING = 0.5
ACCELERATION_CURVE = 1.5
```

### Souris PLUS PRÉCISE
```python
SENSITIVITY = 15.0
MAX_SENSITIVITY = 40.0
SMOOTHING = 0.4
ACCELERATION_CURVE = 1.2
```

### Souris SANS SACCADES
```python
UPDATE_INTERVAL = 0.005
SMOOTHING = 0.6
DEADZONE = 0.1
```

## 📊 Explication des paramètres

### `SENSITIVITY` (20-50 recommandé)
- Vitesse de base du curseur
- **Trop bas** → trop lent
- **Trop haut** → difficile à contrôler

### `MAX_SENSITIVITY` (40-100 recommandé)
- Vitesse maximale quand le joystick est à fond
- Permet d'avoir de la précision ET de la vitesse

### `ACCELERATION_CURVE` (1.0-3.0 recommandé)
- **1.0** = Linéaire (pas d'accélération)
- **2.0** = Accélération progressive (recommandé)
- **3.0** = Accélération forte

### `UPDATE_INTERVAL` (0.005-0.016 recommandé)
- Temps entre chaque mise à jour en secondes
- **0.005** = 200 FPS (très fluide, plus de CPU)
- **0.008** = 125 FPS (équilibre parfait) ⭐
- **0.016** = 60 FPS (économie CPU)

### `SMOOTHING` (0.0-0.7 recommandé)
- Lisse les mouvements brusques
- **0.0** = Aucun lissage (réactif mais peut trembler)
- **0.3** = Lissage léger (recommandé) ⭐
- **0.7** = Lissage fort (peut sembler retardé)

### `DEADZONE` (0.1-0.2 recommandé)
- Zone centrale où le joystick est considéré au repos
- **Trop bas** → le curseur bouge tout seul (drift)
- **Trop haut** → difficile de faire de petits mouvements

## 🎮 Configuration du scroll

```python
class ScrollConfig:
    SENSITIVITY = 3.0
    ACCELERATION_CURVE = 1.8
    DEADZONE = 0.2
```

## 🔧 Comment tester vos changements

1. Modifiez les valeurs dans `config.py`
2. Relancez le programme : `python main.py`
3. Testez avec votre manette
4. Ajustez jusqu'à obtenir le comportement désiré

## 💡 Mes réglages préférés

### Pour du jeu FPS (précis et rapide)
```python
SENSITIVITY = 35.0
MAX_SENSITIVITY = 80.0
ACCELERATION_CURVE = 2.2
UPDATE_INTERVAL = 0.005
SMOOTHING = 0.2
DEADZONE = 0.12
```

### Pour de la bureautique (précis et confortable)
```python
SENSITIVITY = 25.0
MAX_SENSITIVITY = 50.0
ACCELERATION_CURVE = 1.8
UPDATE_INTERVAL = 0.008
SMOOTHING = 0.4
DEADZONE = 0.15
```

### Pour de la navigation web (équilibré)
```python
SENSITIVITY = 30.0
MAX_SENSITIVITY = 60.0
ACCELERATION_CURVE = 2.0
UPDATE_INTERVAL = 0.008
SMOOTHING = 0.3
DEADZONE = 0.15
```

## 🐛 Problèmes courants

### Le curseur est saccadé
- ✅ Diminuez `UPDATE_INTERVAL` (ex: 0.005)
- ✅ Augmentez `SMOOTHING` (ex: 0.4)

### Le curseur va trop lentement
- ✅ Augmentez `SENSITIVITY` et `MAX_SENSITIVITY`
- ✅ Diminuez `ACCELERATION_CURVE`

### Le curseur bouge même au repos (drift)
- ✅ Augmentez `DEADZONE` (ex: 0.20)

### Le curseur semble retardé
- ✅ Diminuez `SMOOTHING` (ex: 0.1)
- ✅ Augmentez `UPDATE_INTERVAL`

### Impossible de faire de petits mouvements précis
- ✅ Diminuez `DEADZONE`
- ✅ Diminuez `SENSITIVITY`
- ✅ Augmentez `SMOOTHING`

## 🎯 Architecture technique

Le système utilise :
- **Thread séparé** pour le mouvement (indépendant du polling du gamepad)
- **Accumulateur fractionnaire** pour les mouvements sub-pixel
- **Delta time** pour un mouvement indépendant du framerate
- **Lissage exponentiel** pour la fluidité
- **Courbe d'accélération** pour précision + vitesse

Fichiers impliqués :
- `config.py` - Configuration centralisée
- `outils/mouse_controller.py` - Moteur de mouvement fluide
- `modules/gamepad_controller.py` - Intégration avec le gamepad
