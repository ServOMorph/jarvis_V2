# Changelog - Interface UI Configuration

## Version 2.0 - Nouvelles Fonctionnalités

### ✨ Ajouts

#### 1. Scrollbar (Ascenseur)
- **Fichier**: `ui/gamepad_controls_ui.py`
- **Lignes**: 81-109
- Ajout d'un Canvas avec scrollbar verticale
- Support de la molette de la souris pour scroller
- Permet de gérer plus de paramètres à l'avenir
- Largeur de la zone scrollable: 580px
- Nettoyage automatique des bindings à la fermeture

#### 2. Bouton "Réinitialiser"
- **Fichier**: `ui/gamepad_controls_ui.py`
- **Lignes**: 198-212
- Bouton violet (couleur: #533483)
- Icône: 🔄
- Fonction: `_reset_to_defaults()` (lignes 365-375)
- Remet tous les paramètres aux valeurs par défaut
- Valeurs par défaut stockées dans `DEFAULT_VALUES` (lignes 24-31)

#### 3. Bouton "Appliquer"
- **Fichier**: `ui/gamepad_controls_ui.py`
- **Lignes**: 214-228
- Bouton cyan (couleur: #00d9ff)
- Icône: ✓
- Fonction: `_apply_config()` (lignes 377-447)
- Fonctionnalités:
  - Récupère les valeurs actuelles des sliders
  - Sauvegarde dans `config.py` via regex
  - Met à jour `MouseConfig` en mémoire
  - Affiche une confirmation pendant 2 secondes
  - Logs détaillés dans la console

#### 4. Message de Confirmation
- **Fichier**: `ui/gamepad_controls_ui.py`
- **Lignes**: 449-464
- Fonction: `_show_confirmation()`
- Affiche un label cyan pendant 2 secondes
- Position: centré en bas de la fenêtre
- Message: "✓ Configuration appliquée et sauvegardée !"
- Auto-destruction après 2 secondes

### 🔧 Modifications

#### Fenêtre de Configuration
- **Taille**: 600x700 → 650x750 pixels (ligne 44)
- **Structure**:
  - En-tête (fixe)
  - Zone scrollable (Canvas + Scrollbar)
  - Boutons en bas (fixe): Reset | Appliquer | Fermer

#### Gestion de la Fermeture
- Ajout de `_on_close()` (lignes 472-477)
- Nettoyage des bindings de la molette
- Protocole de fermeture personnalisé (ligne 57)

### 📦 Fichiers Ajoutés

1. **test_config_ui.py**
   - Script de test pour la fenêtre de configuration
   - Contrôleur simulé (MockController)
   - Affiche les valeurs initiales et finales

2. **UI_CONFIG_README.md**
   - Documentation complète des nouvelles fonctionnalités
   - Workflow recommandé
   - Conseils d'utilisation

3. **CHANGELOG_UI.md** (ce fichier)
   - Historique des modifications
   - Détails techniques

### 🎨 Design

#### Boutons
- **Réinitialiser**: Violet (#533483)
- **Appliquer**: Cyan (#00d9ff)
- **Fermer**: Rouge/Rose (#e94560)

#### Organisation
```
┌─────────────────────────────┐
│  En-tête (fixe)             │
├─────────────────────────────┤
│  Zone Scrollable            │ ←─ Scrollbar
│  - Sensibilité              │
│  - Sensibilité max          │
│  - Accélération             │
│  - Lissage                  │
│  - Précision                │
│  - Zone morte               │
│  - Préréglages              │
├─────────────────────────────┤
│ [Reset][Appliquer][Fermer]  │ ←─ Fixe
└─────────────────────────────┘
```

### 🧪 Tests

Pour tester:
```bash
python test_config_ui.py
```

Vérifications:
- ✓ Import du module
- ✓ Création de la fenêtre
- ✓ Scrollbar fonctionnel
- ✓ Bouton Reset
- ✓ Bouton Appliquer
- ✓ Sauvegarde dans config.py
- ✓ Message de confirmation
- ✓ Nettoyage à la fermeture

### 📝 Notes Techniques

#### Regex pour la Sauvegarde
Pattern utilisé: `r'(\s+)(PARAM_NAME\s*=\s*)[0-9.]+'`
- Capture l'indentation
- Capture le nom de la variable
- Remplace uniquement la valeur numérique

#### Ordre des Paramètres
L'ordre dans `self.vars.values()` est important:
1. SENSITIVITY
2. MAX_SENSITIVITY
3. ACCELERATION_CURVE
4. SMOOTHING
5. PRECISION_DIVIDER
6. DEADZONE

### 🐛 Corrections

- Unbind de la molette à la fermeture (évite les conflits)
- Gestion des erreurs lors de la sauvegarde
- Vérification du nombre de paramètres
- Encodage UTF-8 pour config.py

### 🔮 Améliorations Futures

- [ ] Bouton "Exporter" pour sauvegarder les profils
- [ ] Bouton "Importer" pour charger des profils
- [ ] Plus de préréglages personnalisables
- [ ] Graphique de visualisation de la courbe d'accélération
- [ ] Undo/Redo des modifications
