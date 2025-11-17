"""
Module pour la reconnaissance vocale
Support de plusieurs moteurs : Google Speech Recognition, Whisper
"""

import speech_recognition as sr
import io
from typing import Optional, Union
from enum import Enum


class RecognitionEngine(Enum):
    """Moteurs de reconnaissance disponibles"""
    GOOGLE = "google"  # Google Speech Recognition (gratuit, nécessite internet)
    WHISPER = "whisper"  # OpenAI Whisper (local, plus précis mais plus lourd)
    SPHINX = "sphinx"  # CMU Sphinx (offline, moins précis)


class SpeechRecognizer:
    """Classe pour reconnaître la parole depuis l'audio"""

    def __init__(self, engine: RecognitionEngine = RecognitionEngine.GOOGLE, language: str = "fr-FR"):
        """
        Initialise le recognizer

        Args:
            engine: Moteur de reconnaissance à utiliser
            language: Code de langue (ex: "fr-FR", "en-US")
        """
        self.recognizer = sr.Recognizer()
        self.engine = engine
        self.language = language

        # Paramètres de reconnaissance
        self.recognizer.energy_threshold = 300  # Seuil de détection du son
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8  # Secondes de silence pour fin de phrase

    def recognize_from_audio_data(self, audio_data: bytes, sample_rate: int = 16000) -> Optional[str]:
        """
        Reconnaît la parole depuis des données audio brutes

        Args:
            audio_data: Données audio brutes
            sample_rate: Taux d'échantillonnage

        Returns:
            Texte reconnu ou None si erreur
        """
        try:
            # Convertir les données audio en AudioData de speech_recognition
            audio = sr.AudioData(audio_data, sample_rate, 2)  # 2 bytes = 16-bit

            return self._recognize(audio)

        except Exception as e:
            print(f"Erreur lors de la reconnaissance : {e}")
            return None

    def recognize_from_file(self, filename: str) -> Optional[str]:
        """
        Reconnaît la parole depuis un fichier audio

        Args:
            filename: Chemin du fichier audio (WAV, FLAC, etc.)

        Returns:
            Texte reconnu ou None si erreur
        """
        try:
            with sr.AudioFile(filename) as source:
                audio = self.recognizer.record(source)

            return self._recognize(audio)

        except Exception as e:
            print(f"Erreur lors de la lecture du fichier : {e}")
            return None

    def recognize_from_buffer(self, buffer: io.BytesIO) -> Optional[str]:
        """
        Reconnaît la parole depuis un buffer BytesIO

        Args:
            buffer: Buffer contenant l'audio au format WAV

        Returns:
            Texte reconnu ou None si erreur
        """
        try:
            with sr.AudioFile(buffer) as source:
                audio = self.recognizer.record(source)

            return self._recognize(audio)

        except Exception as e:
            print(f"Erreur lors de la lecture du buffer : {e}")
            return None

    def _recognize(self, audio: sr.AudioData) -> Optional[str]:
        """
        Méthode interne pour reconnaître la parole selon le moteur choisi

        Args:
            audio: Données audio au format AudioData

        Returns:
            Texte reconnu ou None si erreur
        """
        try:
            if self.engine == RecognitionEngine.GOOGLE:
                # Google Speech Recognition (gratuit, nécessite internet)
                text = self.recognizer.recognize_google(audio, language=self.language)

            elif self.engine == RecognitionEngine.WHISPER:
                # OpenAI Whisper (local, nécessite le package openai-whisper)
                text = self.recognizer.recognize_whisper(audio, language=self.language.split('-')[0])

            elif self.engine == RecognitionEngine.SPHINX:
                # CMU Sphinx (offline, moins précis)
                text = self.recognizer.recognize_sphinx(audio, language=self.language)

            else:
                print(f"Moteur non supporté : {self.engine}")
                return None

            return text

        except sr.UnknownValueError:
            print("❌ Impossible de comprendre l'audio")
            return None

        except sr.RequestError as e:
            print(f"❌ Erreur de requête au service de reconnaissance : {e}")
            return None

        except Exception as e:
            print(f"❌ Erreur lors de la reconnaissance : {e}")
            return None

    def listen_from_microphone(self, timeout: Optional[float] = None, phrase_time_limit: Optional[float] = None) -> Optional[str]:
        """
        Écoute directement depuis le microphone et reconnaît la parole

        Args:
            timeout: Temps d'attente max avant de commencer l'écoute (secondes)
            phrase_time_limit: Durée max d'enregistrement d'une phrase (secondes)

        Returns:
            Texte reconnu ou None si erreur
        """
        try:
            with sr.Microphone() as source:
                print("🎤 Ajustement au bruit ambiant...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                print("🎤 Parlez maintenant...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

                print("🔄 Reconnaissance en cours...")
                return self._recognize(audio)

        except sr.WaitTimeoutError:
            print("⏱️  Timeout : aucun son détecté")
            return None

        except Exception as e:
            print(f"Erreur lors de l'écoute : {e}")
            return None

    def set_energy_threshold(self, threshold: int):
        """
        Définit le seuil d'énergie pour la détection de la voix

        Args:
            threshold: Seuil (300 par défaut, plus bas = plus sensible)
        """
        self.recognizer.energy_threshold = threshold

    def set_pause_threshold(self, threshold: float):
        """
        Définit la durée de silence pour considérer la fin d'une phrase

        Args:
            threshold: Durée en secondes (0.8 par défaut)
        """
        self.recognizer.pause_threshold = threshold


if __name__ == "__main__":
    # Test simple
    print("\n=== Test de reconnaissance vocale ===\n")

    recognizer = SpeechRecognizer(engine=RecognitionEngine.GOOGLE, language="fr-FR")

    print("Test 1 : Écoute depuis le microphone")
    print("Parlez maintenant (timeout 5 secondes)...\n")

    text = recognizer.listen_from_microphone(timeout=5, phrase_time_limit=10)

    if text:
        print(f"\n✅ Texte reconnu : {text}")
    else:
        print("\n❌ Aucun texte reconnu")
