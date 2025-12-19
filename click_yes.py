import os
import sys
import time

IMAGE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "assets", "images", "yes.png")
)

# Try to reuse project helpers
find_image_fn = None
click_fn = None

try:
    from outils import image_finder  # type: ignore
    for name in ("find_image_on_screen", "find_image", "locate_image", "locate_on_screen"):
        if hasattr(image_finder, name):
            find_image_fn = getattr(image_finder, name)
            break
except Exception:
    find_image_fn = None

try:
    from outils import mouse_controller  # type: ignore
    for name in ("click_at", "click", "mouse_click"):
        if hasattr(mouse_controller, name):
            click_fn = getattr(mouse_controller, name)
            break
except Exception:
    click_fn = None

# Fallback libraries
pyautogui = None
try:
    import pyautogui  # type: ignore
    pyautogui.FAILSAFE = False
except Exception:
    pyautogui = None

keyboard_mod = None
try:
    from pynput import keyboard  # type: ignore
    keyboard_mod = keyboard
except Exception:
    keyboard_mod = None

stop_requested = False

def _center_from_tuple(t):
    if len(t) == 2:
        return int(t[0]), int(t[1])
    if len(t) == 4:
        left, top, w, h = t
        return int(left + w / 2), int(top + h / 2)
    return None

def locate_image_with_project(path):
    if not find_image_fn:
        return None
    try:
        res = find_image_fn(path)
        if res is None:
            return None
        if isinstance(res, tuple):
            return _center_from_tuple(res)
        if isinstance(res, dict) and {"left", "top", "width", "height"}.issubset(res.keys()):
            left = res["left"]; top = res["top"]; w = res["width"]; h = res["height"]
            return int(left + w / 2), int(top + h / 2)
        if hasattr(res, "left") and hasattr(res, "top") and hasattr(res, "width") and hasattr(res, "height"):
            left = getattr(res, "left"); top = getattr(res, "top")
            w = getattr(res, "width"); h = getattr(res, "height")
            return int(left + w / 2), int(top + h / 2)
    except Exception:
        return None
    return None

def locate_image_with_pyautogui(path, confidence=0.8):
    if pyautogui is None:
        return None
    try:
        box = None
        try:
            box = pyautogui.locateOnScreen(path, confidence=confidence)
        except TypeError:
            box = pyautogui.locateOnScreen(path)
        if not box:
            return None
        x, y = pyautogui.center(box)
        return int(x), int(y)
    except Exception:
        return None

def click_with_project(x, y):
    if not click_fn:
        return False
    try:
        click_fn(x, y)
        return True
    except TypeError:
        try:
            click_fn((x, y))
            return True
        except Exception:
            return False
    except Exception:
        return False

def click_with_pyautogui(x, y):
    if pyautogui is None:
        return False
    try:
        pyautogui.click(x, y)
        return True
    except Exception:
        return False

def on_press(key):
    global stop_requested
    try:
        if key == keyboard_mod.Key.esc:
            stop_requested = True
            return False
    except Exception:
        pass

def main(poll_interval=0.5):
    global stop_requested

    if not os.path.isfile(IMAGE_PATH):
        print(f"Image introuvable: {IMAGE_PATH}")
        sys.exit(1)

    if find_image_fn:
        print("Utilisation de 'outils.image_finder' pour la détection.")
    elif pyautogui:
        print("Utilisation de 'pyautogui' pour la détection (fallback).")
    else:
        print("Aucun moyen de détecter l'image. Installez 'pyautogui' ou ajoutez 'outils.image_finder'.")
        sys.exit(1)

    if click_fn:
        print("Utilisation de 'outils.mouse_controller' pour cliquer.")
    elif pyautogui:
        print("Utilisation de 'pyautogui' pour le clic (fallback).")
    else:
        print("Aucun moyen de cliquer. Installez 'pyautogui' ou ajoutez 'outils.mouse_controller'.")
        sys.exit(1)

    listener = None
    if keyboard_mod:
        listener = keyboard_mod.Listener(on_press=on_press)
        listener.start()
        print("Appuyez sur Esc pour arrêter.")
    else:
        print("Le module 'pynput' n'est pas installé; utilisez Ctrl+C pour arrêter.")

    try:
        while not stop_requested:
            coords = None
            if find_image_fn:
                coords = locate_image_with_project(IMAGE_PATH)
            if coords is None:
                coords = locate_image_with_pyautogui(IMAGE_PATH)
            if coords:
                x, y = coords
                clicked = False
                if click_fn:
                    clicked = click_with_project(x, y)
                if not clicked:
                    clicked = click_with_pyautogui(x, y)
                if clicked:
                    print(f"Clic effectué en {x},{y}")
                    time.sleep(0.4)
                else:
                    print("Détecté mais impossible de cliquer.")
                    time.sleep(poll_interval)
            else:
                time.sleep(poll_interval)
    except KeyboardInterrupt:
        pass
    finally:
        stop_requested = True
        if listener:
            listener.stop()
        print("Arrêt demandé, sortie.")

if __name__ == "__main__":
    main()