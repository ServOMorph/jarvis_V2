"""
Module de synthèse vocale (Text-to-Speech)
Utilise pyttsx3 pour une synthèse locale sans connexion internet
"""

import pyttsx3
from typing import Optional


class TextToSpeech:
    """Classe pour convertir du texte en parole"""

    def __init__(self, language: str = "fr", rate: int = 180, volume: float = 1.0):
        """
        Initialise le moteur TTS

        Args:
            language: Code de langue (ex: "fr", "en")
            rate: Vitesse de lecture en mots par minute (150-200 recommandé)
            volume: Volume (0.0 à 1.0)
        """
        try:
            self.engine = pyttsx3.init()
            self.language = language
            self.rate = rate
            self.volume = volume

            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)

            self._set_french_voice()

            print("[TTS] ✅ Moteur de synthèse vocale initialisé")

        except Exception as e:
            print(f"[TTS] ❌ Erreur d'initialisation : {e}")
            self.engine = None

    def _set_french_voice(self):
        """Configure la voix française si disponible"""
        try:
            voices = self.engine.getProperty('voices')

            for voice in voices:
                if 'french' in voice.name.lower() or 'fr' in voice.languages:
                    self.engine.setProperty('voice', voice.id)
                    print(f"[TTS] Voix sélectionnée : {voice.name}")
                    return

            if voices:
                self.engine.setProperty('voice', voices[0].id)
                print(f"[TTS] Voix par défaut : {voices[0].name}")

        except Exception as e:
            print(f"[TTS] ⚠️  Configuration voix : {e}")

    def speak(self, text: str, wait: bool = True) -> bool:
        """
        Lit le texte à voix haute

        Args:
            text: Texte à lire
            wait: Si True, attend la fin de la lecture

        Returns:
            True si succès, False sinon
        """
        if not self.engine:
            print("[TTS] ❌ Moteur TTS non disponible")
            return False

        if not text or not text.strip():
            print("[TTS] ❌ Texte vide")
            return False

        try:
            print(f"[TTS] 🔊 Lecture : {text[:100]}{'...' if len(text) > 100 else ''}")
            self.engine.say(text)

            if wait:
                self.engine.runAndWait()

            return True

        except Exception as e:
            print(f"[TTS] ❌ Erreur de lecture : {e}")
            return False

    def stop(self):
        """Arrête la lecture en cours"""
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass

    def set_rate(self, rate: int):
        """
        Modifie la vitesse de lecture

        Args:
            rate: Vitesse en mots par minute
        """
        if self.engine:
            self.rate = rate
            self.engine.setProperty('rate', rate)

    def set_volume(self, volume: float):
        """
        Modifie le volume

        Args:
            volume: Volume entre 0.0 et 1.0
        """
        if self.engine:
            self.volume = max(0.0, min(1.0, volume))
            self.engine.setProperty('volume', self.volume)

    def list_voices(self):
        """Liste les voix disponibles"""
        if not self.engine:
            print("[TTS] ❌ Moteur TTS non disponible")
            return

        try:
            voices = self.engine.getProperty('voices')
            print("\n[TTS] Voix disponibles :")
            for i, voice in enumerate(voices):
                print(f"  {i+1}. {voice.name} ({voice.languages})")
        except Exception as e:
            print(f"[TTS] ❌ Erreur : {e}")

    def cleanup(self):
        """Nettoie les ressources"""
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass


if __name__ == "__main__":
    print("\n=== Test de synthèse vocale ===\n")

    tts = TextToSpeech(rate=180, volume=1.0)

    tts.list_voices()

    text = "Bonjour, je suis l'assistant vocal de Jarvis. Comment puis-je vous aider ?"

    print(f"\n[TEST] Lecture du texte : {text}\n")
    tts.speak(text)

    print("\n✅ Test terminé")
