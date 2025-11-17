"""
Module pour gérer le presse-papier (copier/coller)
Utilise pyperclip pour la compatibilité multi-plateforme
"""

import pyperclip
import pyautogui
from typing import Optional
import time


class ClipboardManager:
    """Classe pour gérer le presse-papier système"""

    def __init__(self):
        """Initialise le gestionnaire de presse-papier"""
        pass

    def copy(self, text: str) -> bool:
        """
        Copie du texte dans le presse-papier

        Args:
            text: Texte à copier

        Returns:
            True si succès
        """
        try:
            pyperclip.copy(text)
            return True
        except Exception as e:
            print(f"Erreur lors de la copie : {e}")
            return False

    def paste(self) -> Optional[str]:
        """
        Récupère le contenu du presse-papier

        Returns:
            Contenu du presse-papier ou None si erreur
        """
        try:
            return pyperclip.paste()
        except Exception as e:
            print(f"Erreur lors de la récupération : {e}")
            return None

    def get_content(self) -> Optional[str]:
        """
        Alias pour paste() - récupère le contenu du presse-papier

        Returns:
            Contenu du presse-papier ou None si erreur
        """
        return self.paste()

    def clear(self) -> bool:
        """
        Vide le presse-papier

        Returns:
            True si succès
        """
        try:
            pyperclip.copy('')
            return True
        except Exception as e:
            print(f"Erreur lors du nettoyage : {e}")
            return False

    def copy_and_type(self, text: str, interval: float = 0.0) -> bool:
        """
        Copie le texte et le colle directement avec Ctrl+V

        Args:
            text: Texte à copier et coller
            interval: Intervalle entre chaque caractère (pour simulation de frappe)

        Returns:
            True si succès
        """
        try:
            # Copier dans le presse-papier
            self.copy(text)

            # Court délai pour s'assurer que la copie est effectuée
            time.sleep(0.05)

            # Simuler Ctrl+V pour coller
            pyautogui.hotkey('ctrl', 'v')

            return True

        except Exception as e:
            print(f"Erreur lors du copier-coller : {e}")
            return False

    def type_text(self, text: str, interval: float = 0.0) -> bool:
        """
        Tape le texte directement (sans passer par le presse-papier)

        Args:
            text: Texte à taper
            interval: Intervalle entre chaque caractère (secondes)

        Returns:
            True si succès
        """
        try:
            pyautogui.write(text, interval=interval)
            return True
        except Exception as e:
            print(f"Erreur lors de la frappe : {e}")
            return False

    def paste_from_clipboard(self) -> bool:
        """
        Colle le contenu actuel du presse-papier avec Ctrl+V

        Returns:
            True si succès
        """
        try:
            pyautogui.hotkey('ctrl', 'v')
            return True
        except Exception as e:
            print(f"Erreur lors du collage : {e}")
            return False

    def save_and_restore(self, new_text: str, action_callback=None):
        """
        Sauvegarde le presse-papier actuel, copie un nouveau texte,
        exécute une action, puis restaure l'ancien contenu

        Args:
            new_text: Nouveau texte à copier temporairement
            action_callback: Fonction à exécuter avec le nouveau contenu
        """
        # Sauvegarder le contenu actuel
        old_content = self.paste()

        try:
            # Copier le nouveau texte
            self.copy(new_text)

            # Exécuter l'action si fournie
            if action_callback:
                action_callback()

        finally:
            # Restaurer l'ancien contenu
            if old_content is not None:
                self.copy(old_content)
            else:
                self.clear()


if __name__ == "__main__":
    # Test simple
    print("\n=== Test du gestionnaire de presse-papier ===\n")

    manager = ClipboardManager()

    # Test 1 : Copier et récupérer
    print("Test 1 : Copier et récupérer du texte")
    test_text = "Bonjour depuis Python !"
    manager.copy(test_text)
    content = manager.get_content()
    print(f"Texte copié : {content}")
    assert content == test_text, "Erreur : le texte ne correspond pas"
    print("✅ Succès\n")

    # Test 2 : Sauvegarder et restaurer
    print("Test 2 : Sauvegarder et restaurer")
    manager.copy("Contenu original")
    print(f"Contenu original : {manager.get_content()}")

    def action_temporaire():
        print(f"Contenu temporaire : {manager.get_content()}")

    manager.save_and_restore("Contenu temporaire", action_temporaire)
    print(f"Contenu restauré : {manager.get_content()}")
    print("✅ Succès\n")

    # Test 3 : Vider le presse-papier
    print("Test 3 : Vider le presse-papier")
    manager.clear()
    content = manager.get_content()
    print(f"Contenu après nettoyage : '{content}'")
    print("✅ Succès\n")
