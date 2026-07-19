class JarvisWebUI {
    constructor() {
        this.ws = null;
        this.gamepadEnabled = false;
        this.config = {
            mouse: {
                sensitivity: 8.0,
                max_sensitivity: 21.0,
                acceleration_curve: 2.4,
                smoothing: 0.3,
                precision_divider: 7.5,
                deadzone: 0.15
            },
            scroll: {
                sensitivity: 310.0,
                acceleration_curve: 3.0,
                deadzone: 0.1
            }
        };
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.init();
    }

    init() {
        this.bindElements();
        this.bindEvents();
        this.connectWebSocket();
        this.log('Interface initialisee', 'info');
    }

    bindElements() {
        this.statusLed = document.getElementById('statusLed');
        this.statusText = document.getElementById('statusText');
        this.wsLed = document.getElementById('wsLed');
        this.wsStatus = document.getElementById('wsStatus');
        this.toggleBtn = document.getElementById('toggleGamepad');
        this.toggleIcon = document.getElementById('toggleIcon');
        this.toggleText = document.getElementById('toggleText');
        this.openConfigBtn = document.getElementById('openConfig');
        this.configModal = document.getElementById('configModal');
        this.closeModalBtn = document.getElementById('closeModal');
        this.resetConfigBtn = document.getElementById('resetConfig');
        this.applyConfigBtn = document.getElementById('applyConfig');
        this.consoleEl = document.getElementById('console');

        this.sliders = {
            sensitivity: document.getElementById('sensitivity'),
            maxSensitivity: document.getElementById('maxSensitivity'),
            acceleration: document.getElementById('acceleration'),
            smoothing: document.getElementById('smoothing'),
            precisionDivider: document.getElementById('precisionDivider'),
            deadzone: document.getElementById('deadzone'),
            scrollSensitivity: document.getElementById('scrollSensitivity'),
            scrollAcceleration: document.getElementById('scrollAcceleration'),
            scrollDeadzone: document.getElementById('scrollDeadzone')
        };

        this.sliderValues = {
            sensitivity: document.getElementById('sensitivityValue'),
            maxSensitivity: document.getElementById('maxSensitivityValue'),
            acceleration: document.getElementById('accelerationValue'),
            smoothing: document.getElementById('smoothingValue'),
            precisionDivider: document.getElementById('precisionDividerValue'),
            deadzone: document.getElementById('deadzoneValue'),
            scrollSensitivity: document.getElementById('scrollSensitivityValue'),
            scrollAcceleration: document.getElementById('scrollAccelerationValue'),
            scrollDeadzone: document.getElementById('scrollDeadzoneValue')
        };
    }

    bindEvents() {
        this.toggleBtn.addEventListener('click', () => this.toggleGamepad());
        this.openConfigBtn.addEventListener('click', () => this.openConfig());
        this.closeModalBtn.addEventListener('click', () => this.closeConfig());
        this.resetConfigBtn.addEventListener('click', () => this.resetConfig());
        this.applyConfigBtn.addEventListener('click', () => this.applyConfig());

        this.configModal.addEventListener('click', (e) => {
            if (e.target === this.configModal) {
                this.closeConfig();
            }
        });

        Object.keys(this.sliders).forEach(key => {
            this.sliders[key].addEventListener('input', (e) => {
                this.sliderValues[key].textContent = parseFloat(e.target.value).toFixed(2);
            });
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.configModal.classList.contains('active')) {
                this.closeConfig();
            }
        });
    }

    connectWebSocket() {
        const wsUrl = 'ws://localhost:8765';
        this.log(`Connexion a ${wsUrl}...`, 'info');

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                this.reconnectAttempts = 0;
                this.updateWsStatus(true);
                this.log('WebSocket connecte', 'info');
                this.ws.send(JSON.stringify({ type: 'get_state' }));
            };

            this.ws.onclose = () => {
                this.updateWsStatus(false);
                this.log('WebSocket deconnecte', 'warning');
                this.attemptReconnect();
            };

            this.ws.onerror = (error) => {
                this.log('Erreur WebSocket', 'error');
            };

            this.ws.onmessage = (event) => {
                this.handleMessage(JSON.parse(event.data));
            };
        } catch (error) {
            this.log(`Erreur connexion: ${error.message}`, 'error');
            this.attemptReconnect();
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000);
            this.log(`Reconnexion dans ${delay/1000}s (tentative ${this.reconnectAttempts})`, 'warning');
            setTimeout(() => this.connectWebSocket(), delay);
        } else {
            this.log('Echec reconnexion - verifier le serveur', 'error');
        }
    }

    handleMessage(data) {
        switch (data.type) {
            case 'gamepad_state':
                this.updateGamepadState(data.enabled, data.buttons || []);
                break;
            case 'config':
                this.updateConfig(data.mouse, data.scroll);
                break;
            case 'log':
                this.log(data.message, data.level || 'info');
                break;
            case 'button_press':
                this.highlightButton(data.button, true);
                break;
            case 'button_release':
                this.highlightButton(data.button, false);
                break;
        }
    }

    updateWsStatus(connected) {
        if (connected) {
            this.wsLed.classList.add('active');
            this.wsStatus.textContent = 'WebSocket connecte';
        } else {
            this.wsLed.classList.remove('active');
            this.wsStatus.textContent = 'WebSocket deconnecte';
        }
    }

    updateGamepadState(enabled, buttons) {
        this.gamepadEnabled = enabled;

        if (enabled) {
            this.statusLed.classList.add('active');
            this.statusText.classList.add('active');
            this.statusText.textContent = 'MANETTE ACTIVE';
            this.toggleBtn.classList.add('active');
            this.toggleIcon.innerHTML = '&#10004;';
            this.toggleText.textContent = 'Manette ACTIVEE';
        } else {
            this.statusLed.classList.remove('active');
            this.statusText.classList.remove('active');
            this.statusText.textContent = 'MANETTE INACTIVE';
            this.toggleBtn.classList.remove('active');
            this.toggleIcon.innerHTML = '&#10060;';
            this.toggleText.textContent = 'Manette DESACTIVEE';
        }

        buttons.forEach(btn => {
            this.highlightButton(btn.id, btn.pressed);
        });
    }

    highlightButton(buttonId, pressed) {
        const buttonEl = document.querySelector(`[data-button="${buttonId}"]`);
        if (buttonEl) {
            if (pressed) {
                buttonEl.classList.add('active');
            } else {
                buttonEl.classList.remove('active');
            }
        }
    }

    updateConfig(mouse, scroll) {
        if (mouse) {
            this.config.mouse = mouse;
            this.sliders.sensitivity.value = mouse.sensitivity;
            this.sliderValues.sensitivity.textContent = mouse.sensitivity.toFixed(2);
            this.sliders.maxSensitivity.value = mouse.max_sensitivity;
            this.sliderValues.maxSensitivity.textContent = mouse.max_sensitivity.toFixed(2);
            this.sliders.acceleration.value = mouse.acceleration_curve;
            this.sliderValues.acceleration.textContent = mouse.acceleration_curve.toFixed(2);
            this.sliders.smoothing.value = mouse.smoothing;
            this.sliderValues.smoothing.textContent = mouse.smoothing.toFixed(2);
            this.sliders.precisionDivider.value = mouse.precision_divider;
            this.sliderValues.precisionDivider.textContent = mouse.precision_divider.toFixed(2);
            this.sliders.deadzone.value = mouse.deadzone;
            this.sliderValues.deadzone.textContent = mouse.deadzone.toFixed(2);
        }
        if (scroll) {
            this.config.scroll = scroll;
            this.sliders.scrollSensitivity.value = scroll.sensitivity;
            this.sliderValues.scrollSensitivity.textContent = scroll.sensitivity.toFixed(2);
            this.sliders.scrollAcceleration.value = scroll.acceleration_curve;
            this.sliderValues.scrollAcceleration.textContent = scroll.acceleration_curve.toFixed(2);
            this.sliders.scrollDeadzone.value = scroll.deadzone;
            this.sliderValues.scrollDeadzone.textContent = scroll.deadzone.toFixed(2);
        }
    }

    toggleGamepad() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type: 'toggle_gamepad' }));
        } else {
            this.log('WebSocket non connecte', 'error');
        }
    }

    openConfig() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type: 'get_config' }));
        }
        this.configModal.classList.add('active');
    }

    closeConfig() {
        this.configModal.classList.remove('active');
    }

    resetConfig() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type: 'reset_config' }));
            this.log('Configuration reinitilisee', 'info');
        }
    }

    applyConfig() {
        const newConfig = {
            mouse: {
                sensitivity: parseFloat(this.sliders.sensitivity.value),
                max_sensitivity: parseFloat(this.sliders.maxSensitivity.value),
                acceleration_curve: parseFloat(this.sliders.acceleration.value),
                smoothing: parseFloat(this.sliders.smoothing.value),
                precision_divider: parseFloat(this.sliders.precisionDivider.value),
                deadzone: parseFloat(this.sliders.deadzone.value)
            },
            scroll: {
                sensitivity: parseFloat(this.sliders.scrollSensitivity.value),
                acceleration_curve: parseFloat(this.sliders.scrollAcceleration.value),
                deadzone: parseFloat(this.sliders.scrollDeadzone.value)
            }
        };

        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'update_mouse_config',
                data: newConfig
            }));
            this.log('Configuration appliquee', 'info');
            this.closeConfig();
        } else {
            this.log('WebSocket non connecte', 'error');
        }
    }

    log(message, level = 'info') {
        const timestamp = new Date().toLocaleTimeString('fr-FR');
        const line = document.createElement('div');
        line.className = `console-line ${level}`;
        line.textContent = `[${timestamp}] ${message}`;
        this.consoleEl.appendChild(line);
        this.consoleEl.scrollTop = this.consoleEl.scrollHeight;

        while (this.consoleEl.children.length > 100) {
            this.consoleEl.removeChild(this.consoleEl.firstChild);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.jarvisUI = new JarvisWebUI();
});
