"""
Contrôleur de souris fluide avec accélération et lissage
Optimisé pour un mouvement sans saccades avec un joystick
"""

import pyautogui
import time
import threading
from typing import Optional
import math


class SmoothMouseController:
    """Contrôleur de souris avec mouvement fluide et accéléré"""

    def __init__(
        self,
        sensitivity: float = 30.0,
        max_sensitivity: float = 60.0,
        acceleration_curve: float = 2.0,
        update_interval: float = 0.008,
        smoothing: float = 0.3,
        deadzone: float = 0.15,
        precision_divider: float = 3.0
    ):
        """
        Initialise le contrôleur de souris

        Args:
            sensitivity: Sensibilité de base
            max_sensitivity: Sensibilité maximale
            acceleration_curve: Courbe d'accélération (1.0 = linéaire, >1.0 = exponentiel)
            update_interval: Intervalle de mise à jour en secondes (~125 FPS par défaut)
            smoothing: Lissage du mouvement (0.0-1.0)
            deadzone: Zone morte du joystick
            precision_divider: Diviseur de vitesse pour le mode précision
        """
        self.sensitivity = sensitivity
        self.max_sensitivity = max_sensitivity
        self.acceleration_curve = acceleration_curve
        self.update_interval = update_interval
        self.smoothing = smoothing
        self.deadzone = deadzone
        self.precision_divider = precision_divider

        # État actuel du mouvement
        self.current_x = 0.0
        self.current_y = 0.0

        # Valeurs lissées
        self.smoothed_x = 0.0
        self.smoothed_y = 0.0

        # Accumulateur pour les mouvements fractionnaires
        self.accumulated_x = 0.0
        self.accumulated_y = 0.0

        # Mode précision
        self.precision_mode = False

        # Thread de mise à jour
        self.running = False
        self.update_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()

        # Désactiver les protections pyautogui pour plus de fluidité
        pyautogui.PAUSE = 0
        pyautogui.MINIMUM_DURATION = 0

    def apply_deadzone(self, value: float) -> float:
        """
        Applique une zone morte circulaire

        Args:
            value: Valeur de l'axe (-1.0 à 1.0)

        Returns:
            Valeur ajustée
        """
        if abs(value) < self.deadzone:
            return 0.0

        # Remapper pour avoir une transition douce après la deadzone
        sign = 1 if value > 0 else -1
        adjusted = (abs(value) - self.deadzone) / (1.0 - self.deadzone)
        return sign * adjusted

    def apply_acceleration(self, value: float) -> float:
        """
        Applique une courbe d'accélération

        Args:
            value: Valeur normalisée (-1.0 à 1.0)

        Returns:
            Valeur avec accélération appliquée
        """
        if value == 0:
            return 0

        sign = 1 if value > 0 else -1
        magnitude = abs(value)

        # Courbe d'accélération exponentielle
        accelerated = math.pow(magnitude, self.acceleration_curve)

        # Interpoler entre la sensibilité de base et la sensibilité max
        sensitivity = self.sensitivity + (self.max_sensitivity - self.sensitivity) * accelerated

        # Appliquer le diviseur de précision si le mode précision est actif
        if self.precision_mode:
            sensitivity /= self.precision_divider

        return sign * accelerated * sensitivity

    def apply_smoothing(self, current: float, target: float) -> float:
        """
        Applique un lissage exponentiel

        Args:
            current: Valeur actuelle
            target: Valeur cible

        Returns:
            Valeur lissée
        """
        return current + (target - current) * (1.0 - self.smoothing)

    def set_input(self, x: float, y: float):
        """
        Définit l'entrée du joystick

        Args:
            x: Axe horizontal (-1.0 à 1.0)
            y: Axe vertical (-1.0 à 1.0)
        """
        with self.lock:
            self.current_x = x
            self.current_y = y

    def set_precision_mode(self, enabled: bool):
        """
        Active ou désactive le mode précision (vitesse réduite)

        Args:
            enabled: True pour activer, False pour désactiver
        """
        with self.lock:
            self.precision_mode = enabled

    def _update_loop(self):
        """Boucle de mise à jour du mouvement (exécutée dans un thread)"""
        last_time = time.perf_counter()

        while self.running:
            current_time = time.perf_counter()
            delta_time = current_time - last_time

            # Limiter le delta_time pour éviter les sauts
            if delta_time > 0.05:  # Max 50ms
                delta_time = 0.05

            with self.lock:
                # Appliquer deadzone
                x = self.apply_deadzone(self.current_x)
                y = self.apply_deadzone(self.current_y)

                # Appliquer accélération
                accel_x = self.apply_acceleration(x)
                accel_y = self.apply_acceleration(y)

                # Appliquer lissage
                self.smoothed_x = self.apply_smoothing(self.smoothed_x, accel_x)
                self.smoothed_y = self.apply_smoothing(self.smoothed_y, accel_y)

                # Calculer le mouvement avec delta_time pour un mouvement indépendant du framerate
                move_x = self.smoothed_x * delta_time * 60.0  # Normaliser à 60 FPS
                move_y = self.smoothed_y * delta_time * 60.0

                # Accumuler les mouvements fractionnaires
                self.accumulated_x += move_x
                self.accumulated_y += move_y

                # Extraire la partie entière pour le mouvement
                pixel_x = int(self.accumulated_x)
                pixel_y = int(self.accumulated_y)

                # Garder la partie fractionnaire
                self.accumulated_x -= pixel_x
                self.accumulated_y -= pixel_y

                # Déplacer la souris si nécessaire
                if pixel_x != 0 or pixel_y != 0:
                    try:
                        pyautogui.moveRel(pixel_x, pixel_y, _pause=False)
                    except Exception as e:
                        # Ignorer les erreurs de mouvement (par ex. hors écran)
                        pass

            last_time = current_time

            # Attendre le prochain cycle
            time.sleep(self.update_interval)

    def start(self):
        """Démarre le contrôleur de souris"""
        if not self.running:
            self.running = True
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()

    def stop(self):
        """Arrête le contrôleur de souris"""
        if self.running:
            self.running = False
            if self.update_thread:
                self.update_thread.join(timeout=1.0)

    def cleanup(self):
        """Nettoie les ressources"""
        self.stop()


class SmoothScrollController:
    """Contrôleur de scroll fluide"""

    def __init__(
        self,
        sensitivity: float = 3.0,
        acceleration_curve: float = 1.8,
        deadzone: float = 0.2
    ):
        """
        Initialise le contrôleur de scroll

        Args:
            sensitivity: Sensibilité du scroll
            acceleration_curve: Courbe d'accélération
            deadzone: Zone morte
        """
        self.sensitivity = sensitivity
        self.acceleration_curve = acceleration_curve
        self.deadzone = deadzone
        self.accumulated_scroll = 0.0

    def apply_deadzone(self, value: float) -> float:
        """Applique une zone morte"""
        if abs(value) < self.deadzone:
            return 0.0
        sign = 1 if value > 0 else -1
        adjusted = (abs(value) - self.deadzone) / (1.0 - self.deadzone)
        return sign * adjusted

    def scroll(self, value: float):
        """
        Effectue un scroll en fonction de la valeur du joystick

        Args:
            value: Valeur de l'axe (-1.0 à 1.0)
        """
        value = self.apply_deadzone(value)

        if abs(value) > 0:
            # Appliquer accélération
            sign = 1 if value > 0 else -1
            magnitude = abs(value)
            accelerated = math.pow(magnitude, self.acceleration_curve)
            scroll_amount = sign * accelerated * self.sensitivity

            # Accumuler pour les mouvements fractionnaires
            self.accumulated_scroll += scroll_amount

            # Scroller par pas entiers
            scroll_pixels = int(self.accumulated_scroll)
            if scroll_pixels != 0:
                try:
                    pyautogui.scroll(-scroll_pixels)
                    self.accumulated_scroll -= scroll_pixels
                except Exception:
                    pass


if __name__ == "__main__":
    """Test du contrôleur de souris fluide"""
    import pygame

    print("\n" + "=" * 60)
    print("TEST DU CONTRÔLEUR DE SOURIS FLUIDE")
    print("=" * 60)
    print("\nDéplacez le joystick gauche pour bouger la souris")
    print("Ctrl+C pour quitter\n")

    # Initialiser pygame
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("❌ Aucune manette détectée")
        exit(1)

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    print(f"✅ Manette connectée : {joystick.get_name()}\n")

    # Créer le contrôleur
    mouse_controller = SmoothMouseController(
        sensitivity=30.0,
        max_sensitivity=60.0,
        acceleration_curve=2.0,
        update_interval=0.008,
        smoothing=0.3,
        deadzone=0.15
    )

    mouse_controller.start()

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    if event.axis == 0:  # Axe X
                        x = event.value
                        y = joystick.get_axis(1)
                        mouse_controller.set_input(x, y)
                    elif event.axis == 1:  # Axe Y
                        x = joystick.get_axis(0)
                        y = event.value
                        mouse_controller.set_input(x, y)

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n\n✅ Arrêt du test")

    finally:
        mouse_controller.cleanup()
        pygame.quit()
