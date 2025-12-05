"""
Module pour la dictée vocale - Copier-Coller par la voix
Combine l'enregistrement audio, la reconnaissance vocale et le presse-papier
"""

import sys
import os

# Ajouter le dossier parent au path pour importer les outils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from outils.audio_recorder import AudioRecorder, AudioConfig
from outils.speech_recognizer import SpeechRecognizer, RecognitionEngine
from outils.clipboard_manager import ClipboardManager
from typing import Optional
from dataclasses import dataclass


@dataclass
class VoiceConfig:
    """Configuration pour la dictée vocale"""
    language: str = "fr-FR"
    engine: RecognitionEngine = RecognitionEngine.GOOGLE
    max_duration: float = 10.0  # Durée max d'enregistrement en secondes
    auto_paste: bool = True  # Coller automatiquement après reconnaissance
    feedback: bool = True  # Afficher les messages de feedback
    ollama_config: dict = None  # Configuration Ollama pour l'IA


class VoiceCopyPaste:
    """Classe principale pour la dictée vocale"""

    def __init__(self, config: Optional[VoiceConfig] = None):
        """
        Initialise le système de dictée vocale

        Args:
            config: Configuration personnalisée (optionnel)
        """
        self.config = config or VoiceConfig()

        # Initialiser les composants
        self.audio_recorder = AudioRecorder(AudioConfig(sample_rate=16000))
        self.speech_recognizer = SpeechRecognizer(
            engine=self.config.engine,
            language=self.config.language
        )
        self.clipboard_manager = ClipboardManager()

        self.is_recording = False
        self.last_recognized_text = None

    def start_voice_input(self) -> Optional[str]:
        """
        Démarre l'enregistrement vocal, reconnaît et copie le texte

        Returns:
            Texte reconnu ou None si erreur
        """
        if self.is_recording:
            if self.config.feedback:
                print("⚠️  Enregistrement déjà en cours !")
            return None

        try:
            # 1. Démarrer l'enregistrement
            if self.config.feedback:
                print("🎤 Enregistrement démarré - Parlez maintenant...")

            success = self.audio_recorder.start_recording()
            if not success:
                return None

            self.is_recording = True
            return None  # L'enregistrement continue...

        except Exception as e:
            if self.config.feedback:
                print(f"❌ Erreur lors du démarrage : {e}")
            return None

    def stop_voice_input(self) -> Optional[str]:
        """
        Arrête l'enregistrement, reconnaît la parole et copie le texte

        Returns:
            Texte reconnu ou None si erreur
        """
        if not self.is_recording:
            if self.config.feedback:
                print("⚠️  Aucun enregistrement en cours !")
            return None

        try:
            # 1. Arrêter l'enregistrement
            audio_data = self.audio_recorder.stop_recording()
            self.is_recording = False

            if not audio_data:
                if self.config.feedback:
                    print("❌ Aucune donnée audio enregistrée")
                return None

            # 2. Reconnaissance vocale
            if self.config.feedback:
                print("🔄 Reconnaissance en cours...")

            # Convertir en buffer WAV
            audio_buffer = self.audio_recorder.get_audio_buffer(audio_data)

            # Reconnaître la parole
            text = self.speech_recognizer.recognize_from_buffer(audio_buffer)

            if not text:
                if self.config.feedback:
                    print("❌ Impossible de reconnaître la parole")
                return None

            # 3. Copier dans le presse-papier
            self.last_recognized_text = text

            if self.config.feedback:
                print(f"✅ Texte reconnu : {text}")

            self.clipboard_manager.copy(text)

            # 4. Coller automatiquement si configuré
            if self.config.auto_paste:
                if self.config.feedback:
                    print("📋 Collage automatique...")
                self.clipboard_manager.paste_from_clipboard()

            return text

        except Exception as e:
            self.is_recording = False
            if self.config.feedback:
                print(f"❌ Erreur lors de l'arrêt : {e}")
            return None

    def quick_voice_input(self, duration: float = 5.0) -> Optional[str]:
        """
        Enregistre pendant une durée fixe, puis reconnaît et copie

        Args:
            duration: Durée d'enregistrement en secondes

        Returns:
            Texte reconnu ou None si erreur
        """
        try:
            if self.config.feedback:
                print(f"🎤 Enregistrement de {duration} secondes - Parlez maintenant...")

            # Enregistrer pendant la durée spécifiée
            audio_data = self.audio_recorder.record_for_duration(duration)

            if not audio_data:
                if self.config.feedback:
                    print("❌ Aucune donnée audio")
                return None

            # Reconnaissance vocale
            if self.config.feedback:
                print("🔄 Reconnaissance en cours...")

            audio_buffer = self.audio_recorder.get_audio_buffer(audio_data)
            text = self.speech_recognizer.recognize_from_buffer(audio_buffer)

            if not text:
                if self.config.feedback:
                    print("❌ Impossible de reconnaître la parole")
                return None

            # Copier et coller
            self.last_recognized_text = text

            if self.config.feedback:
                print(f"✅ Texte reconnu : {text}")

            self.clipboard_manager.copy(text)

            if self.config.auto_paste:
                if self.config.feedback:
                    print("📋 Collage automatique...")
                self.clipboard_manager.paste_from_clipboard()

            return text

        except Exception as e:
            if self.config.feedback:
                print(f"❌ Erreur : {e}")
            return None

    def get_last_text(self) -> Optional[str]:
        """Retourne le dernier texte reconnu"""
        return self.last_recognized_text

    def cleanup(self):
        """Nettoie les ressources"""
        if self.is_recording:
            self.audio_recorder.stop_recording()
            self.is_recording = False

        self.audio_recorder.cleanup()


if __name__ == "__main__":
    # Test simple
    print("\n=== Test de la dictée vocale ===\n")

    config = VoiceConfig(
        language="fr-FR",
        engine=RecognitionEngine.GOOGLE,
        auto_paste=False,  # Pas de collage auto pour le test
        feedback=True
    )

    voice_paste = VoiceCopyPaste(config)

    print("Mode 1 : Enregistrement manuel (start/stop)")
    print("Mode 2 : Enregistrement rapide (5 secondes)\n")

    choice = input("Choisissez un mode (1 ou 2) [1]: ").strip()

    if choice == "2":
        # Mode rapide
        text = voice_paste.quick_voice_input(duration=5.0)
    else:
        # Mode manuel
        import time

        voice_paste.start_voice_input()
        print("\nParlez pendant 3 secondes...\n")
        time.sleep(3)
        text = voice_paste.stop_voice_input()

    if text:
        print(f"\n📋 Le texte est maintenant dans le presse-papier : {text}")
    else:
        print("\n❌ Échec de la reconnaissance")

    voice_paste.cleanup()
