"""
Test de la fonctionnalité de recherche et clic CONTINU sur yes.png
Simule le maintien du bouton B
"""

import sys
import os

# Ajouter le dossier racine au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from outils.auto_clicker import AutoClicker
from pathlib import Path
import time
import threading


def continuous_click_test(stop_event, duration=10):
    """
    Test de clic continu pendant une durée donnée

    Args:
        stop_event: Event pour arrêter la boucle
        duration: Durée du test en secondes
    """
    # Chemin vers l'image yes.png
    yes_image_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "assets", "images", "yes.png"
    )

    # Vérifier que l'image existe
    if not Path(yes_image_path).exists():
        print(f"❌ ERREUR : L'image n'existe pas !")
        return

    clicker = AutoClicker(confidence=0.8, click_delay=0.2)

    print(f"\n[TEST] 🔍 Recherche continue ACTIVÉE")
    print(f"[TEST] Durée du test : {duration} secondes\n")

    search_count = 0
    click_count = 0
    start_time = time.time()

    while not stop_event.is_set() and (time.time() - start_time) < duration:
        search_count += 1
        print(f"[TEST] 🔍 Recherche #{search_count}...")

        success = clicker.click_on_image(
            yes_image_path,
            button='left',
            clicks=1
        )

        if success:
            click_count += 1
            print(f"[TEST] ✅ Clic #{click_count} effectué sur yes.png")
        else:
            print(f"[TEST] ⚠️  Image non trouvée (recherche #{search_count})")

        # Pause entre les recherches
        if stop_event.wait(timeout=0.3):
            break

    print(f"\n[TEST] ⏹️  Recherche continue ARRÊTÉE")
    print(f"[TEST] 📊 Résumé : {click_count} clic(s) sur {search_count} recherche(s)")
    print(f"[TEST] ⏱️  Durée : {time.time() - start_time:.1f}s\n")


def main():
    """Fonction principale du test"""

    print("\n" + "=" * 70)
    print(" " * 15 + "🖱️  TEST CLICKER CONTINU (yes.png)")
    print("=" * 70)

    print("\n⚠️  INSTRUCTIONS :")
    print("   1. Ouvrez une fenêtre avec l'image yes.png visible")
    print("   2. Le test va chercher et cliquer en continu pendant 10 secondes")
    print("   3. Vous pouvez aussi arrêter avec Ctrl+C")
    print("\n💡 ASTUCE : Affichez l'image yes.png dans un navigateur ou une visionneuse")
    print("=" * 70 + "\n")

    # Compte à rebours
    for i in range(5, 0, -1):
        print(f"⏱️  Début dans {i}...")
        time.sleep(1)

    # Event pour arrêter le test
    stop_event = threading.Event()

    try:
        continuous_click_test(stop_event, duration=10)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption par l'utilisateur (Ctrl+C)")
        stop_event.set()

    print("\n" + "=" * 70)
    print("✅ TEST TERMINÉ")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
