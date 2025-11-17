"""
Module de clic automatique
Combine ImageFinder pour cliquer sur des éléments visuels
"""

import pyautogui
import time
from typing import Optional, Tuple
from pathlib import Path

from outils.image_finder import ImageFinder


class AutoClicker:
    """Classe pour effectuer des clics automatiques sur des éléments visuels"""

    def __init__(self, confidence: float = 0.8, click_delay: float = 0.2):
        """
        Initialise le clicker automatique

        Args:
            confidence: Seuil de confiance pour la recherche d'image (0.0-1.0)
            click_delay: Délai avant le clic en secondes
        """
        self.image_finder = ImageFinder(confidence=confidence)
        self.click_delay = click_delay
        pyautogui.FAILSAFE = True  # Sécurité : coin de l'écran pour arrêter
        pyautogui.PAUSE = 0.1  # Pause entre les actions pyautogui

    def click_on_image(
        self,
        template_path: str,
        button: str = 'left',
        clicks: int = 1,
        region: Optional[Tuple[int, int, int, int]] = None,
        offset: Tuple[int, int] = (0, 0)
    ) -> bool:
        """
        Recherche une image et clique dessus

        Args:
            template_path: Chemin vers l'image à rechercher
            button: Type de clic ('left', 'right', 'middle')
            clicks: Nombre de clics (1 pour simple, 2 pour double)
            region: Région de recherche (x, y, width, height) ou None
            offset: Décalage du point de clic par rapport au centre (offset_x, offset_y)

        Returns:
            True si le clic a été effectué, False sinon
        """
        # Rechercher l'image
        location = self.image_finder.find_image_on_screen(
            template_path,
            region=region
        )

        if not location:
            # Pas de log quand l'image n'est pas trouvée
            return False

        # Calculer le centre
        center_x, center_y = self.image_finder.get_center_point(location)

        # Appliquer l'offset
        click_x = center_x + offset[0]
        click_y = center_y + offset[1]

        # Petite pause avant le clic
        time.sleep(self.click_delay)

        # Effectuer le clic
        try:
            pyautogui.click(click_x, click_y, clicks=clicks, button=button)
            return True

        except Exception as e:
            # Log uniquement en cas d'erreur de clic
            print(f"❌ Erreur lors du clic : {e}")
            return False

    def click_on_first_match(
        self,
        template_path: str,
        button: str = 'left',
        clicks: int = 1
    ) -> bool:
        """
        Recherche et clique sur la première occurrence d'une image

        Args:
            template_path: Chemin vers l'image à rechercher
            button: Type de clic ('left', 'right', 'middle')
            clicks: Nombre de clics

        Returns:
            True si le clic a été effectué, False sinon
        """
        return self.click_on_image(template_path, button=button, clicks=clicks)

    def click_all_matches(
        self,
        template_path: str,
        button: str = 'left',
        delay_between_clicks: float = 0.5
    ) -> int:
        """
        Recherche et clique sur toutes les occurrences d'une image

        Args:
            template_path: Chemin vers l'image à rechercher
            button: Type de clic
            delay_between_clicks: Délai entre chaque clic en secondes

        Returns:
            Nombre de clics effectués
        """
        print(f"\n🔍 Recherche de toutes les occurrences de : {Path(template_path).name}")

        # Rechercher toutes les occurrences
        locations = self.image_finder.find_all_images_on_screen(template_path)

        if not locations:
            print(f"❌ Aucune occurrence trouvée")
            return 0

        clicks_done = 0

        for i, location in enumerate(locations, 1):
            center_x, center_y = self.image_finder.get_center_point(location)
            print(f"🎯 Clic {i}/{len(locations)} sur ({center_x}, {center_y})")

            try:
                time.sleep(self.click_delay)
                pyautogui.click(center_x, center_y, button=button)
                clicks_done += 1
                time.sleep(delay_between_clicks)

            except Exception as e:
                print(f"❌ Erreur lors du clic {i} : {e}")

        print(f"✅ {clicks_done} clic(s) effectué(s)")
        return clicks_done

    def wait_and_click(
        self,
        template_path: str,
        timeout: float = 5.0,
        button: str = 'left',
        clicks: int = 1
    ) -> bool:
        """
        Attend qu'une image apparaisse puis clique dessus

        Args:
            template_path: Chemin vers l'image à rechercher
            timeout: Temps maximum d'attente en secondes
            button: Type de clic
            clicks: Nombre de clics

        Returns:
            True si le clic a été effectué, False si timeout
        """
        print(f"\n🕐 Attente de l'image (timeout: {timeout}s)...")

        # Attendre l'image
        location = self.image_finder.wait_for_image(
            template_path,
            timeout=timeout
        )

        if not location:
            print(f"❌ Timeout : impossible de cliquer")
            return False

        # Cliquer
        center_x, center_y = self.image_finder.get_center_point(location)
        print(f"🎯 Clic {button} sur ({center_x}, {center_y})")

        try:
            time.sleep(self.click_delay)
            pyautogui.click(center_x, center_y, clicks=clicks, button=button)
            print(f"✅ Clic effectué avec succès")
            return True

        except Exception as e:
            print(f"❌ Erreur lors du clic : {e}")
            return False

    def move_to_image(
        self,
        template_path: str,
        duration: float = 0.5,
        offset: Tuple[int, int] = (0, 0)
    ) -> bool:
        """
        Déplace la souris vers une image (sans cliquer)

        Args:
            template_path: Chemin vers l'image
            duration: Durée du mouvement en secondes
            offset: Décalage par rapport au centre

        Returns:
            True si le mouvement a été effectué, False sinon
        """
        location = self.image_finder.find_image_on_screen(template_path)

        if not location:
            return False

        center_x, center_y = self.image_finder.get_center_point(location)
        target_x = center_x + offset[0]
        target_y = center_y + offset[1]

        try:
            pyautogui.moveTo(target_x, target_y, duration=duration)
            print(f"✅ Souris déplacée vers ({target_x}, {target_y})")
            return True

        except Exception as e:
            print(f"❌ Erreur lors du déplacement : {e}")
            return False


def test_auto_clicker():
    """Fonction de test du module"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python auto_clicker.py <chemin_image>")
        print("Exemple: python auto_clicker.py ../assets/images/yes.png")
        return

    template_path = sys.argv[1]
    print("\n" + "=" * 60)
    print(f"🖱️  TEST AUTO-CLICKER")
    print("=" * 60)
    print(f"Image cible : {template_path}")
    print("\n⚠️  Le clic sera effectué dans 3 secondes...")
    print("   Déplacez la souris dans un coin pour annuler (FAILSAFE)\n")

    time.sleep(3)

    clicker = AutoClicker(confidence=0.8)
    success = clicker.click_on_image(template_path)

    if success:
        print("\n✅ Test réussi !")
    else:
        print("\n❌ Test échoué")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_auto_clicker()
