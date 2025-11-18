"""
Script de test pour le scroll avec le joystick droit
"""

import pygame
import time
import sys
import os

# Ajouter le chemin racine au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from outils.mouse_controller import SmoothScrollController
from config import ScrollConfig

pygame.init()
pygame.joystick.init()

# Vérifier si une manette est connectée
if pygame.joystick.get_count() == 0:
    print("Aucune manette détectée !")
    exit()

# Connexion à la première manette
joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"Manette connectée : {joystick.get_name()}")
print(f"Nombre d'axes : {joystick.get_numaxes()}")
print("\nDéplacez le joystick droit pour tester le scroll...")
print("Axe 2 (X) : Scroll horizontal")
print("Axe 3 (Y) : Scroll vertical")
print("Appuyez sur Ctrl+C pour quitter\n")

# Créer le contrôleur de scroll
scroll_controller = SmoothScrollController(
    sensitivity=ScrollConfig.SENSITIVITY,
    acceleration_curve=ScrollConfig.ACCELERATION_CURVE,
    deadzone=ScrollConfig.DEADZONE
)

print(f"Configuration du scroll :")
print(f"  Sensibilité : {ScrollConfig.SENSITIVITY}")
print(f"  Courbe d'accélération : {ScrollConfig.ACCELERATION_CURVE}")
print(f"  Zone morte : {ScrollConfig.DEADZONE}\n")

try:
    while True:
        for event in pygame.event.get():
            # Mouvement des axes
            if event.type == pygame.JOYAXISMOTION:
                axis = event.axis
                value = event.value

                # Axe 2 : Scroll horizontal
                if axis == 2:
                    print(f"Axe 2 (X): {value:+.3f} -> Scroll horizontal", end="\r")
                    scroll_controller.scroll_horizontal(value)

                # Axe 3 : Scroll vertical
                elif axis == 3:
                    print(f"Axe 3 (Y): {value:+.3f} -> Scroll vertical", end="\r")
                    scroll_controller.scroll(value)

        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n\nArrêt du test.")
    joystick.quit()
    pygame.quit()
