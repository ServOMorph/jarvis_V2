"""
Interface graphique moderne pour afficher les contrôles de la manette
"""

import tkinter as tk
from tkinter import ttk
import pygame
import json
from pathlib import Path
from typing import Dict, Optional
import sys
import os

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import MouseConfig, ScrollConfig


class MouseConfigWindow:
    """Fenêtre de configuration des paramètres de la souris"""

    # Valeurs par défaut (depuis MouseConfig et ScrollConfig)
    DEFAULT_VALUES = {
        'SENSITIVITY': 20.0,
        'MAX_SENSITIVITY': 60.0,
        'ACCELERATION_CURVE': 2.0,
        'SMOOTHING': 0.3,
        'PRECISION_DIVIDER': 3.0,
        'DEADZONE': 0.15,
        # Scroll
        'SCROLL_SENSITIVITY': 50.0,
        'SCROLL_ACCELERATION_CURVE': 1.3,
        'SCROLL_DEADZONE': 0.10
    }

    # Fichier de sauvegarde des réglages
    SETTINGS_FILE = Path(__file__).parent.parent / 'config' / 'mouse_settings.json'

    def __init__(self, parent, controller):
        """
        Initialise la fenêtre de configuration

        Args:
            parent: Fenêtre parent
            controller: Référence au contrôleur pour modifier les paramètres en temps réel
        """
        self.controller = controller
        self.window = tk.Toplevel(parent)
        self.window.title("⚙️ Configuration Souris & Scroll")
        self.window.geometry("650x850")
        self.window.configure(bg='#1a1a2e')
        self.window.resizable(False, False)

        # Variables pour les sliders
        self.vars = {}

        # Canvas pour cleanup
        self.canvas = None

        # Charger les réglages sauvegardés
        self._load_saved_settings()

        self._create_ui()

        # Nettoyer les bindings à la fermeture
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_ui(self):
        """Crée l'interface de configuration"""

        # En-tête
        header = tk.Label(
            self.window,
            text="⚙️ CONFIGURATION DE LA SOURIS",
            font=('Segoe UI', 20, 'bold'),
            bg='#1a1a2e',
            fg='#eaeaea'
        )
        header.pack(pady=(20, 10))

        subtitle = tk.Label(
            self.window,
            text="Ajustez les paramètres en temps réel",
            font=('Segoe UI', 11),
            bg='#1a1a2e',
            fg='#a0a0a0'
        )
        subtitle.pack(pady=(0, 20))

        # Conteneur pour la zone scrollable
        container = tk.Frame(self.window, bg='#1a1a2e')
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        # Canvas pour le scroll
        self.canvas = tk.Canvas(container, bg='#1a1a2e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)

        # Frame principal avec scroll
        main_frame = tk.Frame(self.canvas, bg='#1a1a2e')

        # Configuration du scroll
        main_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=main_frame, anchor="nw", width=580)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Permettre le scroll avec la molette
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Packing du canvas et scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Sensibilité
        self._create_slider(
            main_frame,
            "Sensibilité de base",
            "Vitesse du curseur (mouvements légers)",
            MouseConfig.SENSITIVITY,
            5.0, 100.0,
            lambda v: self._update_config('SENSITIVITY', v)
        )

        # Sensibilité maximale
        self._create_slider(
            main_frame,
            "Sensibilité maximale",
            "Vitesse maximale (joystick à fond)",
            MouseConfig.MAX_SENSITIVITY,
            10.0, 150.0,
            lambda v: self._update_config('MAX_SENSITIVITY', v)
        )

        # Courbe d'accélération
        self._create_slider(
            main_frame,
            "Accélération",
            "1.0 = Linéaire, >2.0 = Accélération progressive",
            MouseConfig.ACCELERATION_CURVE,
            1.0, 4.0,
            lambda v: self._update_config('ACCELERATION_CURVE', v),
            resolution=0.1
        )

        # Lissage
        self._create_slider(
            main_frame,
            "Lissage",
            "0.0 = Aucun, 1.0 = Maximum (réduit les saccades)",
            MouseConfig.SMOOTHING,
            0.0, 0.9,
            lambda v: self._update_config('SMOOTHING', v),
            resolution=0.05
        )

        # Multiplicateur de boost
        self._create_slider(
            main_frame,
            "Mode Boost (Bouton RB/R1)",
            "Multiplicateur de vitesse (plus élevé = plus rapide)",
            MouseConfig.PRECISION_DIVIDER,
            1.5, 10.0,
            lambda v: self._update_config('PRECISION_DIVIDER', v),
            resolution=0.5
        )

        # Zone morte
        self._create_slider(
            main_frame,
            "Zone morte du joystick",
            "Seuil avant mouvement (évite le drift)",
            MouseConfig.DEADZONE,
            0.0, 0.4,
            lambda v: self._update_config('DEADZONE', v),
            resolution=0.01
        )

        # Séparateur
        separator = tk.Frame(main_frame, height=2, bg='#533483')
        separator.pack(fill=tk.X, pady=20, padx=20)

        # Titre section SCROLL
        scroll_title = tk.Label(
            main_frame,
            text="🖱️ CONFIGURATION DU SCROLL",
            font=('Segoe UI', 14, 'bold'),
            bg='#1a1a2e',
            fg='#00d9ff'
        )
        scroll_title.pack(pady=(10, 20))

        # Sensibilité du scroll
        self._create_slider(
            main_frame,
            "Sensibilité du scroll",
            "Vitesse de défilement avec le joystick droit (10-6000 pour vitesse ultra-extrême)",
            ScrollConfig.SENSITIVITY,
            10.0, 6000.0,
            lambda v: self._update_scroll_config('SENSITIVITY', v),
            resolution=20.0
        )

        # Accélération du scroll
        self._create_slider(
            main_frame,
            "Accélération du scroll",
            "1.0 = Linéaire, >1.5 = Accélération progressive",
            ScrollConfig.ACCELERATION_CURVE,
            1.0, 3.0,
            lambda v: self._update_scroll_config('ACCELERATION_CURVE', v),
            resolution=0.1
        )

        # Zone morte du scroll
        self._create_slider(
            main_frame,
            "Zone morte du scroll",
            "Seuil avant défilement",
            ScrollConfig.DEADZONE,
            0.0, 0.3,
            lambda v: self._update_scroll_config('DEADZONE', v),
            resolution=0.01
        )

        # Boutons Reset, Appliquer et Fermer (en bas de la fenêtre, hors scroll)
        bottom_frame = tk.Frame(self.window, bg='#1a1a2e')
        bottom_frame.pack(pady=(10, 20))

        # Bouton Reset
        reset_btn = tk.Button(
            bottom_frame,
            text="🔄 Réinitialiser",
            font=('Segoe UI', 11, 'bold'),
            bg='#533483',
            fg='white',
            activebackground='#6b4498',
            activeforeground='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self._reset_to_defaults
        )
        reset_btn.pack(side=tk.LEFT, padx=5)

        # Bouton Appliquer
        apply_btn = tk.Button(
            bottom_frame,
            text="✓ Appliquer",
            font=('Segoe UI', 11, 'bold'),
            bg='#00d9ff',
            fg='#1a1a2e',
            activebackground='#00b8d4',
            activeforeground='#1a1a2e',
            relief=tk.FLAT,
            padx=25,
            pady=10,
            command=self._apply_config
        )
        apply_btn.pack(side=tk.LEFT, padx=5)

        # Bouton fermer
        close_btn = tk.Button(
            bottom_frame,
            text="Fermer",
            font=('Segoe UI', 11, 'bold'),
            bg='#e94560',
            fg='white',
            activebackground='#c93550',
            activeforeground='white',
            relief=tk.FLAT,
            padx=25,
            pady=10,
            command=self.window.destroy
        )
        close_btn.pack(side=tk.LEFT, padx=5)

    def _create_slider(self, parent, title, description, default_value, from_, to_, command, resolution=1.0):
        """Crée un slider avec son label"""

        frame = tk.Frame(parent, bg='#16213e', highlightbackground='#0f3460', highlightthickness=2)
        frame.pack(fill=tk.X, pady=8, padx=10)

        inner = tk.Frame(frame, bg='#16213e')
        inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)

        # Titre
        title_label = tk.Label(
            inner,
            text=title,
            font=('Segoe UI', 12, 'bold'),
            bg='#16213e',
            fg='#eaeaea'
        )
        title_label.pack(anchor='w')

        # Description
        desc_label = tk.Label(
            inner,
            text=description,
            font=('Segoe UI', 9),
            bg='#16213e',
            fg='#a0a0a0'
        )
        desc_label.pack(anchor='w', pady=(2, 8))

        # Frame pour slider et valeur
        slider_frame = tk.Frame(inner, bg='#16213e')
        slider_frame.pack(fill=tk.X)

        # Variable
        var = tk.DoubleVar(value=default_value)
        self.vars[title] = var

        # Label de valeur
        value_label = tk.Label(
            slider_frame,
            text=f"{default_value:.2f}",
            font=('Segoe UI', 11, 'bold'),
            bg='#16213e',
            fg='#00d9ff',
            width=8
        )
        value_label.pack(side=tk.RIGHT, padx=(10, 0))

        # Slider
        slider = tk.Scale(
            slider_frame,
            from_=from_,
            to=to_,
            resolution=resolution,
            orient=tk.HORIZONTAL,
            variable=var,
            bg='#16213e',
            fg='#eaeaea',
            highlightthickness=0,
            troughcolor='#0f3460',
            activebackground='#00d9ff',
            command=lambda v: self._on_slider_change(v, value_label, command)
        )
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _on_slider_change(self, value, label, command):
        """Callback quand un slider change"""
        label.configure(text=f"{float(value):.2f}")
        command(float(value))

    def _create_preset_button(self, parent, text, command):
        """Crée un bouton de préréglage"""
        return tk.Button(
            parent,
            text=text,
            font=('Segoe UI', 10, 'bold'),
            bg='#533483',
            fg='white',
            activebackground='#6b4498',
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=command
        )

    def _update_config(self, param_name, value):
        """Met à jour un paramètre en temps réel"""
        if not self.controller or not hasattr(self.controller, 'smooth_mouse'):
            return

        mouse = self.controller.smooth_mouse

        # Mettre à jour le paramètre correspondant
        if param_name == 'SENSITIVITY':
            mouse.sensitivity = value
        elif param_name == 'MAX_SENSITIVITY':
            mouse.max_sensitivity = value
        elif param_name == 'ACCELERATION_CURVE':
            mouse.acceleration_curve = value
        elif param_name == 'SMOOTHING':
            mouse.smoothing = value
        elif param_name == 'PRECISION_DIVIDER':
            mouse.precision_divider = value
        elif param_name == 'DEADZONE':
            mouse.deadzone = value

    def _update_scroll_config(self, param_name, value):
        """Met à jour un paramètre du scroll en temps réel"""
        if not self.controller or not hasattr(self.controller, 'smooth_scroll'):
            return

        scroll = self.controller.smooth_scroll

        # Mettre à jour le paramètre correspondant
        if param_name == 'SENSITIVITY':
            scroll.sensitivity = value
        elif param_name == 'ACCELERATION_CURVE':
            scroll.acceleration_curve = value
        elif param_name == 'DEADZONE':
            scroll.deadzone = value

    def _preset_gaming(self):
        """Préréglage pour le jeu"""
        self._set_all_values(35.0, 80.0, 2.2, 0.2, 3.0, 0.12)

    def _preset_office(self):
        """Préréglage pour la bureautique"""
        self._set_all_values(25.0, 50.0, 1.8, 0.4, 4.0, 0.15)

    def _preset_precision(self):
        """Préréglage pour la précision"""
        self._set_all_values(15.0, 40.0, 1.2, 0.5, 5.0, 0.10)

    def _reset_to_defaults(self):
        """Réinitialise tous les paramètres aux valeurs par défaut"""
        self._set_all_values(
            self.DEFAULT_VALUES['SENSITIVITY'],
            self.DEFAULT_VALUES['MAX_SENSITIVITY'],
            self.DEFAULT_VALUES['ACCELERATION_CURVE'],
            self.DEFAULT_VALUES['SMOOTHING'],
            self.DEFAULT_VALUES['PRECISION_DIVIDER'],
            self.DEFAULT_VALUES['DEADZONE'],
            self.DEFAULT_VALUES['SCROLL_SENSITIVITY'],
            self.DEFAULT_VALUES['SCROLL_ACCELERATION_CURVE'],
            self.DEFAULT_VALUES['SCROLL_DEADZONE']
        )
        print("[Config] Paramètres réinitialisés aux valeurs par défaut (souris + scroll)")

    def _apply_config(self):
        """Applique et sauvegarde les paramètres dans config.py"""
        try:
            # Récupérer les valeurs actuelles
            values_list = list(self.vars.values())
            if len(values_list) != 9:
                print(f"[Erreur] Nombre de paramètres incorrect: {len(values_list)}, attendu 9")
                return

            sens = values_list[0].get()
            max_sens = values_list[1].get()
            accel = values_list[2].get()
            smooth = values_list[3].get()
            precision = values_list[4].get()
            deadzone = values_list[5].get()
            scroll_sens = values_list[6].get()
            scroll_accel = values_list[7].get()
            scroll_deadzone = values_list[8].get()

            # Lire le fichier config.py
            config_path = Path(__file__).parent.parent / 'config.py'
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Remplacer les valeurs dans le contenu
            import re

            # Fonction pour remplacer une valeur dans une classe spécifique
            def replace_value_in_class(class_name, var_name, new_value):
                nonlocal content
                # Pattern pour trouver la classe
                class_pattern = rf'class {class_name}:.*?(?=class |\Z)'
                class_match = re.search(class_pattern, content, re.DOTALL)

                if class_match:
                    class_content = class_match.group(0)
                    # Pattern pour trouver la variable dans cette classe
                    var_pattern = rf'(\n\s+{var_name}\s*=\s*)([0-9.]+)'
                    var_match = re.search(var_pattern, class_content)

                    if var_match:
                        old_value = var_match.group(2)
                        old_line = var_match.group(1) + old_value
                        new_line = var_match.group(1) + str(new_value)
                        content = content.replace(old_line, new_line, 1)
                        print(f"[Debug] Remplacé {class_name}.{var_name}: {old_value} -> {new_value}")
                    else:
                        print(f"[Warning] Variable {var_name} non trouvée dans {class_name}")
                else:
                    print(f"[Warning] Classe {class_name} non trouvée")

            # Remplacer les paramètres de MouseConfig
            replace_value_in_class('MouseConfig', 'SENSITIVITY', sens)
            replace_value_in_class('MouseConfig', 'MAX_SENSITIVITY', max_sens)
            replace_value_in_class('MouseConfig', 'ACCELERATION_CURVE', accel)
            replace_value_in_class('MouseConfig', 'SMOOTHING', smooth)
            replace_value_in_class('MouseConfig', 'PRECISION_DIVIDER', precision)
            replace_value_in_class('MouseConfig', 'DEADZONE', deadzone)

            # Remplacer les paramètres de ScrollConfig
            replace_value_in_class('ScrollConfig', 'SENSITIVITY', scroll_sens)
            replace_value_in_class('ScrollConfig', 'ACCELERATION_CURVE', scroll_accel)
            replace_value_in_class('ScrollConfig', 'DEADZONE', scroll_deadzone)

            # Écrire le fichier modifié
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Mettre à jour aussi les valeurs en mémoire
            MouseConfig.SENSITIVITY = sens
            MouseConfig.MAX_SENSITIVITY = max_sens
            MouseConfig.ACCELERATION_CURVE = accel
            MouseConfig.SMOOTHING = smooth
            MouseConfig.PRECISION_DIVIDER = precision
            MouseConfig.DEADZONE = deadzone

            ScrollConfig.SENSITIVITY = scroll_sens
            ScrollConfig.ACCELERATION_CURVE = scroll_accel
            ScrollConfig.DEADZONE = scroll_deadzone

            # Appliquer au contrôleur en temps réel
            if self.controller:
                if hasattr(self.controller, 'smooth_mouse'):
                    mouse = self.controller.smooth_mouse
                    mouse.sensitivity = sens
                    mouse.max_sensitivity = max_sens
                    mouse.acceleration_curve = accel
                    mouse.smoothing = smooth
                    mouse.precision_divider = precision
                    mouse.deadzone = deadzone

                if hasattr(self.controller, 'smooth_scroll'):
                    scroll = self.controller.smooth_scroll
                    scroll.sensitivity = scroll_sens
                    scroll.acceleration_curve = scroll_accel
                    scroll.deadzone = scroll_deadzone

            print(f"[Config] Paramètres sauvegardés dans config.py")
            print(f"  SOURIS:")
            print(f"    - Sensibilité: {sens}")
            print(f"    - Sensibilité max: {max_sens}")
            print(f"    - Accélération: {accel}")
            print(f"    - Lissage: {smooth}")
            print(f"    - Précision: {precision}")
            print(f"    - Zone morte: {deadzone}")
            print(f"  SCROLL:")
            print(f"    - Sensibilité: {scroll_sens}")
            print(f"    - Accélération: {scroll_accel}")
            print(f"    - Zone morte: {scroll_deadzone}")

            # Afficher un message de confirmation dans l'UI
            self._show_confirmation()

        except Exception as e:
            print(f"[Erreur] Impossible de sauvegarder la configuration: {e}")
            import traceback
            traceback.print_exc()

    def _show_confirmation(self):
        """Affiche un message de confirmation temporaire"""
        # Créer un label de confirmation
        confirm_label = tk.Label(
            self.window,
            text="✓ Configuration appliquée et sauvegardée !",
            font=('Segoe UI', 10, 'bold'),
            bg='#00d9ff',
            fg='#1a1a2e',
            padx=15,
            pady=5
        )
        confirm_label.place(relx=0.5, rely=0.95, anchor='center')

        # Supprimer le message après 2 secondes
        self.window.after(2000, confirm_label.destroy)

    def _set_all_values(self, sens, max_sens, accel, smooth, precision, deadzone, scroll_sens=None, scroll_accel=None, scroll_deadzone=None):
        """Définit toutes les valeurs (souris + optionnellement scroll)"""
        if scroll_sens is not None and scroll_accel is not None and scroll_deadzone is not None:
            # Mode complet avec 9 paramètres (souris + scroll)
            values = [sens, max_sens, accel, smooth, precision, deadzone, scroll_sens, scroll_accel, scroll_deadzone]
        else:
            # Mode rétrocompatible avec 6 paramètres (souris uniquement)
            values = [sens, max_sens, accel, smooth, precision, deadzone]

        for var, value in zip(self.vars.values(), values):
            var.set(value)

    def _load_saved_settings(self):
        """Charge les réglages sauvegardés depuis le fichier JSON"""
        try:
            if self.SETTINGS_FILE.exists():
                import json
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    mouse_settings = data.get('mouse', {})
                    scroll_settings = data.get('scroll', {})

                    # Mettre à jour les valeurs par défaut avec les valeurs sauvegardées
                    if mouse_settings:
                        self.DEFAULT_VALUES.update({
                            'SENSITIVITY': mouse_settings.get('sensitivity', self.DEFAULT_VALUES['SENSITIVITY']),
                            'MAX_SENSITIVITY': mouse_settings.get('max_sensitivity', self.DEFAULT_VALUES['MAX_SENSITIVITY']),
                            'ACCELERATION_CURVE': mouse_settings.get('acceleration_curve', self.DEFAULT_VALUES['ACCELERATION_CURVE']),
                            'SMOOTHING': mouse_settings.get('smoothing', self.DEFAULT_VALUES['SMOOTHING']),
                            'PRECISION_DIVIDER': mouse_settings.get('precision_divider', self.DEFAULT_VALUES['PRECISION_DIVIDER']),
                            'DEADZONE': mouse_settings.get('deadzone', self.DEFAULT_VALUES['DEADZONE'])
                        })

                        # Appliquer directement au contrôleur si disponible
                        if self.controller and hasattr(self.controller, 'smooth_mouse'):
                            mouse = self.controller.smooth_mouse
                            mouse.sensitivity = self.DEFAULT_VALUES['SENSITIVITY']
                            mouse.max_sensitivity = self.DEFAULT_VALUES['MAX_SENSITIVITY']
                            mouse.acceleration_curve = self.DEFAULT_VALUES['ACCELERATION_CURVE']
                            mouse.smoothing = self.DEFAULT_VALUES['SMOOTHING']
                            mouse.precision_divider = self.DEFAULT_VALUES['PRECISION_DIVIDER']
                            mouse.deadzone = self.DEFAULT_VALUES['DEADZONE']

                    if scroll_settings:
                        self.DEFAULT_VALUES.update({
                            'SCROLL_SENSITIVITY': scroll_settings.get('sensitivity', self.DEFAULT_VALUES['SCROLL_SENSITIVITY']),
                            'SCROLL_ACCELERATION_CURVE': scroll_settings.get('acceleration_curve', self.DEFAULT_VALUES['SCROLL_ACCELERATION_CURVE']),
                            'SCROLL_DEADZONE': scroll_settings.get('deadzone', self.DEFAULT_VALUES['SCROLL_DEADZONE'])
                        })

                        # Appliquer directement au contrôleur si disponible
                        if self.controller and hasattr(self.controller, 'smooth_scroll'):
                            scroll = self.controller.smooth_scroll
                            scroll.sensitivity = self.DEFAULT_VALUES['SCROLL_SENSITIVITY']
                            scroll.acceleration_curve = self.DEFAULT_VALUES['SCROLL_ACCELERATION_CURVE']
                            scroll.deadzone = self.DEFAULT_VALUES['SCROLL_DEADZONE']

                        print("[Config] Réglages chargés depuis mouse_settings.json")
        except Exception as e:
            print(f"[Config] Impossible de charger les réglages: {e}")

    def _save_settings(self):
        """Sauvegarde les réglages actuels dans le fichier JSON"""
        try:
            # Récupérer les valeurs actuelles
            values_list = list(self.vars.values())
            if len(values_list) != 9:
                print(f"[Erreur] Nombre de paramètres incorrect pour la sauvegarde: {len(values_list)}, attendu 9")
                return

            settings_data = {
                "mouse": {
                    "sensitivity": values_list[0].get(),
                    "max_sensitivity": values_list[1].get(),
                    "acceleration_curve": values_list[2].get(),
                    "smoothing": values_list[3].get(),
                    "precision_divider": values_list[4].get(),
                    "deadzone": values_list[5].get()
                },
                "scroll": {
                    "sensitivity": values_list[6].get(),
                    "acceleration_curve": values_list[7].get(),
                    "deadzone": values_list[8].get()
                }
            }

            # Créer le dossier config s'il n'existe pas
            self.SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

            # Écrire le fichier JSON
            import json
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2, ensure_ascii=False)

            print(f"[Config] Réglages sauvegardés dans {self.SETTINGS_FILE.name}")
        except Exception as e:
            print(f"[Erreur] Impossible de sauvegarder les réglages: {e}")
            import traceback
            traceback.print_exc()

    def _on_close(self):
        """Nettoie les ressources avant de fermer la fenêtre"""
        # Sauvegarder automatiquement les réglages
        self._save_settings()

        # Unbind la molette de la souris
        if self.canvas:
            self.canvas.unbind_all("<MouseWheel>")

        # Fermer la fenêtre
        self.window.destroy()


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

        # Indicateur d'état de la manette
        self.gamepad_status_indicator = tk.Label(
            header_frame,
            text="✅ MANETTE ACTIVE",
            font=('Segoe UI', 14, 'bold'),
            bg='#00d900',
            fg='white',
            padx=20,
            pady=8,
            relief=tk.FLAT
        )
        self.gamepad_status_indicator.pack(pady=(10, 0))

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

        # Boutons de contrôle (Configuration et Affichage)
        config_button_frame = tk.Frame(self.root, bg=self.COLORS['bg'])
        config_button_frame.pack(side=tk.BOTTOM, pady=(10, 5))

        # Bouton Toggle Manette (Activer/Désactiver)
        self.toggle_btn = tk.Button(
            config_button_frame,
            text="✅ Manette ACTIVÉE",
            font=('Segoe UI', 12, 'bold'),
            bg='#00d900',
            fg='white',
            activebackground='#00b000',
            activeforeground='white',
            relief=tk.FLAT,
            padx=30,
            pady=12,
            command=self._toggle_gamepad
        )
        self.toggle_btn.pack(side=tk.LEFT, padx=5)

        # Bouton Affichage Contrôle
        display_btn = tk.Button(
            config_button_frame,
            text="🎮 Affichage Contrôle",
            font=('Segoe UI', 11, 'bold'),
            bg=self.COLORS['primary'],
            fg=self.COLORS['text'],
            activebackground='#c93550',
            activeforeground=self.COLORS['text'],
            relief=tk.FLAT,
            padx=25,
            pady=10,
            command=self._open_gamepad_image
        )
        display_btn.pack(side=tk.LEFT, padx=5)

        # Bouton Configuration Souris
        config_btn = tk.Button(
            config_button_frame,
            text="⚙️ Configuration Souris",
            font=('Segoe UI', 11, 'bold'),
            bg=self.COLORS['secondary'],
            fg=self.COLORS['text'],
            activebackground='#6b4498',
            activeforeground=self.COLORS['text'],
            relief=tk.FLAT,
            padx=25,
            pady=10,
            command=self._open_mouse_config
        )
        config_btn.pack(side=tk.LEFT, padx=5)

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

    def _toggle_gamepad(self):
        """Active ou désactive les commandes de la manette"""
        if self.controller:
            # Inverser l'état
            self.controller.gamepad_enabled = not self.controller.gamepad_enabled

            # Mettre à jour l'apparence du bouton et de l'indicateur
            if self.controller.gamepad_enabled:
                # État ACTIVÉ
                self.toggle_btn.configure(
                    text="✅ Manette ACTIVÉE",
                    bg='#00d900',
                    activebackground='#00b000'
                )
                self.gamepad_status_indicator.configure(
                    text="✅ MANETTE ACTIVE",
                    bg='#00d900'
                )
                print("[UI] ✅ Commandes de la manette ACTIVÉES")
            else:
                # État DÉSACTIVÉ
                self.toggle_btn.configure(
                    text="❌ Manette DÉSACTIVÉE",
                    bg='#e94560',
                    activebackground='#c93550'
                )
                self.gamepad_status_indicator.configure(
                    text="❌ MANETTE DÉSACTIVÉE (Mode Jeu)",
                    bg='#e94560'
                )
                print("[UI] ❌ Commandes de la manette DÉSACTIVÉES - Vous pouvez jouer à un jeu")
        else:
            print("[UI] Aucun contrôleur lié")

    def _open_mouse_config(self):
        """Ouvre la fenêtre de configuration de la souris"""
        if self.controller:
            MouseConfigWindow(self.root, self.controller)
        else:
            print("[UI] Aucun contrôleur lié, impossible d'ouvrir la configuration")

    def _open_gamepad_image(self):
        """Ouvre l'image de la manette dans une nouvelle fenêtre"""
        try:
            from PIL import Image, ImageTk
            import os

            # Chemin de l'image
            image_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "assets", "images", "manette.png"
            )

            # Vérifier si l'image existe
            if not os.path.exists(image_path):
                print(f"[UI] Image introuvable : {image_path}")
                # Afficher une fenêtre d'erreur
                error_window = tk.Toplevel(self.root)
                error_window.title("⚠️ Erreur")
                error_window.geometry("400x150")
                error_window.configure(bg=self.COLORS['bg'])
                error_window.resizable(False, False)

                error_label = tk.Label(
                    error_window,
                    text="❌ Image de la manette introuvable",
                    font=('Segoe UI', 14, 'bold'),
                    bg=self.COLORS['bg'],
                    fg=self.COLORS['primary']
                )
                error_label.pack(pady=20)

                path_label = tk.Label(
                    error_window,
                    text=f"Chemin recherché :\n{image_path}",
                    font=('Segoe UI', 9),
                    bg=self.COLORS['bg'],
                    fg=self.COLORS['text_dim']
                )
                path_label.pack(pady=10)

                ok_btn = tk.Button(
                    error_window,
                    text="OK",
                    font=('Segoe UI', 10, 'bold'),
                    bg=self.COLORS['primary'],
                    fg='white',
                    relief=tk.FLAT,
                    padx=20,
                    pady=5,
                    command=error_window.destroy
                )
                ok_btn.pack(pady=10)
                return

            # Créer une nouvelle fenêtre
            image_window = tk.Toplevel(self.root)
            image_window.title("🎮 Schéma de la Manette")
            image_window.configure(bg=self.COLORS['bg'])

            # Fermer avec la touche Échap
            image_window.bind('<Escape>', lambda e: image_window.destroy())

            # Charger l'image
            img = Image.open(image_path)

            # Garder la résolution originale pour une qualité maximale
            # Ne redimensionner QUE si l'image est trop grande pour l'écran
            img_width, img_height = img.size

            # Obtenir la taille de l'écran
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            # Marges pour ne pas occuper tout l'écran
            max_width = screen_width - 100
            max_height = screen_height - 200

            # Redimensionner UNIQUEMENT si nécessaire (garde la qualité originale)
            if img_width > max_width or img_height > max_height:
                ratio = min(max_width / img_width, max_height / img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                # NEAREST pour garder la netteté des pixels
                img = img.resize((new_width, new_height), Image.Resampling.NEAREST)

            # Convertir pour tkinter
            photo = ImageTk.PhotoImage(img)

            # Ajuster la taille de la fenêtre (+ d'espace pour le titre et le bouton)
            window_width = img.size[0] + 40
            window_height = img.size[1] + 180  # Augmenté pour le bouton FERMER

            # Centrer la fenêtre
            x = (screen_width - window_width) // 2
            y = max(10, (screen_height - window_height) // 2)
            image_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

            # Permettre le redimensionnement de la fenêtre
            image_window.resizable(True, True)

            # Titre
            title_label = tk.Label(
                image_window,
                text="🎮 SCHÉMA DE LA MANETTE",
                font=('Segoe UI', 18, 'bold'),
                bg=self.COLORS['bg'],
                fg=self.COLORS['success']
            )
            title_label.pack(pady=10)

            # Frame pour l'image
            image_frame = tk.Frame(image_window, bg=self.COLORS['bg'])
            image_frame.pack(pady=10)

            # Afficher l'image
            image_label = tk.Label(image_frame, image=photo, bg=self.COLORS['bg'])
            image_label.image = photo  # Garder une référence pour éviter le garbage collection
            image_label.pack()

            # Frame pour les boutons
            button_frame = tk.Frame(image_window, bg=self.COLORS['bg'])
            button_frame.pack(pady=15)

            # Bouton Fermer (grand et visible)
            close_btn = tk.Button(
                button_frame,
                text="✖ FERMER",
                font=('Segoe UI', 14, 'bold'),
                bg=self.COLORS['primary'],
                fg='white',
                activebackground='#c93550',
                activeforeground='white',
                relief=tk.FLAT,
                padx=40,
                pady=12,
                cursor='hand2',
                command=image_window.destroy
            )
            close_btn.pack()

            # Texte d'aide
            help_text = tk.Label(
                image_window,
                text="(Appuyez sur Échap pour fermer)",
                font=('Segoe UI', 9),
                bg=self.COLORS['bg'],
                fg=self.COLORS['text_dim']
            )
            help_text.pack(pady=(0, 10))

        except ImportError:
            print("[UI] PIL/Pillow n'est pas installé. Installation requise : pip install Pillow")
            # Afficher une fenêtre d'erreur
            error_window = tk.Toplevel(self.root)
            error_window.title("⚠️ Erreur")
            error_window.geometry("450x150")
            error_window.configure(bg=self.COLORS['bg'])
            error_window.resizable(False, False)

            error_label = tk.Label(
                error_window,
                text="❌ Module PIL/Pillow non installé",
                font=('Segoe UI', 14, 'bold'),
                bg=self.COLORS['bg'],
                fg=self.COLORS['primary']
            )
            error_label.pack(pady=20)

            info_label = tk.Label(
                error_window,
                text="Installez Pillow avec : pip install Pillow",
                font=('Segoe UI', 10),
                bg=self.COLORS['bg'],
                fg=self.COLORS['text']
            )
            info_label.pack(pady=10)

            ok_btn = tk.Button(
                error_window,
                text="OK",
                font=('Segoe UI', 10, 'bold'),
                bg=self.COLORS['primary'],
                fg='white',
                relief=tk.FLAT,
                padx=20,
                pady=5,
                command=error_window.destroy
            )
            ok_btn.pack(pady=10)

        except Exception as e:
            print(f"[UI] Erreur lors de l'ouverture de l'image : {e}")
            import traceback
            traceback.print_exc()

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
