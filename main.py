"""
JARVIS V2 - Contrôle PC par manette avec reconnaissance vocale
Point d'entrée principal du programme
"""

import sys
import os
import json
from pathlib import Path

# Ajouter le dossier racine au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.gamepad_voice_controller import GamepadVoiceController, get_voice_gamepad_config
from modules.copier_coller import VoiceConfig
from outils.speech_recognizer import RecognitionEngine


def load_config(config_path: str = "config/voice_config.json") -> dict:
    """
    Charge la configuration depuis le fichier JSON

    Args:
        config_path: Chemin du fichier de configuration

    Returns:
        Dictionnaire de configuration
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  Fichier de configuration non trouvé : {config_path}")
        print("Utilisation de la configuration par défaut.")
        return None
    except json.JSONDecodeError as e:
        print(f"⚠️  Erreur de lecture de la configuration : {e}")
        print("Utilisation de la configuration par défaut.")
        return None


def create_voice_config(config_data: dict = None) -> VoiceConfig:
    """
    Crée une VoiceConfig depuis les données de configuration

    Args:
        config_data: Données de configuration JSON

    Returns:
        VoiceConfig configuré
    """
    if not config_data or 'voice' not in config_data:
        return VoiceConfig()

    voice_cfg = config_data['voice']

    # Convertir le nom du moteur en enum
    engine_name = voice_cfg.get('engine', 'google').lower()
    engine = RecognitionEngine.GOOGLE  # Par défaut

    if engine_name == 'whisper':
        engine = RecognitionEngine.WHISPER
    elif engine_name == 'sphinx':
        engine = RecognitionEngine.SPHINX

    return VoiceConfig(
        language=voice_cfg.get('language', 'fr-FR'),
        engine=engine,
        max_duration=voice_cfg.get('max_duration', 10.0),
        auto_paste=voice_cfg.get('auto_paste', True),
        feedback=voice_cfg.get('feedback', True)
    )


def print_banner():
    """Affiche la bannière de démarrage"""
    print("\n" + "=" * 70)
    print(" " * 20 + "🎮 JARVIS V2 🎤")
    print(" " * 10 + "Contrôle PC par manette + Reconnaissance vocale")
    print("=" * 70 + "\n")


def print_help():
    """Affiche l'aide et les commandes"""
    print("=" * 70)
    print("📖 CONFIGURATION DE LA MANETTE")
    print("=" * 70)
    print("\n🎮 BOUTONS:")
    print("  Bouton 0 (A/X)     : Clic gauche")
    print("  Bouton 1 (B/O)     : Clic droit")
    print("  Bouton 2 (X/□)     : Entrée")
    print("  Bouton 3 (Y/△)     : 🎤 DICTÉE VOCALE (maintenir)")
    print("  Bouton 4 (LB/L1)   : Alt+Tab (changer fenêtre)")
    print("  Bouton 5 (RB/R1)   : Ctrl+W (fermer onglet)")
    print("  Bouton 6 (Back)    : Volume -")
    print("  Bouton 7 (Start)   : Volume +")

    print("\n🕹️  JOYSTICKS:")
    print("  Joystick gauche    : Déplacer le curseur de la souris")
    print("  Joystick droit (Y) : Scroll haut/bas")

    print("\n🎤 DICTÉE VOCALE:")
    print("  1. Maintenez le bouton 3 (Y/△)")
    print("  2. Parlez clairement")
    print("  3. Relâchez le bouton")
    print("  4. Le texte reconnu sera automatiquement collé")

    print("\n⚙️  CONFIGURATION:")
    print("  Fichier : config/voice_config.json")
    print("  Langue  : fr-FR (français)")
    print("  Moteur  : Google Speech Recognition")

    print("\n❌ QUITTER:")
    print("  Appuyez sur Ctrl+C")

    print("\n" + "=" * 70 + "\n")


def main():
    """Fonction principale"""

    # Afficher la bannière
    print_banner()

    # Charger la configuration
    config_data = load_config()

    # Créer les configurations
    gamepad_config = get_voice_gamepad_config()
    voice_config = create_voice_config(config_data)

    # Afficher les informations
    print(f"🔧 Configuration chargée")
    print(f"   Langue : {voice_config.language}")
    print(f"   Moteur : {voice_config.engine.value}")
    print(f"   Collage auto : {'Oui' if voice_config.auto_paste else 'Non'}")
    print()

    # Afficher l'aide
    print_help()

    # Créer le contrôleur
    controller = GamepadVoiceController(gamepad_config, voice_config)

    # Connecter la manette
    if not controller.connect():
        print("❌ Impossible de se connecter à la manette.")
        print("\n💡 CONSEILS:")
        print("   - Vérifiez que votre manette est branchée")
        print("   - Sous Windows, vérifiez dans 'Périphériques de jeu'")
        print("   - Essayez de débrancher et rebrancher la manette")
        return

    print("\n" + "=" * 70)
    print(" " * 25 + "✅ PRÊT !")
    print("=" * 70 + "\n")

    try:
        # Lancer la boucle principale
        controller.run()

    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print(" " * 20 + "👋 Arrêt de JARVIS V2")
        print("=" * 70)

    finally:
        # Nettoyage
        controller.cleanup()
        print("\n✅ Ressources libérées. À bientôt !\n")


if __name__ == "__main__":
    main()
