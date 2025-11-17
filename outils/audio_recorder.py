"""
Module pour l'enregistrement audio du microphone
Utilise pyaudio pour capturer l'audio en temps réel
"""

import pyaudio
import wave
import threading
import time
from typing import Optional
from dataclasses import dataclass
import io


@dataclass
class AudioConfig:
    """Configuration pour l'enregistrement audio"""
    sample_rate: int = 16000  # Hz (16kHz recommandé pour la reconnaissance vocale)
    channels: int = 1  # Mono
    chunk_size: int = 1024  # Taille du buffer
    format: int = pyaudio.paInt16  # 16-bit audio
    device_index: Optional[int] = None  # None = micro par défaut


class AudioRecorder:
    """Classe pour enregistrer l'audio du microphone"""

    def __init__(self, config: Optional[AudioConfig] = None):
        """
        Initialise le recorder audio

        Args:
            config: Configuration personnalisée (optionnel)
        """
        self.config = config or AudioConfig()
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.is_recording = False
        self.recording_thread = None

    def list_devices(self):
        """Liste tous les périphériques audio disponibles"""
        print("\n=== Périphériques audio disponibles ===")
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:  # Seulement les périphériques d'entrée
                print(f"[{i}] {info['name']} (Canaux: {info['maxInputChannels']})")

    def get_default_device_info(self):
        """Retourne les infos du périphérique par défaut"""
        try:
            default_device = self.audio.get_default_input_device_info()
            return default_device
        except Exception as e:
            print(f"Erreur lors de la récupération du périphérique par défaut : {e}")
            return None

    def start_recording(self) -> bool:
        """
        Démarre l'enregistrement audio

        Returns:
            True si l'enregistrement a démarré avec succès
        """
        if self.is_recording:
            print("Enregistrement déjà en cours !")
            return False

        try:
            # Ouvrir le stream audio
            self.stream = self.audio.open(
                format=self.config.format,
                channels=self.config.channels,
                rate=self.config.sample_rate,
                input=True,
                input_device_index=self.config.device_index,
                frames_per_buffer=self.config.chunk_size
            )

            self.frames = []
            self.is_recording = True

            # Démarrer l'enregistrement dans un thread séparé
            self.recording_thread = threading.Thread(target=self._record)
            self.recording_thread.start()

            print("🎤 Enregistrement démarré...")
            return True

        except Exception as e:
            print(f"Erreur lors du démarrage de l'enregistrement : {e}")
            return False

    def _record(self):
        """Méthode interne pour enregistrer l'audio (thread)"""
        while self.is_recording:
            try:
                data = self.stream.read(self.config.chunk_size, exception_on_overflow=False)
                self.frames.append(data)
            except Exception as e:
                print(f"Erreur lors de la lecture audio : {e}")
                break

    def stop_recording(self) -> bytes:
        """
        Arrête l'enregistrement et retourne les données audio

        Returns:
            Données audio brutes (bytes)
        """
        if not self.is_recording:
            print("Aucun enregistrement en cours !")
            return b''

        self.is_recording = False

        # Attendre la fin du thread d'enregistrement
        if self.recording_thread:
            self.recording_thread.join()

        # Fermer le stream
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        print("⏹️  Enregistrement arrêté.")

        # Retourner les données audio
        return b''.join(self.frames)

    def save_to_file(self, filename: str, audio_data: Optional[bytes] = None):
        """
        Sauvegarde l'audio dans un fichier WAV

        Args:
            filename: Nom du fichier (avec extension .wav)
            audio_data: Données audio à sauvegarder (si None, utilise self.frames)
        """
        if audio_data is None:
            audio_data = b''.join(self.frames)

        if not audio_data:
            print("Aucune donnée audio à sauvegarder !")
            return

        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.config.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.config.format))
                wf.setframerate(self.config.sample_rate)
                wf.writeframes(audio_data)

            print(f"💾 Audio sauvegardé dans : {filename}")

        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")

    def get_audio_buffer(self, audio_data: Optional[bytes] = None) -> io.BytesIO:
        """
        Retourne un buffer BytesIO avec les données audio au format WAV

        Args:
            audio_data: Données audio (si None, utilise self.frames)

        Returns:
            Buffer BytesIO contenant l'audio au format WAV
        """
        if audio_data is None:
            audio_data = b''.join(self.frames)

        buffer = io.BytesIO()

        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(self.config.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.config.format))
            wf.setframerate(self.config.sample_rate)
            wf.writeframes(audio_data)

        buffer.seek(0)
        return buffer

    def record_for_duration(self, duration: float) -> bytes:
        """
        Enregistre pendant une durée spécifique

        Args:
            duration: Durée en secondes

        Returns:
            Données audio brutes
        """
        self.start_recording()
        time.sleep(duration)
        return self.stop_recording()

    def cleanup(self):
        """Nettoie les ressources"""
        if self.is_recording:
            self.stop_recording()

        if self.stream:
            self.stream.close()

        self.audio.terminate()

    def __del__(self):
        """Destructeur pour nettoyer les ressources"""
        self.cleanup()


if __name__ == "__main__":
    # Test simple
    recorder = AudioRecorder()

    print("\n=== Test de l'enregistreur audio ===\n")

    # Lister les périphériques
    recorder.list_devices()

    # Afficher le périphérique par défaut
    default = recorder.get_default_device_info()
    if default:
        print(f"\nPériphérique par défaut : {default['name']}")

    # Enregistrer 3 secondes
    print("\nEnregistrement de 3 secondes...")
    print("Parlez maintenant !\n")

    recorder.start_recording()
    time.sleep(3)
    audio_data = recorder.stop_recording()

    # Sauvegarder
    recorder.save_to_file("test_recording.wav", audio_data)

    recorder.cleanup()
