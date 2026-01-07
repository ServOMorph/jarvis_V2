# 🎮 JARVIS V2 🎤

Contrôlez votre PC avec une manette de jeu et la reconnaissance vocale !

## 🚀 Lancement rapide

```bash
pip install -r requirements.txt
python main.py
```

## 📋 Fonctionnalités

- **Contrôle de la souris** avec les joysticks
- **Raccourcis clavier** via les boutons de la manette
- **Dictée vocale** : maintenez un bouton, parlez, et le texte est automatiquement collé
- **Architecture modulaire** : outils réutilisables pour vos propres projets
- **Configuration personnalisable** via fichier JSON

## 🏗️ Structure du projet

```
jarvis_V2/
├── main.py                    # Point d'entrée principal
├── requirements.txt           # Dépendances Python
│
├── outils/                    # Outils réutilisables
│   ├── audio_recorder.py      # Enregistrement audio
│   ├── speech_recognizer.py   # Reconnaissance vocale
│   └── clipboard_manager.py   # Gestion presse-papier
│
├── modules/                   # Modules fonctionnels
│   ├── gamepad_controller.py          # Contrôle manette
│   ├── copier_coller.py               # Dictée vocale
│   └── gamepad_voice_controller.py    # Manette + voix
│
├── config/                    # Configuration
│   └── voice_config.json      # Paramètres globaux
│
└── tests/manuels/             # Tests manuels
    └── test_gamepad_buttons.py
```

## 🚀 Installation

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2. Configuration audio (Windows)

Pour PyAudio sous Windows, vous pourriez avoir besoin d'installer le package précompilé :

```bash
pip install pipwin
pipwin install pyaudio
```

## 🎯 Utilisation

### Lancer le programme principal

```bash
python main.py
```

### Tester la manette

```bash
python tests/manuels/test_gamepad_buttons.py
```

### Tester la dictée vocale seule

```bash
python modules/copier_coller.py
```

## 🎮 Configuration de la manette

### Boutons

| Bouton | Action |
|--------|--------|
| **0 (A/X)** | Clic gauche |
| **1 (B/O)** | Clic droit |
| **2 (X/□)** | Touche Entrée |
| **3 (Y/△)** | 🎤 **DICTÉE VOCALE** (maintenir) |
| **4 (LB/L1)** | Alt+Tab (changer fenêtre) |
| **5 (RB/R1)** | Ctrl+W (fermer onglet) |
| **6 (Back)** | Volume - |
| **7 (Start)** | Volume + |

### Joysticks

| Joystick | Action |
|----------|--------|
| **Gauche** | Déplacer le curseur |
| **Droit (Y)** | Scroll haut/bas |

## 🎤 Dictée vocale

1. **Maintenez** le bouton 3 (Y/△)
2. **Parlez** clairement en français
3. **Relâchez** le bouton
4. Le texte reconnu est **automatiquement collé**

## ⚙️ Configuration

Modifiez le fichier `config/voice_config.json` pour personnaliser :

- **Langue** de reconnaissance (`fr-FR`, `en-US`, etc.)
- **Moteur** de reconnaissance (`google`, `whisper`, `sphinx`)
- **Sensibilité** de la souris et du scroll
- **Mapping** des boutons

### Exemple de configuration

```json
{
  "voice": {
    "language": "fr-FR",
    "engine": "google",
    "auto_paste": true
  },
  "gamepad": {
    "voice_button": 3,
    "mouse_sensitivity": 15.0
  }
}
```

## 🧩 Réutiliser les outils

Les outils sont modulaires et peuvent être utilisés indépendamment :

### Enregistrement audio

```python
from outils.audio_recorder import AudioRecorder

recorder = AudioRecorder()
recorder.start_recording()
# ... parler ...
audio_data = recorder.stop_recording()
recorder.save_to_file("mon_audio.wav", audio_data)
```

### Reconnaissance vocale

```python
from outils.speech_recognizer import SpeechRecognizer, RecognitionEngine

recognizer = SpeechRecognizer(engine=RecognitionEngine.GOOGLE, language="fr-FR")
text = recognizer.listen_from_microphone()
print(f"Texte reconnu : {text}")
```

### Presse-papier

```python
from outils.clipboard_manager import ClipboardManager

clipboard = ClipboardManager()
clipboard.copy("Mon texte")
clipboard.paste_from_clipboard()
```

## 🔧 Développement

### Ajouter un nouveau bouton

1. Modifiez `config/voice_config.json`
2. Ou créez une nouvelle fonction dans `modules/gamepad_controller.py`

### Changer le moteur de reconnaissance

Dans `config/voice_config.json`, changez `"engine"` :
- `"google"` : Google Speech (gratuit, nécessite internet)
- `"whisper"` : OpenAI Whisper (local, très précis, nécessite `openai-whisper`)
- `"sphinx"` : CMU Sphinx (offline, moins précis)

## 📝 TODO / Évolutions futures

- [ ] Support de plusieurs langues simultanées
- [ ] Commandes vocales personnalisées
- [ ] Interface graphique de configuration
- [ ] Support des profils de configuration
- [ ] Macros de boutons

## 🐛 Dépannage

### La manette n'est pas détectée

- Vérifiez que la manette est branchée
- Sous Windows : Panneau de configuration → Périphériques de jeu
- Redémarrez le programme après avoir branché la manette

### Erreur PyAudio

```bash
pip uninstall pyaudio
pip install pipwin
pipwin install pyaudio
```

### La reconnaissance vocale ne fonctionne pas

- Vérifiez votre connexion internet (pour Google Speech)
- Testez votre micro dans les paramètres Windows
- Essayez d'augmenter le volume du micro

## 📄 Licence

Ce projet est libre d'utilisation pour un usage personnel et éducatif.

## 👨‍💻 Auteur

JARVIS V2 - Projet de contrôle PC par manette avec IA vocale

---

**Bon contrôle ! 🎮🎤**
