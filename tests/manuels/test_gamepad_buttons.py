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
print("\nAppuyez sur les boutons de la manette...")
print("Appuyez sur Ctrl+C pour quitter\n")

try:
    while True:
        for event in pygame.event.get():
            # Bouton presse
            if event.type == pygame.JOYBUTTONDOWN:
                print(f"Bouton #{event.button}")

        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nArret du test.")
    joystick.quit()
    pygame.quit()
