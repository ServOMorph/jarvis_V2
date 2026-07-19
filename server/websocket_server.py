import asyncio
import json
import sys
from pathlib import Path

try:
    import websockets
except ImportError:
    print("Installation de websockets...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets"])
    import websockets

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from modules.gamepad_controller import GamepadController

CONFIG_PATH = ROOT_DIR / "config" / "mouse_settings.json"
VOICE_CONFIG_PATH = ROOT_DIR / "config" / "voice_config.json"

DEFAULT_CONFIG = {
    "mouse": {
        "sensitivity": 8.0,
        "max_sensitivity": 21.0,
        "acceleration_curve": 2.4,
        "smoothing": 0.3,
        "precision_divider": 7.5,
        "deadzone": 0.15
    },
    "scroll": {
        "sensitivity": 310.0,
        "acceleration_curve": 3.0,
        "deadzone": 0.1
    }
}


class JarvisWebSocketServer:
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.gamepad_enabled = False
        self.gamepad_controller = None
        self.button_states = {}
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_CONFIG.copy()

    def save_config(self, config):
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump(config, f, indent=2)
            self.config = config
            return True
        except Exception as e:
            print(f"Erreur sauvegarde config: {e}")
            return False

    async def broadcast(self, message):
        if self.clients:
            data = json.dumps(message)
            await asyncio.gather(
                *[client.send(data) for client in self.clients],
                return_exceptions=True
            )

    async def send_state(self, websocket):
        buttons = [
            {"id": btn_id, "pressed": pressed}
            for btn_id, pressed in self.button_states.items()
        ]
        await websocket.send(json.dumps({
            "type": "gamepad_state",
            "enabled": self.gamepad_enabled,
            "buttons": buttons
        }))

    async def send_config(self, websocket):
        await websocket.send(json.dumps({
            "type": "config",
            "mouse": self.config.get("mouse", {}),
            "scroll": self.config.get("scroll", {})
        }))

    async def handle_message(self, websocket, message):
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "get_state":
                await self.send_state(websocket)
                await self.send_config(websocket)

            elif msg_type == "get_config":
                await self.send_config(websocket)

            elif msg_type == "toggle_gamepad":
                self.gamepad_enabled = not self.gamepad_enabled
                if self.gamepad_controller:
                    self.gamepad_controller.enabled = self.gamepad_enabled
                await self.broadcast({
                    "type": "gamepad_state",
                    "enabled": self.gamepad_enabled,
                    "buttons": []
                })
                await self.broadcast({
                    "type": "log",
                    "message": f"Manette {'activee' if self.gamepad_enabled else 'desactivee'}",
                    "level": "info"
                })

            elif msg_type == "update_mouse_config":
                new_config = data.get("data", {})
                if self.save_config(new_config):
                    if self.gamepad_controller:
                        self.gamepad_controller.update_mouse_settings(new_config)
                    await self.broadcast({
                        "type": "config",
                        "mouse": new_config.get("mouse", {}),
                        "scroll": new_config.get("scroll", {})
                    })
                    await self.broadcast({
                        "type": "log",
                        "message": "Configuration souris mise a jour",
                        "level": "info"
                    })

            elif msg_type == "reset_config":
                if self.save_config(DEFAULT_CONFIG):
                    if self.gamepad_controller:
                        self.gamepad_controller.update_mouse_settings(DEFAULT_CONFIG)
                    await self.broadcast({
                        "type": "config",
                        "mouse": DEFAULT_CONFIG["mouse"],
                        "scroll": DEFAULT_CONFIG["scroll"]
                    })

        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                "type": "log",
                "message": "Message invalide",
                "level": "error"
            }))

    async def handler(self, websocket):
        self.clients.add(websocket)
        client_addr = websocket.remote_address
        print(f"Client connecte: {client_addr}")

        await self.broadcast({
            "type": "log",
            "message": f"Client connecte: {client_addr[0]}:{client_addr[1]}",
            "level": "info"
        })

        try:
            await self.send_state(websocket)
            await self.send_config(websocket)

            async for message in websocket:
                await self.handle_message(websocket, message)

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
            print(f"Client deconnecte: {client_addr}")

    async def gamepad_loop(self):
        try:
            import pygame
            pygame.init()
            pygame.joystick.init()

            while True:
                pygame.event.pump()

                if pygame.joystick.get_count() > 0:
                    if self.gamepad_controller is None:
                        joystick = pygame.joystick.Joystick(0)
                        joystick.init()
                        await self.broadcast({
                            "type": "log",
                            "message": f"Manette detectee: {joystick.get_name()}",
                            "level": "info"
                        })

                    joystick = pygame.joystick.Joystick(0)
                    for i in range(joystick.get_numbuttons()):
                        pressed = joystick.get_button(i)
                        old_state = self.button_states.get(i, False)

                        if pressed != old_state:
                            self.button_states[i] = pressed
                            event_type = "button_press" if pressed else "button_release"
                            await self.broadcast({
                                "type": event_type,
                                "button": i
                            })

                await asyncio.sleep(0.05)

        except Exception as e:
            print(f"Erreur gamepad loop: {e}")

    async def start(self):
        print(f"Demarrage serveur WebSocket sur ws://{self.host}:{self.port}")

        gamepad_task = asyncio.create_task(self.gamepad_loop())

        async with websockets.serve(self.handler, self.host, self.port):
            print("Serveur pret. Ctrl+C pour arreter.")
            await asyncio.Future()


def main():
    server = JarvisWebSocketServer()
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\nArret du serveur.")


if __name__ == "__main__":
    main()
