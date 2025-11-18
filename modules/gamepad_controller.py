"""
Module pour contrôler le PC avec une manette de jeu
Utilise pygame pour la détection de la manette et pyautogui pour les actions
"""

import pygame
import pyautogui
import time
import sys
import os
from typing import Callable, Dict, Any, Optional
from dataclasses import dataclass

# Ajouter le dossier parent au path pour importer config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import MouseConfig, ScrollConfig, GamepadConfig as AppGamepadConfig
from outils.mouse_controller import SmoothMouseController, SmoothScrollController


@dataclass
class GamepadConfig:
    """Configuration pour mapper les boutons/axes de la manette aux actions"""
    button_mappings: Dict[int, Callable] = None
    axis_mappings: Dict[int, Callable] = None
    deadzone: float = 0.15  # Zone morte pour les joysticks
    mouse_sensitivity: float = 10.0  # Sensibilité du mouvement de souris
    scroll_sensitivity: float = 1.0  # Sensibilité du scroll


class GamepadController:
    """Classe principale pour contrôler le PC avec une manette"""

    def __init__(self, config: Optional[GamepadConfig] = None):
        """
        Initialise le contrôleur de manette

        Args:
            config: Configuration personnalisée (optionnel)
        """
        pygame.init()
        pygame.joystick.init()

        self.config = config or GamepadConfig()
        self.joystick = None
        self.running = False
        self.button_states = {}
        self.axis_states = {}

        # Initialiser le contrôleur de souris fluide
        self.smooth_mouse = SmoothMouseController(
            sensitivity=MouseConfig.SENSITIVITY,
            max_sensitivity=MouseConfig.MAX_SENSITIVITY,
            acceleration_curve=MouseConfig.ACCELERATION_CURVE,
            update_interval=MouseConfig.UPDATE_INTERVAL,
            smoothing=MouseConfig.SMOOTHING,
            deadzone=MouseConfig.DEADZONE,
            precision_divider=MouseConfig.PRECISION_DIVIDER
        )

        # Initialiser le contrôleur de scroll fluide
        self.smooth_scroll = SmoothScrollController(
            sensitivity=ScrollConfig.SENSITIVITY,
            acceleration_curve=ScrollConfig.ACCELERATION_CURVE,
            deadzone=ScrollConfig.DEADZONE
        )

        # Démarrer les contrôleurs
        self.smooth_mouse.start()
        self.smooth_scroll.start()

        # Configurer les actions pour utiliser les contrôleurs fluides
        GamepadActions.set_controllers(self.smooth_mouse, self.smooth_scroll)

    def connect(self, joystick_id: int = 0) -> bool:
        """
        Connecte à une manette

        Args:
            joystick_id: ID de la manette (0 pour la première)

        Returns:
            True si la connexion réussit
        """
        try:
            if pygame.joystick.get_count() == 0:
                print("Aucune manette détectée !")
                return False

            self.joystick = pygame.joystick.Joystick(joystick_id)
            self.joystick.init()

            print(f"Manette connectée : {self.joystick.get_name()}")
            print(f"Nombre de boutons : {self.joystick.get_numbuttons()}")
            print(f"Nombre d'axes : {self.joystick.get_numaxes()}")
            print(f"Nombre de chapeaux : {self.joystick.get_numhats()}")

            return True

        except pygame.error as e:
            print(f"Erreur lors de la connexion : {e}")
            return False

    def disconnect(self):
        """Déconnecte la manette"""
        # Arrêter les contrôleurs fluides
        self.smooth_mouse.cleanup()
        self.smooth_scroll.cleanup()

        if self.joystick:
            self.joystick.quit()
            self.joystick = None
        pygame.quit()

    def apply_deadzone(self, value: float) -> float:
        """
        Applique une zone morte aux valeurs des axes

        Args:
            value: Valeur de l'axe (-1.0 à 1.0)

        Returns:
            Valeur ajustée
        """
        if abs(value) < self.config.deadzone:
            return 0.0
        return value

    def handle_button(self, button_id: int, pressed: bool):
        """
        Gère les événements de boutons

        Args:
            button_id: ID du bouton
            pressed: True si pressé, False si relâché
        """
        print(f"[DEBUG PARENT] handle_button appelé: bouton={button_id}, pressed={pressed}, in_states={button_id in self.button_states}")
        if self.config.button_mappings and button_id in self.config.button_mappings:
            print(f"[DEBUG PARENT] Bouton {button_id} trouvé dans button_mappings")
            action = self.config.button_mappings[button_id]
            if pressed and button_id not in self.button_states:
                # Bouton pressé pour la première fois
                print(f"[DEBUG PARENT] Exécution de l'action pour le bouton {button_id}")
                action()
                self.button_states[button_id] = True
            elif not pressed and button_id in self.button_states:
                # Bouton relâché
                print(f"[DEBUG PARENT] Bouton {button_id} relâché, nettoyage de l'état")
                del self.button_states[button_id]
            else:
                print(f"[DEBUG PARENT] Condition non remplie: pressed={pressed}, in_states={button_id in self.button_states}")
        else:
            print(f"[DEBUG PARENT] Bouton {button_id} NON trouvé dans button_mappings ou pas de mappings")

    def handle_axis(self, axis_id: int, value: float):
        """
        Gère les événements d'axes (joysticks/gâchettes)

        Args:
            axis_id: ID de l'axe
            value: Valeur de l'axe (-1.0 à 1.0)
        """
        # Appliquer deadzone seulement pour les axes de mouvement de souris (0 et 1)
        # Les axes de scroll (2 et 3) gèrent leur propre deadzone dans SmoothScrollController
        if axis_id in [0, 1]:
            value = self.apply_deadzone(value)

        if self.config.axis_mappings and axis_id in self.config.axis_mappings:
            action = self.config.axis_mappings[axis_id]
            action(value)

    def handle_hat(self, hat_id: int, value: tuple):
        """
        Gère les événements de chapeau (D-pad)

        Args:
            hat_id: ID du chapeau
            value: Tuple (x, y) avec -1, 0 ou 1
        """
        # Détecter et gérer les directions du D-pad
        x, y = value

        # Gérer l'axe horizontal (gauche/droite)
        if x == -1:
            # D-pad gauche
            pyautogui.press('left')
        elif x == 1:
            # D-pad droite
            pyautogui.press('right')

        # Gérer l'axe vertical (haut/bas)
        if y == 1:
            # D-pad haut
            pyautogui.press('up')
        elif y == -1:
            # D-pad bas
            pyautogui.press('down')

    def run(self, on_event: Optional[Callable] = None):
        """
        Boucle principale pour traiter les événements de la manette

        Args:
            on_event: Callback optionnel appelé pour chaque événement
        """
        if not self.joystick:
            print("Aucune manette connectée ! Appelez connect() d'abord.")
            return

        self.running = True
        print("\nContrôle de la manette actif. Appuyez sur Ctrl+C pour quitter.\n")

        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False

                    elif event.type == pygame.JOYBUTTONDOWN:
                        self.handle_button(event.button, True)
                        if on_event:
                            on_event(event)

                    elif event.type == pygame.JOYBUTTONUP:
                        self.handle_button(event.button, False)
                        if on_event:
                            on_event(event)

                    elif event.type == pygame.JOYAXISMOTION:
                        self.handle_axis(event.axis, event.value)
                        if on_event:
                            on_event(event)

                    elif event.type == pygame.JOYHATMOTION:
                        self.handle_hat(event.hat, event.value)
                        if on_event:
                            on_event(event)

                # Lire constamment les axes pour détecter les changements immédiatement
                # Ceci est crucial pour le scroll qui doit s'arrêter instantanément
                num_axes = self.joystick.get_numaxes()
                for axis_id in range(num_axes):
                    value = self.joystick.get_axis(axis_id)
                    # Mettre à jour les axes de scroll (2 et 3) en temps réel
                    if axis_id in [2, 3] and self.config.axis_mappings and axis_id in self.config.axis_mappings:
                        action = self.config.axis_mappings[axis_id]
                        action(value)

                time.sleep(0.01)  # Petit délai pour ne pas surcharger le CPU

        except KeyboardInterrupt:
            print("\nArrêt du contrôleur...")
        finally:
            self.disconnect()

    def stop(self):
        """Arrête la boucle principale"""
        self.running = False


# Fonctions utilitaires pour actions communes
class GamepadActions:
    """Collection d'actions prédéfinies pour la manette"""

    # Référence au contrôleur de souris (sera défini par le GamepadController)
    _smooth_mouse_controller = None
    _smooth_scroll_controller = None
    _axis_values = {'x': 0.0, 'y': 0.0}  # Stocker les valeurs X et Y

    @classmethod
    def set_controllers(cls, mouse_controller, scroll_controller):
        """Définit les contrôleurs pour les actions"""
        cls._smooth_mouse_controller = mouse_controller
        cls._smooth_scroll_controller = scroll_controller

    @staticmethod
    def mouse_move(sensitivity: float = 10.0):
        """Retourne une fonction pour déplacer la souris horizontalement (utilise le système fluide)"""
        def move(value: float):
            # Stocker la valeur X et mettre à jour le contrôleur fluide
            GamepadActions._axis_values['x'] = value
            if GamepadActions._smooth_mouse_controller:
                GamepadActions._smooth_mouse_controller.set_input(
                    GamepadActions._axis_values['x'],
                    GamepadActions._axis_values['y']
                )
        return move

    @staticmethod
    def mouse_move_vertical(sensitivity: float = 10.0):
        """Retourne une fonction pour déplacer la souris verticalement (utilise le système fluide)"""
        def move(value: float):
            # Stocker la valeur Y et mettre à jour le contrôleur fluide
            GamepadActions._axis_values['y'] = value
            if GamepadActions._smooth_mouse_controller:
                GamepadActions._smooth_mouse_controller.set_input(
                    GamepadActions._axis_values['x'],
                    GamepadActions._axis_values['y']
                )
        return move

    @staticmethod
    def mouse_click(button: str = 'left'):
        """Retourne une fonction pour cliquer avec la souris"""
        def click():
            pyautogui.click(button=button)
        return click

    @staticmethod
    def mouse_scroll(sensitivity: float = 1.0):
        """Retourne une fonction pour scroller verticalement (utilise le système fluide)"""
        def scroll(value: float):
            if GamepadActions._smooth_scroll_controller:
                GamepadActions._smooth_scroll_controller.scroll(value)
        return scroll

    @staticmethod
    def mouse_scroll_horizontal(sensitivity: float = 1.0):
        """Retourne une fonction pour scroller horizontalement (utilise le système fluide)"""
        def scroll(value: float):
            if GamepadActions._smooth_scroll_controller:
                GamepadActions._smooth_scroll_controller.scroll_horizontal(value)
        return scroll

    @staticmethod
    def key_press(key: str):
        """Retourne une fonction pour presser une touche"""
        def press():
            pyautogui.press(key)
        return press

    @staticmethod
    def key_combination(*keys):
        """Retourne une fonction pour presser une combinaison de touches"""
        def press():
            pyautogui.hotkey(*keys)
        return press


# Configuration exemple
def get_default_config() -> GamepadConfig:
    """
    Retourne une configuration par défaut pour une manette Xbox/PlayStation

    Mapping typique :
    - Bouton 0 (A/X) : Clic gauche
    - Bouton 1 (B/O) : Clic droit
    - Bouton 2 (X/□) : Entrée
    - Bouton 3 (Y/△) : Échap
    - Axe 0 : Mouvement horizontal souris (joystick gauche)
    - Axe 1 : Mouvement vertical souris (joystick gauche)
    - Axe 2 : Scroll horizontal (joystick droit X)
    - Axe 3 : Scroll vertical (joystick droit Y)
    - D-pad : Touches fléchées du clavier (↑, ↓, ←, →)
    """
    return GamepadConfig(
        button_mappings={
            0: GamepadActions.mouse_click('left'),      # A/X
            1: GamepadActions.mouse_click('right'),     # B/O
            2: GamepadActions.key_press('enter'),       # X/□
            3: GamepadActions.key_press('esc'),         # Y/△
            4: GamepadActions.key_combination('alt', 'tab'),  # LB/L1
            5: GamepadActions.key_combination('ctrl', 'w'),   # RB/R1
            6: GamepadActions.key_press('volumedown'),  # Back/Select
            7: GamepadActions.key_press('volumeup'),    # Start
        },
        axis_mappings={
            0: GamepadActions.mouse_move(sensitivity=15.0),                # Joystick gauche X
            1: GamepadActions.mouse_move_vertical(sensitivity=15.0),       # Joystick gauche Y
            2: GamepadActions.mouse_scroll_horizontal(sensitivity=5.0),    # Joystick droit X (scroll horizontal)
            3: GamepadActions.mouse_scroll(sensitivity=5.0),               # Joystick droit Y (scroll vertical)
        },
        deadzone=0.15,
        mouse_sensitivity=15.0,
        scroll_sensitivity=2.0
    )


if __name__ == "__main__":
    # Exemple d'utilisation
    config = get_default_config()
    controller = GamepadController(config)

    if controller.connect():
        print("\n=== Configuration ===")
        print("Bouton 0 (A/X) : Clic gauche")
        print("Bouton 1 (B/O) : Clic droit")
        print("Bouton 2 (X/□) : Entrée")
        print("Bouton 3 (Y/△) : Échap")
        print("Bouton 4 (LB/L1) : Alt+Tab")
        print("Bouton 5 (RB/R1) : Ctrl+W (fermer onglet)")
        print("Bouton 6 (Back) : Volume -")
        print("Bouton 7 (Start) : Volume +")
        print("\nJoystick gauche : Déplacer la souris")
        print("Joystick droit (X) : Scroll horizontal (gauche/droite)")
        print("Joystick droit (Y) : Scroll vertical (haut/bas)")

        controller.run()
    else:
        print("Impossible de se connecter à la manette.")
