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
import mss


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

    def _find_image_with_mss(
        self,
        template_path: str,
        grayscale: bool = True
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Recherche une image en utilisant mss pour capturer chaque écran

        Args:
            template_path: Chemin vers l'image à rechercher
            grayscale: Rechercher en niveaux de gris

        Returns:
            Tuple (x, y, width, height) de la position trouvée ou None
        """
        try:
            template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR)
            if template is None:
                print(f"❌ Impossible de charger l'image : {template_path}")
                return None

            template_h, template_w = template.shape[:2]

            with mss.mss() as sct:
                monitors = sct.monitors[1:]
                print(f"[ImageFinder DEBUG] Recherche sur {len(monitors)} écran(s) avec mss...")

                for i, monitor in enumerate(monitors, 1):
                    print(f"[ImageFinder DEBUG] Écran {i}: {monitor['width']}x{monitor['height']} à ({monitor['left']}, {monitor['top']})")

                    screenshot = sct.grab(monitor)
                    img = np.array(screenshot)
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                    if grayscale:
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                    result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                    if max_val >= self.confidence:
                        x = monitor['left'] + max_loc[0]
                        y = monitor['top'] + max_loc[1]
                        print(f"[ImageFinder DEBUG] ✅ Image trouvée sur écran {i} à ({x}, {y}) - confiance: {max_val:.2f}")
                        return (x, y, template_w, template_h)
                    else:
                        print(f"[ImageFinder DEBUG] ❌ Image non trouvée sur écran {i} - confiance max: {max_val:.2f}")

                print(f"[ImageFinder DEBUG] Image non trouvée sur aucun des {len(monitors)} écrans")
                return None

        except Exception as e:
            print(f"[ImageFinder DEBUG] Erreur mss: {e}")
            import traceback
            traceback.print_exc()
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
            if not Path(template_path).exists():
                print(f"❌ Image introuvable : {template_path}")
                return None

            if region is None and self.search_all_screens:
                return self._find_image_with_mss(template_path, grayscale)

            location = pyautogui.locateOnScreen(
                template_path,
                confidence=self.confidence,
                region=region,
                grayscale=grayscale
            )

            if location:
                return (location.left, location.top, location.width, location.height)
            else:
                return None

        except Exception:
            return None

    def _find_all_images_with_mss(
        self,
        template_path: str,
        grayscale: bool = True,
        threshold: float = None
    ) -> List[Tuple[int, int, int, int]]:
        """
        Recherche toutes les occurrences d'une image en utilisant mss

        Args:
            template_path: Chemin vers l'image à rechercher
            grayscale: Rechercher en niveaux de gris
            threshold: Seuil de confiance (utilise self.confidence par défaut)

        Returns:
            Liste de tuples (x, y, width, height) des positions trouvées
        """
        try:
            template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR)
            if template is None:
                print(f"❌ Impossible de charger l'image : {template_path}")
                return []

            template_h, template_w = template.shape[:2]
            if threshold is None:
                threshold = self.confidence

            all_locations = []

            with mss.mss() as sct:
                monitors = sct.monitors[1:]

                for i, monitor in enumerate(monitors, 1):
                    screenshot = sct.grab(monitor)
                    img = np.array(screenshot)
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                    if grayscale:
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                    result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
                    locations = np.where(result >= threshold)

                    for pt in zip(*locations[::-1]):
                        x = monitor['left'] + pt[0]
                        y = monitor['top'] + pt[1]
                        all_locations.append((x, y, template_w, template_h))

            if all_locations:
                print(f"✅ {len(all_locations)} occurrence(s) trouvée(s)")
            else:
                print(f"⚠️  Aucune occurrence trouvée")

            return all_locations

        except Exception as e:
            print(f"❌ Erreur lors de la recherche d'images : {e}")
            return []

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
            if not Path(template_path).exists():
                print(f"❌ Image introuvable : {template_path}")
                return []

            if region is None and self.search_all_screens:
                return self._find_all_images_with_mss(template_path, grayscale)

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
