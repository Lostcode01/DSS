#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <DNSServer.h>
#include <ESP8266mDNS.h>

// ============ НАСТРОЙКИ Wi-Fi ============
const char* ssid = "Robot_Car";
const char* password = "12345678";

// ============ НАСТРОЙКИ ТОЧКИ ДОСТУПА ============
const byte DNS_PORT = 53;
IPAddress apIP(192, 168, 4, 1);
IPAddress netMsk(255, 255, 255, 0);
DNSServer dnsServer;

// ============ ПИНЫ L298N ============
#define IN1 D1
#define IN2 D2
#define IN3 D3
#define IN4 D4

// ============ СЕРВЕР ============
ESP8266WebServer server(80);

// ============ ПЕРЕМЕННЫЕ ============
String currentCommand = "stop";
unsigned long commandTime = 0;
const unsigned long AUTO_STOP = 5000;

// ============ ДЕМО GPS-КООРДИНАТЫ ============
// Координаты заданы вручную для демонстрационного режима.
// Для настоящего GPS нужно подключить модуль NEO-6M или аналогичный.
const double GPS_LAT = 46.375740;
const double GPS_LON = 48.054459;
const int GPS_RADIUS_METERS = 30; // примерный радиус здания

// ============ ПРОТОТИПЫ ФУНКЦИЙ (объявления) ============
void stopMotors();
void moveForward();
void moveBackward();
void turnLeft();
void turnRight();
void setupPins();
void handleRoot();
void handleCommand();
void handleStatus();
void handleGps();
void handleNotFound();

// ============ HTML СТРАНИЦА ============
const char INDEX_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="theme-color" content="#667eea">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
    <title>🤖 Управление роботом</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html { -webkit-text-size-adjust: 100%; }
        body {
            font-family: Arial, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            min-height: 100dvh;
            display: flex;
            justify-content: center;
            padding: max(14px, env(safe-area-inset-top)) 14px max(18px, env(safe-area-inset-bottom));
            color: white;
            touch-action: manipulation;
        }
        .app {
            width: 100%;
            max-width: 460px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        h1 {
            margin: 6px 0 10px;
            text-align: center;
            font-size: clamp(1.35rem, 5vw, 2rem);
            line-height: 1.2;
        }
        .subtitle {
            width: 100%;
            max-width: 420px;
            text-align: center;
            opacity: 0.9;
            font-size: 0.9rem;
            line-height: 1.35;
            margin-bottom: 12px;
        }
        .status {
            background: rgba(255,255,255,0.2);
            padding: 10px 16px;
            border-radius: 999px;
            margin-bottom: 12px;
            font-size: 0.95rem;
            text-align: center;
            min-width: 180px;
        }
        .current-cmd {
            font-size: clamp(1.7rem, 9vw, 2.7rem);
            margin: 6px 0 8px;
            font-weight: bold;
            text-transform: uppercase;
            text-align: center;
            word-break: break-word;
        }
        .mic-btn {
            width: clamp(92px, 28vw, 125px);
            height: clamp(92px, 28vw, 125px);
            border-radius: 50%;
            border: none;
            background: white;
            color: #667eea;
            font-size: clamp(2.2rem, 10vw, 3.2rem);
            cursor: pointer;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            transition: transform 0.2s, background 0.2s;
            margin: 12px 0;
        }
        .mic-btn:active { transform: scale(0.95); }
        .mic-btn:disabled {
            opacity: 0.55;
            cursor: not-allowed;
        }
        .mic-btn.listening {
            background: #ff4757;
            color: white;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255,71,87,0.7); }
            50% { transform: scale(1.05); box-shadow: 0 0 0 18px rgba(255,71,87,0); }
        }
        .commands {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 10px;
            width: 100%;
            max-width: 420px;
            margin-top: 12px;
        }
        .cmd-btn {
            min-height: 54px;
            padding: 13px 10px;
            border: none;
            border-radius: 14px;
            background: rgba(255,255,255,0.92);
            color: #222;
            font-size: clamp(0.95rem, 4vw, 1.05rem);
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.15s, background 0.15s;
            -webkit-tap-highlight-color: transparent;
        }
        .cmd-btn:active { transform: scale(0.96); background: #fff; }
        .wide { grid-column: span 2; }
        .stop-btn { background: #ff4757; color: white; }
        .location-btn { background: #2ed573; color: white; }
        .location-box, .log, .hint, .compat {
            width: 100%;
            max-width: 420px;
            border-radius: 14px;
        }
        .location-box {
            margin-top: 14px;
            padding: 13px;
            background: rgba(255,255,255,0.18);
            font-size: 0.92rem;
            line-height: 1.5;
            word-break: break-word;
            text-align: center;
        }
        .location-box a { color: #fff; font-weight: bold; }
        .log {
            margin-top: 14px;
            padding: 13px;
            background: rgba(0,0,0,0.3);
            min-height: 105px;
            max-height: 190px;
            font-family: Consolas, 'Courier New', monospace;
            font-size: 0.82rem;
            line-height: 1.35;
            overflow-y: auto;
        }
        .hint, .compat {
            margin-top: 12px;
            text-align: center;
            opacity: 0.88;
            font-size: 0.84rem;
            line-height: 1.45;
        }
        .compat {
            padding: 10px 12px;
            background: rgba(255,255,255,0.12);
        }
        @media (min-width: 700px) {
            body { align-items: center; }
            .app { max-width: 560px; }
            .commands, .location-box, .log, .hint, .compat, .subtitle { max-width: 500px; }
            .commands { grid-template-columns: repeat(3, minmax(0, 1fr)); }
            .wide { grid-column: span 3; }
        }
        @media (max-width: 340px) {
            .cmd-btn { min-height: 48px; padding: 10px 6px; }
            .hint, .compat { font-size: 0.78rem; }
        }
    </style>
</head>
<body>
    <main class="app">
        <h1>🤖 Голосовой робот</h1>
        <div class="subtitle">Подключись к Wi‑Fi <b>Robot_Car</b> и открой <b>http://192.168.4.1</b></div>
        <div class="status" id="status">🔌 Подключено</div>
        <div class="current-cmd" id="currentCmd">СТОП</div>
        <button class="mic-btn" id="micBtn" onclick="toggleMic()" aria-label="Голосовая команда">🎤</button>

        <div class="commands">
            <button class="cmd-btn" onclick="sendCmd('forward')">⬆️ Вперёд</button>
            <button class="cmd-btn" onclick="sendCmd('backward')">⬇️ Назад</button>
            <button class="cmd-btn" onclick="sendCmd('left')">⬅️ Налево</button>
            <button class="cmd-btn" onclick="sendCmd('right')">➡️ Направо</button>
            <button class="cmd-btn stop-btn wide" onclick="sendCmd('stop')">⏹️ СТОП</button>
            <button class="cmd-btn location-btn wide" onclick="showLocation()">🛰️ GPS местонахождение</button>
        </div>

        <div class="location-box" id="locationBox">🛰️ GPS-координаты ещё не запрошены</div>
        <div class="log" id="log">Готов к работе...</div>

        <div class="compat" id="compatBox">Работает на телефоне, планшете и компьютере. GPS-координаты показываются без разрешения браузера.</div>

        <div class="hint">
            🎙️ Голосовые команды:<br>
            <b>"Робот вперёд"</b> — ехать вперёд<br>
            <b>"Робот назад"</b> — ехать назад<br>
            <b>"Робот налево"</b> — поворот налево<br>
            <b>"Робот направо"</b> — поворот направо<br>
            <b>"Робот стоп"</b> — остановка<br>
            <b>"Геолокация"</b> или <b>"Местонахождение"</b> — показать GPS-координаты
        </div>
    </main>

    <script>
        var micBtn = document.getElementById('micBtn');
        var log = document.getElementById('log');
        var currentCmd = document.getElementById('currentCmd');
        var recognition = null;
        var isListening = false;

        function addLog(msg) {
            var time = new Date().toLocaleTimeString('ru-RU', {hour: '2-digit', minute:'2-digit', second:'2-digit'});
            log.innerHTML = time + ' ' + msg + '<br>' + log.innerHTML;
        }

        function speak(text) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                var utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'ru-RU';
                utterance.rate = 1;
                utterance.pitch = 1;
                window.speechSynthesis.speak(utterance);
            }
        }

        function setMicUnavailable(reason) {
            micBtn.disabled = true;
            micBtn.innerHTML = '⌨️';
            micBtn.title = reason;
            addLog('⚠️ ' + reason);
        }

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.lang = 'ru-RU';
            recognition.continuous = false;
            recognition.interimResults = false;

            recognition.onstart = function() {
                isListening = true;
                micBtn.classList.add('listening');
                addLog('🎙️ Слушаю...');
            };

            recognition.onend = function() {
                isListening = false;
                micBtn.classList.remove('listening');
            };

            recognition.onresult = function(event) {
                var transcript = event.results[0][0].transcript.toLowerCase();
                addLog('🗣️ Распознано: "' + transcript + '"');
                processVoiceCommand(transcript);
            };

            recognition.onerror = function(event) {
                addLog('❌ Ошибка микрофона: ' + event.error);
            };
        } else {
            setMicUnavailable('Голосовой ввод не поддерживается этим браузером. Кнопки управления работают.');
        }

        function toggleMic() {
            if (!recognition) return;
            try {
                if (isListening) {
                    recognition.stop();
                } else {
                    recognition.start();
                }
            } catch (e) {
                addLog('❌ Не удалось запустить микрофон: ' + e.message);
            }
        }

        function processVoiceCommand(text) {
            if (text.indexOf('вперёд') !== -1 || text.indexOf('вперед') !== -1) {
                sendCmd('forward');
            } else if (text.indexOf('назад') !== -1) {
                sendCmd('backward');
            } else if (text.indexOf('налево') !== -1 || text.indexOf('лево') !== -1) {
                sendCmd('left');
            } else if (text.indexOf('направо') !== -1 || text.indexOf('право') !== -1) {
                sendCmd('right');
            } else if (text.indexOf('стоп') !== -1 || text.indexOf('стой') !== -1 || text.indexOf('хватит') !== -1) {
                sendCmd('stop');
            } else if (
                text.indexOf('местонахождение') !== -1 ||
                text.indexOf('местоположение') !== -1 ||
                text.indexOf('геолокация') !== -1 ||
                text.indexOf('локация') !== -1 ||
                text.indexOf('где я') !== -1 ||
                text.indexOf('где робот') !== -1
            ) {
                addLog('📍 Голосовая команда: показать геолокацию');
                showLocation();
            } else {
                addLog('❓ Команда не распознана');
            }
        }

        function requestJSON(url, onSuccess, onError) {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', url, true);
            xhr.timeout = 5000;
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        try {
                            onSuccess(JSON.parse(xhr.responseText));
                        } catch (e) {
                            if (onError) onError('Ошибка ответа сервера');
                        }
                    } else {
                        if (onError) onError('HTTP ' + xhr.status);
                    }
                }
            };
            xhr.ontimeout = function() { if (onError) onError('таймаут'); };
            xhr.onerror = function() { if (onError) onError('нет связи'); };
            xhr.send(null);
        }

        function sendCmd(cmd) {
            requestJSON('/cmd?action=' + encodeURIComponent(cmd), function(data) {
                currentCmd.textContent = data.command.toUpperCase();
                addLog('✅ Отправлено: ' + data.command);
                updateStatus(data.command);
                if (data.command === 'stop') {
                    speak('Робот остановлен');
                }
            }, function(err) {
                addLog('❌ Ошибка сети: ' + err);
            });
        }

        function updateStatus(cmd) {
            var icons = {
                'forward': '⬆️ Вперёд',
                'backward': '⬇️ Назад',
                'left': '⬅️ Налево',
                'right': '➡️ Направо',
                'stop': '⏹️ СТОП'
            };
            document.getElementById('status').textContent = icons[cmd] || '❓ Неизвестно';
        }

        function showLocation() {
            var locationBox = document.getElementById('locationBox');
            locationBox.innerHTML = '⏳ Подключаюсь к GPS-модулю...';
            addLog('🛰️ Запрос данных GPS...');

            requestJSON('/gps', function(data) {
                var lat = Number(data.lat).toFixed(6);
                var lon = Number(data.lon).toFixed(6);
                var radius = data.radius || 30;

                // В Яндекс Картах порядок координат в ссылке: долгота, широта.
                var yandexUrl =
                    'https://yandex.ru/maps/?ll=' + lon + '%2C' + lat +
                    '&z=19&pt=' + lon + ',' + lat + ',pm2rdm';

                locationBox.innerHTML =
                    '🛰️ <b>GPS подключён</b><br>' +
                    '📍 <b>Координаты робота:</b><br>' +
                    'Широта: ' + lat + '<br>' +
                    'Долгота: ' + lon + '<br>' +
                    'Радиус зоны: ~' + radius + ' м<br>' +
                    '<a href="' + yandexUrl + '" target="_blank" rel="noopener">Открыть в Яндекс Картах</a>';

                addLog('✅ GPS: ' + lat + ', ' + lon + ', радиус ~' + radius + ' м');
                speak('GPS подключён. Местонахождение робота: широта ' + lat + ', долгота ' + lon + '. Радиус зоны примерно ' + radius + ' метров.');
            }, function(err) {
                locationBox.innerHTML = '❌ Не удалось получить данные GPS: ' + err;
                addLog('❌ Ошибка GPS: ' + err);
                speak('Не удалось получить данные GPS');
            });
        }

        function showGeoNoticeOnLoad() {
            var compatBox = document.getElementById('compatBox');
            if (compatBox) {
                compatBox.innerHTML += '<br>🛰️ Режим GPS: координаты берутся с робота, поэтому разрешение геолокации телефона не требуется.';
            }
        }

        function checkStatus() {
            requestJSON('/status', function(data) {
                document.getElementById('status').style.opacity = '1';
                if (data.command) {
                    currentCmd.textContent = data.command.toUpperCase();
                    updateStatus(data.command);
                }
            }, function() {
                document.getElementById('status').textContent = '🔴 Нет связи';
                document.getElementById('status').style.opacity = '0.55';
            });
        }

        showGeoNoticeOnLoad();
        checkStatus();
        setInterval(checkStatus, 3000);
    </script>
</body>
</html>
)rawliteral";

// ============ ФУНКЦИИ ДВИЖЕНИЯ ============

void stopMotors() {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, LOW);
    Serial.println("🛑 СТОП");
}

void moveForward() {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    Serial.println("⬆️ ВПЕРЁД");
}

void moveBackward() {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
    Serial.println("⬇️ НАЗАД");
}

void turnLeft() {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    Serial.println("⬅️ НАЛЕВО");
}

void turnRight() {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, LOW);
    Serial.println("➡️ НАПРАВО");
}

void setupPins() {
    pinMode(IN1, OUTPUT);
    pinMode(IN2, OUTPUT);
    pinMode(IN3, OUTPUT);
    pinMode(IN4, OUTPUT);
    stopMotors();
}

// ============ ОБРАБОТЧИКИ HTTP ============

void handleRoot() {
    server.sendHeader("Cache-Control", "no-store");
    server.send_P(200, "text/html; charset=utf-8", INDEX_HTML);
}

void handleCommand() {
    String action = server.arg("action");
    
    if (action == "forward") {
        moveForward();
        currentCommand = "forward";
    } else if (action == "backward") {
        moveBackward();
        currentCommand = "backward";
    } else if (action == "left") {
        turnLeft();
        currentCommand = "left";
    } else if (action == "right") {
        turnRight();
        currentCommand = "right";
    } else if (action == "stop") {
        stopMotors();
        currentCommand = "stop";
    } else {
        server.send(400, "application/json", "{\"error\":\"unknown command\"}");
        return;
    }
    
    commandTime = millis();
    
    String output = "{";
    output += "\"command\":\"" + currentCommand + "\",";
    output += "\"status\":\"ok\"";
    output += "}";
    server.send(200, "application/json", output);
}

void handleStatus() {
    String output = "{";
    output += "\"command\":\"" + currentCommand + "\",";
    output += "\"uptime\":" + String(millis() / 1000) + ",";
    output += "\"ip\":\"" + apIP.toString() + "\"";
    output += "}";
    server.send(200, "application/json", output);
}

void handleGps() {
    String output = "{";
    output += "\"status\":\"connected\",";
    output += "\"source\":\"demo_gps\",";
    output += "\"lat\":" + String(GPS_LAT, 6) + ",";
    output += "\"lon\":" + String(GPS_LON, 6) + ",";
    output += "\"radius\":" + String(GPS_RADIUS_METERS);
    output += "}";
    server.send(200, "application/json", output);
}

void handleNotFound() {
    // Для телефонов/ПК: если устройство само проверяет интернет или пользователь вводит любой адрес,
    // показываем страницу управления роботом.
    handleRoot();
}

// ============ SETUP & LOOP ============

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("\n\n🤖 РОБОТ ЗАПУСКАЕТСЯ...");
    
    setupPins();
    
    WiFi.mode(WIFI_AP);
    WiFi.softAPConfig(apIP, apIP, netMsk);
    WiFi.softAP(ssid, password);

    dnsServer.setErrorReplyCode(DNSReplyCode::NoError);
    dnsServer.start(DNS_PORT, "*", apIP);
    
    IPAddress myIP = WiFi.softAPIP();
    Serial.print("📡 Wi-Fi сеть: ");
    Serial.println(ssid);
    Serial.print("🔑 Пароль: ");
    Serial.println(password);
    Serial.print("🌐 IP адрес робота: ");
    Serial.println(myIP);
    Serial.println("🌐 Открой: http://192.168.4.1");
    Serial.println("🌐 Также можно попробовать: http://robot.local");
    Serial.print("🛰️ Демо GPS: ");
    Serial.print(GPS_LAT, 6);
    Serial.print(", ");
    Serial.print(GPS_LON, 6);
    Serial.print(" радиус ~");
    Serial.print(GPS_RADIUS_METERS);
    Serial.println(" м");

    if (MDNS.begin("robot")) {
        MDNS.addService("http", "tcp", 80);
        Serial.println("✅ mDNS запущен: http://robot.local");
    } else {
        Serial.println("⚠️ mDNS не запущен, используй http://192.168.4.1");
    }
    
    server.on("/", handleRoot);
    server.on("/cmd", handleCommand);
    server.on("/status", handleStatus);
    server.on("/gps", handleGps);

    // Частые адреса проверки captive portal на разных устройствах.
    server.on("/generate_204", handleRoot);          // Android
    server.on("/gen_204", handleRoot);               // Android/Chrome
    server.on("/hotspot-detect.html", handleRoot);    // iOS/macOS
    server.on("/library/test/success.html", handleRoot);
    server.on("/ncsi.txt", handleRoot);               // Windows
    server.on("/connecttest.txt", handleRoot);        // Windows
    server.on("/redirect", handleRoot);
    server.onNotFound(handleNotFound);
    
    server.begin();
    Serial.println("✅ HTTP сервер запущен");
    Serial.println("📱 Подключись к Wi-Fi Robot_Car и открой браузер");
}

void loop() {
    dnsServer.processNextRequest();
    server.handleClient();
    MDNS.update();
    
    if (currentCommand != "stop" && millis() - commandTime > AUTO_STOP) {
        stopMotors();
        currentCommand = "stop";
        Serial.println("⏰ Автостоп по таймауту");
    }
    
    delay(1);
}