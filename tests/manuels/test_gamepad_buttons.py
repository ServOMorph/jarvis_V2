"""
Script de test simple pour afficher le numero des boutons de la manette
"""

import pygame
import time


pygame.init()
pygame.joystick.init()

# Verifier si une manette est connectee
if pygame.joystick.get_count() == 0:
    print("Aucune manette detectee !")
    exit()

# Connexion a la premiere manette
joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"Manette connectee : {joystick.get_name()}")
print(f"Nombre de boutons : {joystick.get_numbuttons()}")
print(f"Nombre d'axes : {joystick.get_numaxes()}")
print(f"Nombre de chapeaux (D-pad) : {joystick.get_numhats()}")
print("\nAppuyez sur les boutons de la manette ou utilisez le D-pad...")
print("Appuyez sur Ctrl+C pour quitter\n")

# Dictionnaire pour afficher les directions du D-pad de manière lisible
hat_directions = {
    (0, 0): "Centre (repos)",
    (0, 1): "Haut ↑",
    (0, -1): "Bas ↓",
    (-1, 0): "Gauche ←",
    (1, 0): "Droite →",
    (-1, 1): "Haut-Gauche ↖",
    (1, 1): "Haut-Droite ↗",
    (-1, -1): "Bas-Gauche ↙",
    (1, -1): "Bas-Droite ↘"
}

try:
    while True:
        for event in pygame.event.get():
            # Bouton presse
            if event.type == pygame.JOYBUTTONDOWN:
                print(f"Bouton #{event.button}")

            # D-pad (chapeau directionnel)
            elif event.type == pygame.JOYHATMOTION:
                hat_value = event.value
                direction = hat_directions.get(hat_value, f"Direction inconnue: {hat_value}")
                print(f"D-pad (Hat #{event.hat}) : {direction} {hat_value}")

        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nArret du test.")
    joystick.quit()
    pygame.quit()
