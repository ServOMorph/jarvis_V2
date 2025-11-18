"""
Configuration centralisée pour JARVIS V2
Modifiez les valeurs ici pour ajuster le comportement du système
"""

# ============================================================================
# CONFIGURATION DE LA SOURIS
# ============================================================================

class MouseConfig:
    """Configuration du déplacement de la souris avec le joystick"""

    # Sensibilité du mouvement (plus élevé = plus rapide)
    # Valeurs recommandées : 20-50 pour une utilisation normale
    SENSITIVITY = 15.0

    # Sensibilité maximale (lors d'une inclinaison complète du joystick)
    MAX_SENSITIVITY = 40.0

    # Accélération du curseur (courbe exponentielle)
    # 1.0 = linéaire, >1.0 = accélération progressive
    # Valeurs recommandées : 1.5-2.5
    ACCELERATION_CURVE = 1.2

    # Intervalle de mise à jour en secondes (plus petit = plus fluide)
    # Valeurs recommandées : 0.005-0.016 (200Hz à 60Hz)
    UPDATE_INTERVAL = 0.008  # ~125 FPS

    # Zone morte du joystick (0.0-1.0)
    # En dessous de cette valeur, le joystick est considéré au repos
    DEADZONE =  0.1

    # Lissage du mouvement (0.0-1.0)
    # 0.0 = pas de lissage, 1.0 = lissage maximum
    # Réduit les saccades mais ajoute un léger délai
    SMOOTHING = 0.5

    # Mode précision (quand le bouton RB/R1 est maintenu)
    # Diviseur de vitesse pour le mode précision
    # Plus élevé = plus lent et précis
    PRECISION_DIVIDER =5.0  # Divise la vitesse par 3


# ============================================================================
# CONFIGURATION DU SCROLL
# ============================================================================

class ScrollConfig:
    """Configuration du scroll avec le joystick droit"""

    # Sensibilité du scroll (augmentée pour plus de réactivité)
    SENSITIVITY = 50.0

    # Accélération du scroll (réduite pour un contrôle plus linéaire)
    ACCELERATION_CURVE = 1.3

    # Zone morte pour le scroll (réduite pour plus de sensibilité)
    DEADZONE = 0.10


# ============================================================================
# CONFIGURATION DU GAMEPAD
# ============================================================================

class GamepadConfig:
    """Configuration générale du gamepad"""

    # Fréquence de mise à jour du gamepad en Hz
    # Valeurs recommandées : 60-120 Hz
    POLLING_RATE = 120

    # Timeout de connexion en secondes
    CONNECTION_TIMEOUT = 5.0


# ============================================================================
# CONFIGURATION DE LA RECHERCHE D'IMAGE
# ============================================================================

class ImageSearchConfig:
    """Configuration de la recherche d'image"""

    # Intervalle entre les recherches en secondes
    SEARCH_INTERVAL = 0.3

    # Seuil de confiance pour la détection (0.0-1.0)
    # Plus élevé = détection plus stricte
    CONFIDENCE_THRESHOLD = 0.8

    # Délai avant le clic après détection
    CLICK_DELAY = 0.1


# ============================================================================
# CONSEILS D'OPTIMISATION
# ============================================================================

"""
POUR UNE SOURIS PLUS RAPIDE :
- Augmentez MouseConfig.SENSITIVITY (ex: 40-50)
- Augmentez MouseConfig.MAX_SENSITIVITY (ex: 80-100)

POUR UNE SOURIS PLUS FLUIDE :
- Diminuez MouseConfig.UPDATE_INTERVAL (ex: 0.005)
- Augmentez MouseConfig.SMOOTHING (ex: 0.5)
- Diminuez MouseConfig.ACCELERATION_CURVE (ex: 1.5)

POUR UNE SOURIS PLUS PRÉCISE :
- Diminuez MouseConfig.SENSITIVITY (ex: 15-20)
- Augmentez MouseConfig.SMOOTHING (ex: 0.4)
- Diminuez MouseConfig.ACCELERATION_CURVE (ex: 1.2)

POUR UN SCROLL PLUS RAPIDE :
- Augmentez ScrollConfig.SENSITIVITY (ex: 70-100)
- Diminuez ScrollConfig.DEADZONE (ex: 0.05)
- Augmentez ScrollConfig.ACCELERATION_CURVE (ex: 2.0)

POUR UN SCROLL PLUS PRÉCIS :
- Diminuez ScrollConfig.SENSITIVITY (ex: 20-30)
- Augmentez ScrollConfig.DEADZONE (ex: 0.20)
- Diminuez ScrollConfig.ACCELERATION_CURVE (ex: 1.0)

POUR RÉDUIRE LES SACCADES :
- Diminuez MouseConfig.UPDATE_INTERVAL
- Augmentez MouseConfig.SMOOTHING
- Augmentez GamepadConfig.POLLING_RATE
"""
