"""
Test de la fonctionnalité de recherche et clic sur yes.png
"""

import sys
import os

# Ajouter le dossier racine au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from outils.auto_clicker import AutoClicker
from pathlib import Path
import time


def test_yes_clicker():
    """Test de recherche et clic sur yes.png"""

    print("\n" + "=" * 70)
    print(" " * 20 + "🖱️  TEST CLICKER YES.PNG")
    print("=" * 70)

    # Chemin vers l'image yes.png
    yes_image_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "assets", "images", "yes.png"
    )

    print(f"\n📁 Chemin de l'image : {yes_image_path}")

    # Vérifier que l'image existe
    if not Path(yes_image_path).exists():
        print(f"❌ ERREUR : L'image n'existe pas !")
        print(f"\n💡 Assurez-vous que le fichier existe :")
        print(f"   {yes_image_path}")
        return

    print(f"✅ Image trouvée sur le disque")

    # Créer le clicker
    clicker = AutoClicker(confidence=0.8, click_delay=0.2)

    print("\n" + "=" * 70)
    print("⚠️  INSTRUCTIONS :")
    print("   1. Ouvrez une fenêtre avec l'image yes.png visible à l'écran")
    print("   2. Le test va rechercher et cliquer sur cette image")
    print("   3. Vous avez 5 secondes pour préparer votre écran...")
    print("=" * 70 + "\n")

    # Compte à rebours
    for i in range(5, 0, -1):
        print(f"⏱️  Début dans {i}...")
        time.sleep(1)

    print("\n🔍 Recherche de l'image sur l'écran...\n")

    # Tenter de cliquer sur l'image
    success = clicker.click_on_image(yes_image_path, button='left', clicks=1)

    print("\n" + "=" * 70)
    if success:
        print("✅ TEST RÉUSSI : Clic effectué sur yes.png")
    else:
        print("❌ TEST ÉCHOUÉ : Image non trouvée sur l'écran")
        print("\n💡 CONSEILS :")
        print("   - Assurez-vous que l'image yes.png est visible à l'écran")
        print("   - L'image doit être identique au fichier de référence")
        print("   - Essayez d'augmenter la taille de l'image affichée")
        print("   - Vérifiez que l'image n'est pas déformée ou redimensionnée")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    test_yes_clicker()
