"""
Module pour contrôler le PC avec la manette + reconnaissance vocale
Combine GamepadController et VoiceCopyPaste
"""

import sys
import os

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.gamepad_controller import GamepadController, GamepadConfig, GamepadActions
from modules.copier_coller import VoiceCopyPaste, VoiceConfig
from outils.speech_recognizer import RecognitionEngine
from outils.auto_clicker import AutoClicker
from typing import Optional
import time
import threading
import pyautogui


class GamepadVoiceController(GamepadController):
    """Extension de GamepadController avec support de la dictée vocale"""

    def __init__(self, gamepad_config: Optional[GamepadConfig] = None, voice_config: Optional[VoiceConfig] = None):
        """
        Initialise le contrôleur manette + voix

        Args:
            gamepad_config: Configuration de la manette
            voice_config: Configuration de la reconnaissance vocale
        """
        # Initialiser le contrôleur de manette de base
        super().__init__(gamepad_config)

        # Debug: vérifier les button_mappings
        print(f"[DEBUG INIT] button_mappings = {list(self.config.button_mappings.keys()) if self.config.button_mappings else 'None'}")

        # Initialiser le système de dictée vocale
        self.voice_paste = VoiceCopyPaste(voice_config or VoiceConfig())

        # Initialiser le clicker automatique
        self.auto_clicker = AutoClicker(confidence=0.8)

        # État de l'enregistrement vocal
        self.voice_button_pressed = False

        # État du mode ClaudeIA
        self.claude_mode_active = False

        # État du bouton R3 (recherche continue en mode toggle)
        self.search_active = False  # État de la recherche (activée ou non)
        self.button_r3_thread = None
        self.button_r3_stop_event = threading.Event()

        # État du bouton 13 (recherche Windows avec reconnaissance vocale)
        self.button_13_pressed = False

        # État du bouton 10 (commandes vocales spéciales)
        self.button_10_pressed = False

        # État du bouton 0 (maintien du clic gauche)
        self.button_0_holding = False

        # États des boutons pour combinaisons
        self.button_0_pressed_state = False
        self.button_1_pressed_state = False
        self.button_2_pressed_state = False
        self.button_3_pressed_state = False
        self.button_4_pressed_state = False

        # Chemin de l'image yes.png
        self.yes_image_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "images", "yes.png"
        )

    def _click_yes_image_continuous(self):
        """
        Recherche et clique en continu sur l'image yes.png tant que le bouton est pressé
        """
        print(f"\n[BOUTON R3] 🔍 Recherche continue ACTIVÉE\n")

        click_count = 0

        while not self.button_r3_stop_event.is_set():
            success = self.auto_clicker.click_on_image(
                self.yes_image_path,
                button='left',
                clicks=1
            )

            if success:
                click_count += 1
                print(f"[BOUTON R3] ✅ Clic #{click_count} effectué")

            # Petite pause avant la prochaine recherche (évite de surcharger le CPU)
            # Utiliser wait() au lieu de sleep() pour pouvoir être interrompu rapidement
            if self.button_r3_stop_event.wait(timeout=0.3):
                break

        print(f"\n[BOUTON R3] ⏹️ Recherche ARRÊTÉE - {click_count} clic(s) effectué(s)\n")

    def _execute_special_command(self, text: str):
        """
        Exécute une commande vocale spéciale

        Args:
            text: Texte reconnu depuis la voix
        """
        text_lower = text.lower().strip()

        print(f"[COMMANDE SPÉCIALE] Analyse de : '{text}'")

        # Commandes de verrouillage
        if "verrouiller windows" in text_lower or "verrouille windows" in text_lower or "verrouiller" in text_lower:
            print("[COMMANDE SPÉCIALE] 🔒 Verrouillage de Windows...")
            # Utiliser keyDown/keyUp pour plus de fiabilité avec la touche Windows
            pyautogui.keyDown('win')
            time.sleep(0.05)
            pyautogui.press('l')
            time.sleep(0.05)
            pyautogui.keyUp('win')

        # Commandes de bureau virtuel
        elif "nouveau bureau" in text_lower or "créer bureau" in text_lower:
            print("[COMMANDE SPÉCIALE] 🖥️ Création d'un nouveau bureau virtuel...")
            pyautogui.keyDown('ctrl')
            pyautogui.keyDown('win')
            time.sleep(0.05)
            pyautogui.press('d')
            time.sleep(0.05)
            pyautogui.keyUp('win')
            pyautogui.keyUp('ctrl')

        elif "fermer bureau" in text_lower or "ferme bureau" in text_lower:
            print("[COMMANDE SPÉCIALE] 🖥️ Fermeture du bureau virtuel actuel...")
            pyautogui.keyDown('ctrl')
            pyautogui.keyDown('win')
            time.sleep(0.05)
            pyautogui.press('f4')
            time.sleep(0.05)
            pyautogui.keyUp('win')
            pyautogui.keyUp('ctrl')

        # Commandes de fenêtres
        elif "task manager" in text_lower or "gestionnaire" in text_lower:
            print("[COMMANDE SPÉCIALE] 📊 Ouverture du Gestionnaire des tâches...")
            pyautogui.hotkey('ctrl', 'shift', 'esc')

        elif "explorateur" in text_lower or "explorer" in text_lower:
            print("[COMMANDE SPÉCIALE] 📁 Ouverture de l'Explorateur de fichiers...")
            pyautogui.keyDown('win')
            time.sleep(0.05)
            pyautogui.press('e')
            time.sleep(0.05)
            pyautogui.keyUp('win')

        elif "paramètres" in text_lower or "settings" in text_lower:
            print("[COMMANDE SPÉCIALE] ⚙️ Ouverture des Paramètres Windows...")
            pyautogui.keyDown('win')
            time.sleep(0.05)
            pyautogui.press('i')
            time.sleep(0.05)
            pyautogui.keyUp('win')

        else:
            print(f"[COMMANDE SPÉCIALE] ❌ Commande non reconnue : '{text}'")
            print("[COMMANDE SPÉCIALE] 💡 Commandes disponibles :")
            print("  - 'verrouiller windows' : Verrouiller la session")
            print("  - 'nouveau bureau' : Créer un bureau virtuel")
            print("  - 'fermer bureau' : Fermer le bureau virtuel actuel")
            print("  - 'task manager' : Ouvrir le gestionnaire des tâches")
            print("  - 'explorateur' : Ouvrir l'explorateur de fichiers")
            print("  - 'paramètres' : Ouvrir les paramètres Windows")

    def handle_button(self, button_id: int, pressed: bool):
        """
        Surcharge pour gérer les boutons spéciaux (bouton 0, 3, 4, 5, 9, 10, 13)

        Args:
            button_id: ID du bouton
            pressed: True si pressé, False si relâché
        """
        # Debug: afficher quel bouton est pressé
        if pressed:
            print(f"[DEBUG] Bouton {button_id} pressé")

        # Gérer l'état des boutons pour les combinaisons
        if button_id == 0:
            self.button_0_pressed_state = pressed
        elif button_id == 1:
            self.button_1_pressed_state = pressed
        elif button_id == 2:
            self.button_2_pressed_state = pressed
        elif button_id == 3:
            self.button_3_pressed_state = pressed
        elif button_id == 4:
            self.button_4_pressed_state = pressed

        # Bouton 4 comme modificateur : combinaisons Ctrl
        if self.button_4_pressed_state and pressed:
            # Bouton 4 + 0 : Ctrl+Z
            if button_id == 0:
                print("[COMBINAISON] ↶ Ctrl+Z")
                pyautogui.hotkey('ctrl', 'z')
                return
            # Bouton 4 + 3 : Ctrl+A
            elif button_id == 3:
                print("[COMBINAISON] 📄 Ctrl+A")
                pyautogui.hotkey('ctrl', 'a')
                return
            # Bouton 4 + 2 : Ctrl+C
            elif button_id == 2:
                print("[COMBINAISON] 📋 Ctrl+C")
                pyautogui.hotkey('ctrl', 'c')
                return
            # Bouton 4 + 1 : Ctrl+V
            elif button_id == 1:
                print("[COMBINAISON] 📄 Ctrl+V")
                pyautogui.hotkey('ctrl', 'v')
                return
            # Bouton 4 pressé seul : ne rien faire
            elif button_id == 4:
                return

        # Bouton 0 : Clic gauche maintenu (comme drag)
        if button_id == 0:
            if pressed and not self.button_0_holding:
                # Maintenir le clic gauche
                self.button_0_holding = True
                pyautogui.mouseDown(button='left')
                print("[BOUTON 0] 🖱️ Clic gauche maintenu")
            elif not pressed and self.button_0_holding:
                # Relâcher le clic gauche
                self.button_0_holding = False
                pyautogui.mouseUp(button='left')
                print("[BOUTON 0] 🖱️ Clic gauche relâché")
            return

        # Bouton 10 : Commandes vocales spéciales
        elif button_id == 10:
            if pressed and not self.button_10_pressed:
                # Bouton pressé : démarrer l'enregistrement vocal
                self.button_10_pressed = True
                print("\n[BOUTON 10] 🎤 Enregistrement de la commande vocale...")
                print("[BOUTON 10] 💡 Dites une commande (ex: 'verrouiller windows')")
                self.voice_paste.start_voice_input()

            elif not pressed and self.button_10_pressed:
                # Bouton relâché : arrêter l'enregistrement et exécuter la commande
                self.button_10_pressed = False
                print("[BOUTON 10] ⏹️  Arrêt de l'enregistrement...")

                # Arrêter l'enregistrement et récupérer le texte reconnu
                # Temporairement désactiver auto_paste
                original_auto_paste = self.voice_paste.config.auto_paste
                self.voice_paste.config.auto_paste = False

                text = self.voice_paste.stop_voice_input()

                # Restaurer auto_paste
                self.voice_paste.config.auto_paste = original_auto_paste

                if text:
                    print(f"[BOUTON 10] ✅ Texte reconnu : '{text}'")
                    self._execute_special_command(text)
                else:
                    print("[BOUTON 10] ❌ Aucun texte reconnu\n")

        # Bouton 13 : Recherche Windows avec reconnaissance vocale
        elif button_id == 13:
            if pressed and not self.button_13_pressed:
                # Bouton pressé : démarrer l'enregistrement vocal
                self.button_13_pressed = True
                print("\n[BOUTON 13] 🎤 Enregistrement vocal démarré...")
                self.voice_paste.start_voice_input()

            elif not pressed and self.button_13_pressed:
                # Bouton relâché : arrêter l'enregistrement et effectuer la recherche Windows
                self.button_13_pressed = False
                print("[BOUTON 13] ⏹️  Arrêt de l'enregistrement...")

                # Arrêter l'enregistrement et récupérer le texte reconnu
                # Temporairement désactiver auto_paste
                original_auto_paste = self.voice_paste.config.auto_paste
                self.voice_paste.config.auto_paste = False

                text = self.voice_paste.stop_voice_input()

                # Restaurer auto_paste
                self.voice_paste.config.auto_paste = original_auto_paste

                if text:
                    print(f"[BOUTON 13] ✅ Texte reconnu : {text}")
                    print("[BOUTON 13] 🔍 Ouverture de la recherche Windows...")

                    # Appuyer sur la touche Windows
                    pyautogui.press('win')

                    # Attendre que le menu s'ouvre
                    time.sleep(0.3)

                    # Taper le texte reconnu
                    print(f"[BOUTON 13] ⌨️  Saisie : {text}")
                    pyautogui.write(text, interval=0.05)

                    # Petite pause avant d'appuyer sur Entrée
                    time.sleep(0.2)

                    # Appuyer sur Entrée
                    pyautogui.press('enter')
                    print("[BOUTON 13] ✅ Recherche lancée !\n")
                else:
                    print("[BOUTON 13] ❌ Aucun texte reconnu\n")

        # Bouton 9 (R3) : Toggle recherche continue de yes.png
        elif button_id == 9:
            # Détecter uniquement l'appui (pas le relâchement)
            if pressed and button_id not in self.button_states:
                # Marquer le bouton comme pressé
                self.button_states[button_id] = True

                # Toggle le mode ClaudeIA
                self.claude_mode_active = not self.claude_mode_active
                status = "ACTIVE" if self.claude_mode_active else "DESACTIVE"
                print(f"\n[CLAUDE IA] Mode VSCode Auto: {status}")

                # Toggle la recherche continue
                if not self.search_active:
                    # Démarrer la recherche
                    self.search_active = True
                    self.button_r3_stop_event.clear()

                    print(f"[BOUTON R3] ▶️  Démarrage de la recherche continue...")

                    # Lancer la recherche continue dans un thread séparé
                    self.button_r3_thread = threading.Thread(
                        target=self._click_yes_image_continuous,
                        daemon=True
                    )
                    self.button_r3_thread.start()

                else:
                    # Arrêter la recherche
                    self.search_active = False
                    print(f"[BOUTON R3] ⏸️  Arrêt de la recherche continue...")
                    self.button_r3_stop_event.set()

                    # Attendre que le thread se termine (avec timeout)
                    if self.button_r3_thread and self.button_r3_thread.is_alive():
                        self.button_r3_thread.join(timeout=1.0)

            elif not pressed and button_id in self.button_states:
                # Bouton relâché : nettoyer l'état
                del self.button_states[button_id]

        # Bouton 3 : Dictée vocale (maintenir pour enregistrer)
        # Si combinaison 3+4 déjà traitée, ne pas exécuter la dictée
        elif button_id == 3:
            if not self.button_4_pressed_state:
                if pressed and not self.voice_button_pressed:
                    # Bouton pressé : démarrer l'enregistrement
                    self.voice_button_pressed = True
                    self.voice_paste.start_voice_input()

                elif not pressed and self.voice_button_pressed:
                    # Bouton relâché : arrêter et reconnaître
                    self.voice_button_pressed = False
                    self.voice_paste.stop_voice_input()

        # Bouton 5 (RB/R1) : Mode boost de la souris (maintenir)
        elif button_id == 5:
            if pressed:
                # Activer le mode boost
                self.smooth_mouse.set_precision_mode(True)
                print("[MODE BOOST] Vitesse de la souris accélérée x3")
            else:
                # Désactiver le mode boost
                self.smooth_mouse.set_precision_mode(False)
                print("[MODE NORMAL] Vitesse de la souris normale")
            # Ne pas appeler super() car le bouton 5 a un comportement spécial

        else:
            # Laisser le contrôleur de base gérer les autres boutons
            print(f"[DEBUG] Délégation du bouton {button_id} à super().handle_button()")
            super().handle_button(button_id, pressed)

    def cleanup(self):
        """Nettoie les ressources (manette + voix)"""
        # Relâcher le clic gauche si maintenu
        if self.button_0_holding:
            pyautogui.mouseUp(button='left')
            self.button_0_holding = False

        self.voice_paste.cleanup()
        super().disconnect()


def get_voice_gamepad_config() -> GamepadConfig:
    """
    Retourne une configuration par défaut avec le bouton 3 pour la voix

    Mapping :
    - Bouton 0 (A/X) : Clic gauche maintenu (drag)
    - Bouton 1 (B/O) : Entrée
    - Bouton 2 (X/□) : Clic droit
    - Bouton 3 (Y/△) : 🎤 DICTÉE VOCALE (maintenir)
    - Bouton 4 (LB/L1) : Modificateur (comme Ctrl/Win)
    - Bouton 4 + 0 : Ctrl+Z
    - Bouton 4 + 3 : Ctrl+A
    - Bouton 4 + 2 : Ctrl+C
    - Bouton 4 + 1 : Ctrl+V
    - Bouton 3 + 4 : Win + Tab (bureaux virtuels)
    - Bouton 5 (RB/R1) : Ctrl+W
    - Bouton 6 (Back) : Volume -
    - Bouton 7 (Start) : Volume +
    - Bouton 9 (R3) : 🔍 Toggle recherche/clic yes.png
    - D-pad : Touches fléchées du clavier (↑, ↓, ←, →)
    - Joystick gauche : Déplacer la souris
    - Joystick droit (X) : Scroll horizontal
    - Joystick droit (Y) : Scroll vertical
    """
    return GamepadConfig(
        button_mappings={
            # Boutons 0-4 gérés spécialement pour les combinaisons
            # Bouton 5 géré spécialement pour le mode boost (pas dans le mapping)
            6: GamepadActions.key_press('volumedown'),
            7: GamepadActions.key_press('volumeup'),
            # Bouton 9 géré spécialement pour la recherche yes.png
        },
        axis_mappings={
            0: GamepadActions.mouse_move(sensitivity=15.0),
            1: GamepadActions.mouse_move_vertical(sensitivity=15.0),
            2: GamepadActions.mouse_scroll_horizontal(sensitivity=5.0),
            3: GamepadActions.mouse_scroll(sensitivity=5.0),
        },
        deadzone=0.15,
        mouse_sensitivity=15.0,
        scroll_sensitivity=2.0
    )


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🎮 CONTRÔLEUR MANETTE + VOIX")
    print("=" * 60)

    # Configuration
    gamepad_config = get_voice_gamepad_config()
    voice_config = VoiceConfig(
        language="fr-FR",
        engine=RecognitionEngine.GOOGLE,
        auto_paste=True,
        feedback=True
    )

    # Créer le contrôleur
    controller = GamepadVoiceController(gamepad_config, voice_config)

    # Connecter la manette
    if controller.connect():
        print("\n=== CONFIGURATION ===")
        print("Bouton 0 (A/X) : Clic gauche maintenu (drag)")
        print("Bouton 1 (B/O) : Entrée")
        print("Bouton 2 (X/□) : Clic droit")
        print("Bouton 3 (Y/△) : 🎤 DICTÉE VOCALE (maintenir le bouton)")
        print("Bouton 4 (LB/L1) : Modificateur (comme Ctrl/Win)")
        print("Bouton 4 + 0 : Ctrl+Z")
        print("Bouton 4 + 3 : Ctrl+A")
        print("Bouton 4 + 2 : Ctrl+C")
        print("Bouton 4 + 1 : Ctrl+V")
        print("Bouton 3 + 4 : Win + Tab (bureaux virtuels)")
        print("Bouton 5 (RB/R1) : Ctrl+W (fermer)")
        print("Bouton 6 (Back) : Volume -")
        print("Bouton 7 (Start) : Volume +")
        print("Bouton 9 (R3) : 🔍 Toggle recherche/clic yes.png")
        print("\nD-pad : Touches fléchées (↑, ↓, ←, →)")
        print("\nJoystick gauche : Déplacer la souris")
        print("Joystick droit (X) : Scroll horizontal (gauche/droite)")
        print("Joystick droit (Y) : Scroll vertical (haut/bas)")
        print("\n" + "=" * 60)
        print("💡 ASTUCE : Maintenez le bouton 3 et parlez,")
        print("            relâchez pour coller le texte reconnu")
        print("=" * 60 + "\n")

        # Lancer la boucle principale
        controller.run()

    else:
        print("❌ Impossible de se connecter à la manette.")
