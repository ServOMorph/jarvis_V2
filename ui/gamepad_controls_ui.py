"""
Interface graphique moderne pour afficher les contrôles de la manette
"""

import tkinter as tk
from tkinter import ttk
import pygame
import json
from pathlib import Path
from typing import Dict, Optional


class ModernGamepadUI:
    """Interface moderne pour visualiser les contrôles de la manette"""

    # Configuration des couleurs (thème sombre moderne)
    COLORS = {
        'bg': '#1a1a2e',           # Fond principal
        'card_bg': '#16213e',       # Fond des cartes
        'accent': '#0f3460',        # Accent sombre
        'primary': '#e94560',       # Couleur primaire (rouge/rose)
        'secondary': '#533483',     # Couleur secondaire (violet)
        'text': '#eaeaea',          # Texte principal
        'text_dim': '#a0a0a0',      # Texte secondaire
        'success': '#00d9ff',       # Couleur de succès (cyan)
        'active': '#ffd700',        # Couleur active (or)
    }

    # Mapping des noms de boutons (pour l'affichage)
    BUTTON_NAMES = {
        0: {'label': 'Bouton A', 'color': '#00d9ff'},
        1: {'label': 'Bouton B', 'color': '#e94560'},
        2: {'label': 'Bouton Y', 'color': '#533483'},
        3: {'label': 'Bouton X', 'color': '#ffd700'},
        4: {'label': 'Bouton LB', 'color': '#888888'},
        5: {'label': 'Bouton RB', 'color': '#888888'},
        6: {'label': 'Bouton Back', 'color': '#666666'},
        7: {'label': 'Bouton Start', 'color': '#666666'},
        8: {'label': 'Bouton L3', 'color': '#555555'},
        9: {'label': 'Bouton R3', 'color': '#555555'},
    }

    # Mapping des descriptions d'actions
    ACTION_DESCRIPTIONS = {
        'voice_input': '🎤 Dictée vocale (maintenir)',
        'toggle_claude_mode': '🤖 Mode ClaudeIA VSCode Auto (toggle)',
        'mouse_click_left': 'Clic gauche',
        'mouse_click_right': 'Clic droit',
        'key_press_enter': 'Entrée',
        'key_press_esc': 'Échap (ESC)',
        'alt_tab': 'Alt + Tab',
        'ctrl_w': 'Ctrl + W (fermer)',
        'volume_down': 'Volume -',
        'volume_up': 'Volume +',
    }

    def __init__(self, root: tk.Tk, config_path: str = "config/voice_config.json"):
        """
        Initialise l'interface

        Args:
            root: Fenêtre principale tkinter
            config_path: Chemin du fichier de configuration
        """
        self.root = root
        self.root.title("JARVIS V2 - Contrôles Manette")
        self.root.configure(bg=self.COLORS['bg'])

        # Charger la configuration
        self.config = self._load_config(config_path)
        self.button_controls = {}
        self.axis_controls = {}
        self._parse_config()

        # Configuration de la fenêtre
        window_width = 900
        window_height = max(500, min(800, 200 + len(self.button_controls) * 120))
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(False, False)

        # Variables pour stocker les widgets des boutons
        self.button_indicators: Dict[int, tk.Frame] = {}
        self.button_labels: Dict[int, tk.Label] = {}

        # Variables pour pygame
        self.joystick: Optional[pygame.joystick.Joystick] = None
        self.running = False

        # État des modes toggles
        self.toggle_states: Dict[int, bool] = {}
        self.status_label: Optional[tk.Label] = None

        # Suivi des boutons pressés pour éviter les déclenchements multiples
        self.button_pressed_flags: Dict[int, bool] = {}

        # Référence au contrôleur principal pour synchronisation
        self.controller = None

        # Créer l'interface
        self._create_ui()

        # Initialiser pygame et la manette
        self._init_gamepad()

        # Démarrer la mise à jour
        if self.joystick:
            self._update_gamepad_state()

    def set_controller(self, controller):
        """Lie l'UI au contrôleur principal pour synchronisation"""
        self.controller = controller
        print("[UI] Contrôleur lié à l'interface")

    def _load_config(self, config_path: str) -> dict:
        """Charge la configuration depuis le fichier JSON"""
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration : {e}")
        return {}

    def _parse_config(self):
        """Parse la configuration pour extraire les contrôles"""
        # Extraire les boutons configurés
        button_mapping = self.config.get('button_mapping', {})
        for btn_id_str, btn_config in button_mapping.items():
            btn_id = int(btn_id_str)

            # Récupérer le nom du bouton
            btn_info = self.BUTTON_NAMES.get(btn_id, {
                'label': f'Bouton {btn_id}',
                'color': '#888888'
            })

            # Déterminer la description de l'action
            action = btn_config.get('action', 'unknown')
            description = btn_config.get('description', self.ACTION_DESCRIPTIONS.get(action, action))

            self.button_controls[btn_id] = {
                'label': btn_info['label'],
                'action': description,
                'color': btn_info['color']
            }

        # Extraire les axes configurés (si présents dans la config)
        gamepad_config = self.config.get('gamepad', {})

        # Axes pour la souris (définis dans gamepad_config)
        if gamepad_config.get('mouse_sensitivity'):
            self.axis_controls[0] = {
                'label': 'Joystick Gauche (X)',
                'action': 'Déplacer souris ←→',
                'sensitivity': gamepad_config.get('mouse_sensitivity')
            }
            self.axis_controls[1] = {
                'label': 'Joystick Gauche (Y)',
                'action': 'Déplacer souris ↑↓',
                'sensitivity': gamepad_config.get('mouse_sensitivity')
            }

        # Axe pour le scroll (si défini)
        if gamepad_config.get('scroll_sensitivity'):
            self.axis_controls[3] = {
                'label': 'Joystick Droit (Y)',
                'action': 'Scroll ↑↓',
                'sensitivity': gamepad_config.get('scroll_sensitivity')
            }

    def _create_ui(self):
        """Crée l'interface utilisateur"""

        # En-tête
        header_frame = tk.Frame(self.root, bg=self.COLORS['bg'])
        header_frame.pack(fill=tk.X, padx=30, pady=(30, 10))

        title = tk.Label(
            header_frame,
            text="🎮 CONTRÔLES MANETTE",
            font=('Segoe UI', 28, 'bold'),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text']
        )
        title.pack()

        subtitle = tk.Label(
            header_frame,
            text="Configuration active des boutons et actions",
            font=('Segoe UI', 12),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text_dim']
        )
        subtitle.pack()

        # Zone de défilement
        main_container = tk.Frame(self.root, bg=self.COLORS['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        # Canvas pour le scroll
        canvas = tk.Canvas(main_container, bg=self.COLORS['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.COLORS['bg'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Section Boutons (seulement si des boutons sont configurés)
        if self.button_controls:
            buttons_label = tk.Label(
                scrollable_frame,
                text="BOUTONS CONFIGURÉS",
                font=('Segoe UI', 16, 'bold'),
                bg=self.COLORS['bg'],
                fg=self.COLORS['text']
            )
            buttons_label.pack(anchor='w', pady=(10, 15))

            # Grille de boutons
            buttons_grid = tk.Frame(scrollable_frame, bg=self.COLORS['bg'])
            buttons_grid.pack(fill=tk.X, pady=(0, 20))

            # Créer les cartes de boutons (2 colonnes)
            for i, (btn_id, btn_info) in enumerate(self.button_controls.items()):
                row = i // 2
                col = i % 2
                self._create_button_card(buttons_grid, btn_id, btn_info, row, col)

        # Section Axes (Joysticks) - seulement si configurés
        if self.axis_controls:
            axes_label = tk.Label(
                scrollable_frame,
                text="JOYSTICKS & AXES",
                font=('Segoe UI', 16, 'bold'),
                bg=self.COLORS['bg'],
                fg=self.COLORS['text']
            )
            axes_label.pack(anchor='w', pady=(20, 15))

            # Cartes des axes
            for axis_id, axis_info in self.axis_controls.items():
                self._create_axis_card(scrollable_frame, axis_id, axis_info)

        # Message si aucune configuration
        if not self.button_controls and not self.axis_controls:
            empty_label = tk.Label(
                scrollable_frame,
                text="Aucun contrôle configuré dans voice_config.json",
                font=('Segoe UI', 14),
                bg=self.COLORS['bg'],
                fg=self.COLORS['text_dim']
            )
            empty_label.pack(pady=50)

        # Packing du canvas
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Zone de statut pour les modes actifs
        status_container = tk.Frame(self.root, bg=self.COLORS['bg'])
        status_container.pack(side=tk.BOTTOM, fill=tk.X, padx=30, pady=(10, 5))

        self.status_label = tk.Label(
            status_container,
            text="",
            font=('Segoe UI', 11, 'bold'),
            bg=self.COLORS['bg'],
            fg=self.COLORS['success'],
            anchor='w'
        )
        self.status_label.pack(fill=tk.X)

        # Pied de page avec chemin de config
        config_path = "config/voice_config.json"
        footer = tk.Label(
            self.root,
            text=f"JARVIS V2 • Configuration: {config_path}",
            font=('Segoe UI', 9),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text_dim']
        )
        footer.pack(side=tk.BOTTOM, pady=(0, 15))

    def _create_button_card(self, parent: tk.Frame, btn_id: int, btn_info: dict, row: int, col: int):
        """Crée une carte pour un bouton"""

        # Carte principale
        card = tk.Frame(
            parent,
            bg=self.COLORS['card_bg'],
            highlightbackground=self.COLORS['accent'],
            highlightthickness=2
        )
        card.grid(row=row, column=col, padx=10, pady=10, sticky='ew')
        parent.grid_columnconfigure(col, weight=1)

        # Conteneur interne
        content = tk.Frame(card, bg=self.COLORS['card_bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # En-tête avec indicateur
        header = tk.Frame(content, bg=self.COLORS['card_bg'])
        header.pack(fill=tk.X, pady=(0, 10))

        # Indicateur d'état (LED)
        indicator = tk.Frame(
            header,
            width=12,
            height=12,
            bg=self.COLORS['accent']
        )
        indicator.pack(side=tk.LEFT, padx=(0, 10))
        self.button_indicators[btn_id] = indicator

        # Nom du bouton
        btn_label = tk.Label(
            header,
            text=btn_info['label'],
            font=('Segoe UI', 13, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=btn_info['color']
        )
        btn_label.pack(side=tk.LEFT)

        # Action
        action_label = tk.Label(
            content,
            text=f"→ {btn_info['action']}",
            font=('Segoe UI', 11),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        )
        action_label.pack(anchor='w')

        # Numéro du bouton (petit texte en bas)
        num_label = tk.Label(
            content,
            text=f"Bouton #{btn_id}",
            font=('Segoe UI', 9),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text_dim']
        )
        num_label.pack(anchor='w', pady=(5, 0))

        self.button_labels[btn_id] = btn_label

    def _create_axis_card(self, parent: tk.Frame, axis_id: int, axis_info: dict):
        """Crée une carte pour un axe"""

        card = tk.Frame(
            parent,
            bg=self.COLORS['card_bg'],
            highlightbackground=self.COLORS['accent'],
            highlightthickness=2
        )
        card.pack(fill=tk.X, padx=10, pady=10)

        content = tk.Frame(card, bg=self.COLORS['card_bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Nom de l'axe
        name_label = tk.Label(
            content,
            text=axis_info['label'],
            font=('Segoe UI', 13, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['success']
        )
        name_label.pack(anchor='w', pady=(0, 5))

        # Action
        action_label = tk.Label(
            content,
            text=f"→ {axis_info['action']}",
            font=('Segoe UI', 11),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        )
        action_label.pack(anchor='w')

        # Numéro de l'axe
        num_label = tk.Label(
            content,
            text=f"Axe #{axis_id}",
            font=('Segoe UI', 9),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text_dim']
        )
        num_label.pack(anchor='w', pady=(5, 0))

    def _init_gamepad(self):
        """Initialise pygame et la manette"""
        try:
            pygame.init()
            pygame.joystick.init()

            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                print(f"Manette connectée : {self.joystick.get_name()}")
                self.running = True
            else:
                print("Aucune manette détectée")

        except Exception as e:
            print(f"Erreur d'initialisation : {e}")

    def _update_gamepad_state(self):
        """Met à jour l'état de la manette et l'affichage"""
        if not self.running or not self.joystick:
            return

        try:
            # Traiter les événements pygame
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    self._on_button_press(event.button)
                elif event.type == pygame.JOYBUTTONUP:
                    self._on_button_release(event.button)

            # Synchroniser l'affichage avec le contrôleur (toutes les 500ms)
            if hasattr(self, '_sync_counter'):
                self._sync_counter += 1
                if self._sync_counter >= 10:  # 10 * 50ms = 500ms
                    self._sync_counter = 0
                    self._update_status_display()
            else:
                self._sync_counter = 0

            # Mettre à jour à nouveau après 50ms
            self.root.after(50, self._update_gamepad_state)

        except Exception as e:
            print(f"Erreur lors de la mise à jour : {e}")

    def _on_button_press(self, button_id: int):
        """Gère l'appui sur un bouton"""
        # Éviter les déclenchements multiples - ne traiter que si le bouton n'était pas déjà pressé
        if self.button_pressed_flags.get(button_id, False):
            return

        self.button_pressed_flags[button_id] = True

        if button_id in self.button_indicators:
            # Changer la couleur de l'indicateur
            color = self.button_controls[button_id]['color']
            self.button_indicators[button_id].configure(bg=color)

            # Animer le label
            self.button_labels[button_id].configure(
                font=('Segoe UI', 14, 'bold'),
                fg=self.COLORS['active']
            )

            # Gérer les actions toggle
            self._handle_toggle_action(button_id)

    def _on_button_release(self, button_id: int):
        """Gère le relâchement d'un bouton"""
        # Réinitialiser le flag de pression
        self.button_pressed_flags[button_id] = False

        if button_id in self.button_indicators:
            # Remettre la couleur normale
            self.button_indicators[button_id].configure(bg=self.COLORS['accent'])

            # Remettre le label normal
            color = self.button_controls[button_id]['color']
            self.button_labels[button_id].configure(
                font=('Segoe UI', 13, 'bold'),
                fg=color
            )

    def _handle_toggle_action(self, button_id: int):
        """Gère les actions de type toggle"""
        if button_id not in self.button_controls:
            return

        btn_config = None
        # Retrouver la config du bouton
        button_mapping = self.config.get('button_mapping', {})
        for btn_id_str, config in button_mapping.items():
            if int(btn_id_str) == button_id:
                btn_config = config
                break

        if not btn_config:
            return

        action = btn_config.get('action', '')

        # Gérer le toggle du mode ClaudeIA
        if action == 'toggle_claude_mode':
            # Toggle l'état
            current_state = self.toggle_states.get(button_id, False)
            new_state = not current_state
            self.toggle_states[button_id] = new_state

            # Log pour debug
            print(f"[DEBUG] Bouton {button_id} toggle: {current_state} -> {new_state}")

            # Mettre à jour l'affichage
            self._update_status_display()

    def _update_status_display(self):
        """Met à jour l'affichage du statut en se synchronisant avec le contrôleur"""
        if not self.status_label:
            return

        status_messages = []

        # Si on a une référence au contrôleur, utiliser son état
        if self.controller and hasattr(self.controller, 'claude_mode_active'):
            if self.controller.claude_mode_active:
                status_messages.append("✅ Mode ClaudeIA dans VSCode Auto activé")
        else:
            # Sinon, utiliser l'état local de l'UI
            button_mapping = self.config.get('button_mapping', {})
            for btn_id_str, btn_config in button_mapping.items():
                btn_id = int(btn_id_str)
                action = btn_config.get('action', '')

                if action == 'toggle_claude_mode' and self.toggle_states.get(btn_id, False):
                    status_messages.append("✅ Mode ClaudeIA dans VSCode Auto activé")

        # Afficher le statut
        if status_messages:
            self.status_label.configure(text=" • ".join(status_messages))
        else:
            self.status_label.configure(text="")

    def cleanup(self):
        """Nettoie les ressources"""
        self.running = False
        if self.joystick:
            self.joystick.quit()
        pygame.quit()


def main():
    """Point d'entrée principal"""
    root = tk.Tk()
    app = ModernGamepadUI(root, config_path="config/voice_config.json")

    def on_closing():
        app.cleanup()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
