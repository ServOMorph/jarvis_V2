"""
JARVIS V2 - Contrôle PC par manette avec reconnaissance vocale
Point d'entrée principal du programme
"""

import sys
import os
import json
import threading
import tkinter as tk
from pathlib import Path

# Ajouter le dossier racine au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.gamepad_voice_controller import GamepadVoiceController, get_voice_gamepad_config
from modules.copier_coller import VoiceConfig
from outils.speech_recognizer import RecognitionEngine
from ui.gamepad_controls_ui import ModernGamepadUI


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
    print("\n🎮 BOUTONS ACTUELLEMENT CONFIGURÉS:")
    print("  Bouton 1 (B)       : 🤖 MODE CLAUDE IA (toggle on/off)")
    print("  Bouton 3 (X)       : 🎤 DICTÉE VOCALE (maintenir)")

    print("\n🕹️  JOYSTICKS:")
    print("  Joystick gauche    : Déplacer le curseur de la souris")
    print("  Joystick droit (Y) : Scroll haut/bas")

    print("\n🤖 MODE CLAUDE IA:")
    print("  Appuyez sur le bouton B pour activer/désactiver")
    print("  Le statut s'affiche dans l'interface graphique")

    print("\n🎤 DICTÉE VOCALE:")
    print("  1. Maintenez le bouton X (bouton 3)")
    print("  2. Parlez clairement")
    print("  3. Relâchez le bouton")
    print("  4. Le texte reconnu sera automatiquement collé")

    print("\n⚙️  CONFIGURATION:")
    print("  Fichier : config/voice_config.json")
    print("  Langue  : fr-FR (français)")
    print("  Moteur  : Google Speech Recognition")

    print("\n📺 INTERFACE:")
    print("  Une fenêtre s'ouvrira pour visualiser les contrôles en temps réel")

    print("\n❌ QUITTER:")
    print("  Appuyez sur Ctrl+C ou fermez la fenêtre UI")

    print("\n" + "=" * 70 + "\n")


def launch_ui(ui_root_ref, config_path="config/voice_config.json", controller_ref=None):
    """Lance l'interface graphique dans le thread principal"""
    root = tk.Tk()
    ui_root_ref[0] = root
    app = ModernGamepadUI(root, config_path=config_path)

    # Lier l'UI au contrôleur pour synchroniser l'état
    if controller_ref:
        app.set_controller(controller_ref[0])

    def on_closing():
        app.cleanup()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


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

    # Références pour la fenêtre UI et le contrôleur
    ui_root_ref = [None]
    controller_ref = [controller]

    # Lancer l'interface graphique dans un thread séparé
    print("🚀 Lancement de l'interface graphique...\n")
    ui_thread = threading.Thread(
        target=launch_ui,
        args=(ui_root_ref, "config/voice_config.json", controller_ref),
        daemon=True
    )
    ui_thread.start()

    # Petit délai pour laisser l'UI s'initialiser
    import time
    time.sleep(0.5)

    try:
        # Lancer la boucle principale du contrôleur
        controller.run()

    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print(" " * 20 + "👋 Arrêt de JARVIS V2")
        print("=" * 70)

    finally:
        # Nettoyage
        controller.cleanup()

        # Fermer la fenêtre UI si elle est ouverte
        if ui_root_ref[0]:
            try:
                ui_root_ref[0].quit()
            except:
                pass

        print("\n✅ Ressources libérées. À bientôt !\n")


if __name__ == "__main__":
    main()
