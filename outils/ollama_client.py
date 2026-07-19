"""
Client pour interagir avec Ollama API locale
Permet d'envoyer des questions et recevoir des réponses de l'IA
"""

import requests
import json
from typing import Optional, Dict, Any


class OllamaClient:
    """Client pour communiquer avec l'API Ollama"""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "gemma3:4b",
        temperature: float = 0.7,
        max_tokens: int = 500,
        timeout: int = 60
    ):
        """
        Initialise le client Ollama

        Args:
            base_url: URL de base de l'API Ollama
            model: Nom du modèle à utiliser (ex: gemma3:4b)
            temperature: Température pour la génération (0-1)
            max_tokens: Nombre maximum de tokens dans la réponse
            timeout: Timeout pour les requêtes en secondes
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    def ask(self, question: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """
        Envoie une question à l'IA et récupère la réponse

        Args:
            question: Question à poser à l'IA
            system_prompt: Prompt système optionnel pour configurer le comportement

        Returns:
            Réponse de l'IA ou None en cas d'erreur
        """
        try:
            url = f"{self.base_url}/api/generate"

            # Construire le prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\nQuestion: {question}\n\nRéponse:"
            else:
                full_prompt = question

            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            }

            print(f"[OLLAMA] Envoi de la question au modèle {self.model}...")

            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                answer = result.get('response', '').strip()

                if answer:
                    print(f"[OLLAMA] ✅ Réponse reçue ({len(answer)} caractères)")
                    return answer
                else:
                    print("[OLLAMA] ❌ Réponse vide reçue")
                    return None
            else:
                print(f"[OLLAMA] ❌ Erreur HTTP {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            print("[OLLAMA] ❌ Timeout : le serveur Ollama ne répond pas")
            return None

        except requests.exceptions.ConnectionError:
            print("[OLLAMA] ❌ Erreur de connexion : vérifiez qu'Ollama est lancé")
            return None

        except Exception as e:
            print(f"[OLLAMA] ❌ Erreur : {e}")
            return None

    def is_available(self) -> bool:
        """
        Vérifie si le serveur Ollama est disponible

        Returns:
            True si disponible, False sinon
        """
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False

    def list_models(self) -> Optional[list]:
        """
        Liste les modèles disponibles sur Ollama

        Returns:
            Liste des modèles ou None en cas d'erreur
        """
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                return models
            else:
                return None

        except Exception as e:
            print(f"[OLLAMA] ❌ Erreur lors de la récupération des modèles : {e}")
            return None


if __name__ == "__main__":
    print("\n=== Test du client Ollama ===\n")

    client = OllamaClient(model="gemma3:4b")

    if client.is_available():
        print("✅ Serveur Ollama disponible\n")

        models = client.list_models()
        if models:
            print(f"Modèles disponibles : {', '.join(models)}\n")

        question = "Quelle est la capitale de la France ?"
        print(f"Question : {question}\n")

        answer = client.ask(question)

        if answer:
            print(f"\nRéponse :\n{answer}")
        else:
            print("\n❌ Pas de réponse reçue")

    else:
        print("❌ Serveur Ollama non disponible")
        print("Vérifiez qu'Ollama est lancé avec : ollama serve")
