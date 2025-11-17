"""
Module de recherche d'image sur l'écran
Utilise OpenCV et pyautogui pour localiser des images
"""

import cv2
import numpy as np
import pyautogui
from typing import Optional, Tuple, List
from pathlib import Path
import time


class ImageFinder:
    """Classe pour rechercher des images sur l'écran"""

    def __init__(self, confidence: float = 0.8):
        """
        Initialise le chercheur d'image

        Args:
            confidence: Seuil de confiance pour la correspondance (0.0-1.0)
        """
        self.confidence = confidence
        pyautogui.FAILSAFE = True  # Sécurité : déplacer la souris dans un coin pour arrêter

    def find_image_on_screen(
        self,
        template_path: str,
        region: Optional[Tuple[int, int, int, int]] = None,
        grayscale: bool = True
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Recherche une image sur l'écran

        Args:
            template_path: Chemin vers l'image à rechercher
            region: Région de recherche (x, y, width, height) ou None pour tout l'écran
            grayscale: Rechercher en niveaux de gris pour plus de rapidité

        Returns:
            Tuple (x, y, width, height) de la position trouvée ou None si non trouvée
        """
        try:
            # Vérifier que le fichier existe
            if not Path(template_path).exists():
                print(f"❌ Image introuvable : {template_path}")
                return None

            # Chercher l'image sur l'écran
            location = pyautogui.locateOnScreen(
                template_path,
                confidence=self.confidence,
                region=region,
                grayscale=grayscale
            )

            if location:
                # Image trouvée, pas de log ici (sera géré par le niveau supérieur)
                return (location.left, location.top, location.width, location.height)
            else:
                # Pas de log quand l'image n'est pas trouvée
                return None

        except Exception:
            # Pas de log, retourner simplement None
            return None

    def find_all_images_on_screen(
        self,
        template_path: str,
        region: Optional[Tuple[int, int, int, int]] = None,
        grayscale: bool = True
    ) -> List[Tuple[int, int, int, int]]:
        """
        Recherche toutes les occurrences d'une image sur l'écran

        Args:
            template_path: Chemin vers l'image à rechercher
            region: Région de recherche (x, y, width, height) ou None pour tout l'écran
            grayscale: Rechercher en niveaux de gris pour plus de rapidité

        Returns:
            Liste de tuples (x, y, width, height) des positions trouvées
        """
        try:
            # Vérifier que le fichier existe
            if not Path(template_path).exists():
                print(f"❌ Image introuvable : {template_path}")
                return []

            # Chercher toutes les occurrences
            locations = list(pyautogui.locateAllOnScreen(
                template_path,
                confidence=self.confidence,
                region=region,
                grayscale=grayscale
            ))

            if locations:
                print(f"✅ {len(locations)} occurrence(s) trouvée(s)")
                return [(loc.left, loc.top, loc.width, loc.height) for loc in locations]
            else:
                print(f"⚠️  Aucune occurrence trouvée")
                return []

        except Exception as e:
            print(f"❌ Erreur lors de la recherche d'images : {e}")
            return []

    def get_center_point(self, box: Tuple[int, int, int, int]) -> Tuple[int, int]:
        """
        Calcule le point central d'une boîte de délimitation

        Args:
            box: Tuple (x, y, width, height)

        Returns:
            Tuple (center_x, center_y)
        """
        x, y, width, height = box
        return (x + width // 2, y + height // 2)

    def wait_for_image(
        self,
        template_path: str,
        timeout: float = 5.0,
        check_interval: float = 0.5,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Attend qu'une image apparaisse à l'écran

        Args:
            template_path: Chemin vers l'image à rechercher
            timeout: Temps maximum d'attente en secondes
            check_interval: Intervalle entre les vérifications en secondes
            region: Région de recherche ou None pour tout l'écran

        Returns:
            Tuple (x, y, width, height) de la position trouvée ou None si timeout
        """
        start_time = time.time()
        print(f"🔍 Attente de l'image (timeout: {timeout}s)...")

        while time.time() - start_time < timeout:
            location = self.find_image_on_screen(template_path, region=region)
            if location:
                return location
            time.sleep(check_interval)

        print(f"⏱️  Timeout : image non trouvée après {timeout}s")
        return None


def test_image_finder():
    """Fonction de test du module"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python image_finder.py <chemin_image>")
        print("Exemple: python image_finder.py ../assets/images/yes.png")
        return

    template_path = sys.argv[1]
    print(f"\n🔍 Recherche de l'image : {template_path}")
    print("=" * 60)

    finder = ImageFinder(confidence=0.8)

    # Rechercher l'image
    location = finder.find_image_on_screen(template_path)

    if location:
        x, y, w, h = location
        center_x, center_y = finder.get_center_point(location)
        print(f"\n📍 Position : x={x}, y={y}")
        print(f"📐 Dimensions : {w}x{h}")
        print(f"🎯 Centre : ({center_x}, {center_y})")
    else:
        print("\n❌ Image non trouvée sur l'écran")

    print("=" * 60)


if __name__ == "__main__":
    test_image_finder()
