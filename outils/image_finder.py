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
from screeninfo import get_monitors


class ImageFinder:
    """Classe pour rechercher des images sur l'écran"""

    def __init__(self, confidence: float = 0.8, search_all_screens: bool = True):
        """
        Initialise le chercheur d'image

        Args:
            confidence: Seuil de confiance pour la correspondance (0.0-1.0)
            search_all_screens: Si True, recherche sur tous les écrans (multi-moniteurs)
        """
        self.confidence = confidence
        self.search_all_screens = search_all_screens
        pyautogui.FAILSAFE = True  # Sécurité : déplacer la souris dans un coin pour arrêter

        # Détecter la région globale de tous les écrans
        self.all_screens_region = self._get_all_screens_region() if search_all_screens else None

        if self.all_screens_region:
            x, y, width, height = self.all_screens_region
            print(f"[ImageFinder] 🖥️ Région multi-écrans détectée : {width}x{height} (x={x}, y={y})")

    def _get_all_screens_region(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Calcule la région englobant tous les écrans disponibles

        Returns:
            Tuple (x, y, width, height) de la région totale ou None si erreur
        """
        try:
            monitors = get_monitors()

            if not monitors:
                print("[ImageFinder] ⚠️ Aucun moniteur détecté, utilisation de l'écran par défaut")
                return None

            # Trouver les coordonnées min/max de tous les écrans
            min_x = min(m.x for m in monitors)
            min_y = min(m.y for m in monitors)
            max_x = max(m.x + m.width for m in monitors)
            max_y = max(m.y + m.height for m in monitors)

            width = max_x - min_x
            height = max_y - min_y

            # Afficher les écrans détectés
            print(f"[ImageFinder] 📺 {len(monitors)} écran(s) détecté(s):")
            for i, m in enumerate(monitors, 1):
                print(f"  Écran {i}: {m.width}x{m.height} à ({m.x}, {m.y})")

            return (min_x, min_y, width, height)

        except Exception as e:
            print(f"[ImageFinder] ❌ Erreur lors de la détection des écrans : {e}")
            return None

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
            region: Région de recherche (x, y, width, height) ou None pour utiliser tous les écrans
            grayscale: Rechercher en niveaux de gris pour plus de rapidité

        Returns:
            Tuple (x, y, width, height) de la position trouvée ou None si non trouvée
        """
        try:
            # Vérifier que le fichier existe
            if not Path(template_path).exists():
                print(f"❌ Image introuvable : {template_path}")
                return None

            # Si aucune région n'est spécifiée et que search_all_screens est activé,
            # chercher sur chaque écran individuellement
            if region is None and self.search_all_screens:
                try:
                    monitors = get_monitors()
                    print(f"[ImageFinder DEBUG] Recherche sur {len(monitors)} écran(s)...")

                    for i, monitor in enumerate(monitors, 1):
                        # Définir la région pour cet écran spécifique
                        screen_region = (monitor.x, monitor.y, monitor.width, monitor.height)
                        print(f"[ImageFinder DEBUG] Écran {i}: région={screen_region}")

                        # Chercher sur cet écran
                        location = pyautogui.locateOnScreen(
                            template_path,
                            confidence=self.confidence,
                            region=screen_region,
                            grayscale=grayscale
                        )

                        if location:
                            # Image trouvée sur cet écran
                            print(f"[ImageFinder DEBUG] ✅ Image trouvée sur écran {i} à ({location.left}, {location.top})")
                            return (location.left, location.top, location.width, location.height)
                        else:
                            print(f"[ImageFinder DEBUG] ❌ Image non trouvée sur écran {i}")

                    # Image non trouvée sur aucun écran
                    print(f"[ImageFinder DEBUG] Image non trouvée sur aucun des {len(monitors)} écrans")
                    return None

                except Exception as e:
                    # Si la recherche multi-écrans échoue, fallback sur la méthode standard
                    print(f"[ImageFinder DEBUG] Erreur multi-écrans: {e}")
                    import traceback
                    traceback.print_exc()
                    pass

            # Méthode standard (région spécifiée ou search_all_screens désactivé)
            location = pyautogui.locateOnScreen(
                template_path,
                confidence=self.confidence,
                region=region,
                grayscale=grayscale
            )

            if location:
                # Image trouvée
                return (location.left, location.top, location.width, location.height)
            else:
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
            region: Région de recherche (x, y, width, height) ou None pour utiliser tous les écrans
            grayscale: Rechercher en niveaux de gris pour plus de rapidité

        Returns:
            Liste de tuples (x, y, width, height) des positions trouvées
        """
        try:
            # Vérifier que le fichier existe
            if not Path(template_path).exists():
                print(f"❌ Image introuvable : {template_path}")
                return []

            all_locations = []

            # Si aucune région n'est spécifiée et que search_all_screens est activé,
            # chercher sur chaque écran individuellement
            if region is None and self.search_all_screens:
                try:
                    monitors = get_monitors()
                    for monitor in monitors:
                        # Définir la région pour cet écran spécifique
                        screen_region = (monitor.x, monitor.y, monitor.width, monitor.height)

                        # Chercher toutes les occurrences sur cet écran
                        locations = list(pyautogui.locateAllOnScreen(
                            template_path,
                            confidence=self.confidence,
                            region=screen_region,
                            grayscale=grayscale
                        ))

                        # Ajouter les résultats
                        all_locations.extend([(loc.left, loc.top, loc.width, loc.height) for loc in locations])

                    if all_locations:
                        print(f"✅ {len(all_locations)} occurrence(s) trouvée(s)")
                        return all_locations
                    else:
                        print(f"⚠️  Aucune occurrence trouvée")
                        return []

                except Exception:
                    # Si la recherche multi-écrans échoue, fallback sur la méthode standard
                    pass

            # Méthode standard (région spécifiée ou search_all_screens désactivé)
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
