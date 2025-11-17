# Configuration de l'UI - JARVIS V2

## Fenêtre de Configuration de la Souris

La fenêtre de configuration permet de régler finement les paramètres de la souris contrôlée par la manette.

### 🎯 Nouvelles Fonctionnalités

#### 1. **Scrollbar (Ascenseur)**
- Permet de faire défiler les paramètres si la fenêtre contient beaucoup d'options
- Utilisez la molette de la souris pour scroller
- Pratique pour ajouter de nouveaux paramètres à l'avenir

#### 2. **Bouton 🔄 Réinitialiser**
- Remet tous les paramètres aux valeurs par défaut
- Valeurs par défaut (depuis `config.py`):
  - Sensibilité: 20.0
  - Sensibilité max: 60.0
  - Accélération: 2.0
  - Lissage: 0.3
  - Précision: 3.0
  - Zone morte: 0.15

#### 3. **Bouton ✓ Appliquer**
- **Applique les changements** au contrôleur en temps réel
- **Sauvegarde les paramètres** dans le fichier `config.py`
- Affiche un message de confirmation pendant 2 secondes
- Permet de **tester les paramètres** avant de fermer la fenêtre

#### 4. **Bouton Fermer**
- Ferme la fenêtre de configuration
- Les paramètres restent actifs s'ils ont été appliqués

### 📋 Workflow Recommandé

1. **Ouvrir** la configuration via le bouton "⚙️ Configuration Souris"
2. **Ajuster** les paramètres avec les sliders
3. **Cliquer sur "✓ Appliquer"** pour tester les changements
4. **Tester** la souris avec la manette
5. **Réajuster** si nécessaire et réappliquer
6. **Fermer** la fenêtre une fois satisfait

### 🎮 Préréglages Disponibles

- **🎮 Jeu**: Sensibilité élevée pour les jeux
- **💼 Bureautique**: Sensibilité modérée pour le travail
- **🎯 Précis**: Sensibilité basse pour un contrôle précis

### 💡 Conseils

- Les paramètres sont **mis à jour en temps réel** quand vous bougez les sliders
- Utilisez **"Appliquer"** pour sauvegarder définitivement vos réglages
- Utilisez **"Réinitialiser"** si vous voulez revenir aux valeurs d'origine
- Les préréglages sont un bon point de départ, puis affinez avec "Appliquer"

### 🧪 Test

Pour tester la fenêtre de configuration sans lancer l'application complète:
```bash
python test_config_ui.py
```

### 📝 Paramètres Sauvegardés

Tous les paramètres sont sauvegardés dans le fichier `config.py` dans la classe `MouseConfig`:
- `SENSITIVITY`: Sensibilité de base
- `MAX_SENSITIVITY`: Sensibilité maximale
- `ACCELERATION_CURVE`: Courbe d'accélération
- `SMOOTHING`: Lissage du mouvement
- `PRECISION_DIVIDER`: Diviseur de précision (mode RB/R1)
- `DEADZONE`: Zone morte du joystick
