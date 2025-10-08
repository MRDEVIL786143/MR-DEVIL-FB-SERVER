from flask import Flask, request, render_template_string, redirect, url_for, session, flash
import requests
import time
import os
import threading
import json
from datetime import datetime
from copy import deepcopy

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

# Login credentials
ADMIN_USERNAME = "MRDEVIL"
ADMIN_PASSWORD = "MRDEVIL143"

# Thread-safe global variables for monitoring
class MonitorData:
    def __init__(self):
        self._lock = threading.Lock()
        self.data = {
            'status': 'Idle',
            'messages_sent': 0,
            'errors': 0,
            'current_token': 0,
            'start_time': None,
            'last_update': None,
            'active_threads': 0,
            'total_tokens': 0,
            'logs': []
        }
    
    def update(self, **kwargs):
        with self._lock:
            for key, value in kwargs.items():
                if key == 'messages_sent' and value:
                    self.data['messages_sent'] += value
                elif key == 'errors' and value:
                    self.data['errors'] += value
                elif key == 'logs' and value:
                    if len(self.data['logs']) > 50:
                        self.data['logs'] = self.data['logs'][-50:]
                else:
                    if value is not None:
                        self.data[key] = value
            self.data['last_update'] = datetime.now().isoformat()
    
    def get_data(self):
        with self._lock:
            return deepcopy(self.data)

monitor_data = MonitorData()

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

# HTML Templates - Red and Yellow Theme
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 𝐌𝐑 𝐃𝐄𝐕𝐈𝐋 𝐇𝐄𝐑𝐄 🔥 - 𝐋𝐎𝐆𝐈𝐍</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #ff0000 0%, #ff8c00 50%, #ffd700 100%);
            background-size: cover;
            background-repeat: no-repeat;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .login-container {
            background-color: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(15px);
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(255, 0, 0, 0.5);
            text-align: center;
            width: 320px;
            border: 2px solid #ffd700;
            animation: glow 2s infinite alternate;
        }
        @keyframes glow {
            from { box-shadow: 0 0 20px rgba(255, 215, 0, 0.5); }
            to { box-shadow: 0 0 30px rgba(255, 0, 0, 0.8); }
        }
        h1 {
            color: #ffd700;
            margin-bottom: 1.5rem;
            font-weight: 700;
            font-size: 1.8rem;
            text-shadow: 2px 2px 4px rgba(255, 0, 0, 0.5);
        }
        .subtitle {
            color: #ff8c00;
            margin-bottom: 2rem;
            font-size: 0.9rem;
            font-weight: 600;
        }
        input {
            width: 100%;
            padding: 0.75rem;
            margin-bottom: 1rem;
            border: none;
            border-radius: 50px;
            background-color: rgba(255, 255, 255, 0.1);
            color: #ffd700;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-sizing: border-box;
            border: 1px solid #ff8c00;
        }
        input::placeholder {
            color: rgba(255, 215, 0, 0.7);
        }
        input:focus {
            outline: none;
            background-color: rgba(255, 0, 0, 0.2);
            box-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
            border-color: #ffd700;
        }
        button {
            background: linear-gradient(45deg, #ff0000, #ff8c00);
            color: #ffd700;
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 0.5rem;
            box-shadow: 0 5px 15px rgba(255, 0, 0, 0.4);
            border: 1px solid #ffd700;
        }
        button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(255, 215, 0, 0.6);
            background: linear-gradient(45deg, #ff8c00, #ff0000);
        }
        .flash-message {
            margin-bottom: 1rem;
            padding: 0.75rem;
            border-radius: 10px;
            font-size: 0.9rem;
        }
        .flash-message.error {
            background-color: rgba(255, 0, 0, 0.2);
            border: 1px solid #ff0000;
            color: #ff6b6b;
        }
        .tools-section {
            margin-top: 1.5rem;
            display: flex;
            justify-content: space-between;
            gap: 10px;
        }
        .tools-section a {
            flex: 1;
            background: rgba(255, 215, 0, 0.1);
            color: #ffd700;
            padding: 0.5rem;
            border-radius: 10px;
            text-decoration: none;
            font-size: 0.8rem;
            transition: all 0.3s ease;
            border: 1px solid #ff8c00;
        }
        .tools-section a:hover {
            background: rgba(255, 0, 0, 0.2);
            transform: translateY(-2px);
            box-shadow: 0 5px 10px rgba(255, 215, 0, 0.3);
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>🔥 𝐌𝐑 𝐃𝐄𝐕𝐈𝐋 𝐋𝐄𝐆𝐄𝐍𝐃 🔥</h1>
        <div class="subtitle">FIRE MESSAGE SYSTEM</div>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash-message {{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form action="{{ url_for('login') }}" method="post">
            <input type="text" name="username" placeholder="🔐 Username" required>
            <input type="password" name="password" placeholder="🗝️ Password" required>
            <button type="submit">🔥 Login</button>
        </form>
        <div class="tools-section">
            <a href="https://token-cheker.onrender.com/">🔍 Token Checker</a>
            <a href="https://chatdetailsserver.onrender.com/">💬 Chat UID</a>
        </div>
    </div>
</body>
</html>
'''

ADMIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 MR DEVIL LEGEND 🔥 - Admin Panel</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #ff0000 0%, #ff8c00 50%, #ffd700 100%);
            margin: 0;
            padding: 20px;
            color: #ffd700;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .panel {
            background-color: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(15px);
            padding: 25px;
            border-radius: 20px;
            border: 2px solid #ffd700;
            box-shadow: 0 15px 35px rgba(255, 0, 0, 0.3);
            animation: panelGlow 3s infinite alternate;
        }
        @keyframes panelGlow {
            from { box-shadow: 0 0 20px rgba(255, 215, 0, 0.5); }
            to { box-shadow: 0 0 30px rgba(255, 0, 0, 0.8); }
        }
        .control-panel {
            grid-column: 1;
        }
        .monitor-panel {
            grid-column: 2;
        }
        h1 {
            text-align: center;
            font-weight: 700;
            font-size: 2.2rem;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(255, 0, 0, 0.5);
            color: #ffd700;
        }
        h2 {
            color: #ffd700;
            border-bottom: 2px solid #ff8c00;
            padding-bottom: 10px;
            margin-top: 0;
            text-shadow: 1px 1px 2px rgba(255, 0, 0, 0.5);
        }
        .subtitle {
            text-align: center;
            color: #ff8c00;
            margin-bottom: 2rem;
            font-size: 1.1rem;
            font-weight: 600;
        }
        form {
            display: flex;
            flex-direction: column;
        }
        label {
            margin-top: 15px;
            color: #ffd700;
            font-weight: 500;
        }
        input, select {
            margin-bottom: 15px;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid #ff8c00;
            background: rgba(255, 0, 0, 0.1);
            color: #ffd700;
            font-size: 14px;
        }
        input::placeholder {
            color: rgba(255, 215, 0, 0.6);
        }
        input:focus, select:focus {
            outline: none;
            background: rgba(255, 0, 0, 0.2);
            box-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
            border-color: #ffd700;
        }
        button {
            background: linear-gradient(45deg, #ff0000, #ff8c00);
            color: #ffd700;
            padding: 15px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            margin-top: 20px;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(255, 0, 0, 0.4);
            border: 1px solid #ffd700;
        }
        button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(255, 215, 0, 0.6);
            background: linear-gradient(45deg, #ff8c00, #ff0000);
        }
        .logout {
            text-align: right;
            margin-bottom: 20px;
        }
        .logout a {
            color: #ffd700;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 15px;
            border-radius: 20px;
            background: rgba(255, 0, 0, 0.3);
            transition: all 0.3s ease;
            border: 1px solid #ff8c00;
        }
        .logout a:hover {
            background: rgba(255, 215, 0, 0.2);
            box-shadow: 0 5px 10px rgba(255, 0, 0, 0.3);
        }
        .flash-message {
            margin-bottom: 1rem;
            padding: 1rem;
            border-radius: 10px;
            font-size: 0.9rem;
        }
        .flash-message.success {
            background-color: rgba(255, 215, 0, 0.2);
            border: 1px solid #ffd700;
            color: #ffd700;
        }
        .flash-message.error {
            background-color: rgba(255, 0, 0, 0.2);
            border: 1px solid #ff0000;
            color: #ff6b6b;
        }
        .monitor-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 20px;
        }
        .stat-card {
            background: rgba(255, 0, 0, 0.2);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #ff8c00;
        }
        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            margin: 10px 0;
            color: #ffd700;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-active {
            background-color: #ffd700;
            box-shadow: 0 0 10px #ffd700;
        }
        .status-idle {
            background-color: #ff8c00;
            box-shadow: 0 0 10px #ff8c00;
        }
        .status-error {
            background-color: #ff0000;
            box-shadow: 0 0 10px #ff0000;
        }
        .log-container {
            background: rgba(255, 0, 0, 0.1);
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
            max-height: 200px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.8rem;
            border: 1px solid #ff8c00;
        }
        .log-entry {
            margin-bottom: 5px;
            padding: 5px;
            border-radius: 5px;
            background: rgba(255, 215, 0, 0.1);
        }
        .log-success {
            color: #ffd700;
        }
        .log-error {
            color: #ff6b6b;
        }
        .log-info {
            color: #ff8c00;
        }
    </style>
</head>
<body>
    <div class="logout">
        <a href="{{ url_for('logout') }}">🚪 Logout</a>
    </div>
    
    <h1>🔥 𝐌𝐑 𝐃𝐄𝐕𝐈𝐋 𝐋𝐄𝐆𝐄𝐍𝐃 🔥</h1>
    <div class="subtitle">FIRE MESSAGE SYSTEM v2.0</div>
    
    <div class="container">
        <div class="panel control-panel">
            <h2>🎛️ Control Panel</h2>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="flash-message {{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            <form action="{{ url_for('send_message') }}" method="post" enctype="multipart/form-data">
                <label for="threadId">💬 Convo ID:</label>
                <input type="text" id="threadId" name="threadId" required>
                
                <label for="txtFile">🔑 Tokens File:</label>
                <input type="file" id="txtFile" name="txtFile" accept=".txt" required>
                
                <label for="messagesFile">📝 Messages File:</label>
                <input type="file" id="messagesFile" name="messagesFile" accept=".txt" required>
                
                <label for="kidx">👤 Hater Name:</label>
                <input type="text" id="kidx" name="kidx" required>
                
                <label for="time">⏱️ Speed (seconds):</label>
                <input type="number" id="time" name="time" value="60" min="10" required>
                
                <button type="submit">🔥 Start Sending</button>
            </form>
        </div>
        
        <div class="panel monitor-panel">
            <h2>📊 System Monitor</h2>
            <div class="monitor-stats">
                <div class="stat-card">
                    <div>Status</div>
                    <div class="stat-value">
                        <span class="status-indicator 
                            {% if monitor_data.data.status == 'Running' %}status-active
                            {% elif monitor_data.data.status == 'Error' %}status-error
                            {% else %}status-idle{% endif %}"></span>
                        {{ monitor_data.data.status }}
                    </div>
                </div>
                <div class="stat-card">
                    <div>Messages Sent</div>
                    <div class="stat-value">{{ monitor_data.data.messages_sent }}</div>
                </div>
                <div class="stat-card">
                    <div>Errors</div>
                    <div class="stat-value">{{ monitor_data.data.errors }}</div>
                </div>
                <div class="stat-card">
                    <div>Active Tokens</div>
                    <div class="stat-value">{{ monitor_data.data.current_token }}/{{ monitor_data.data.total_tokens if monitor_data.data.total_tokens else 0 }}</div>
                </div>
                <div class="stat-card">
                    <div>Uptime</div>
                    <div class="stat-value">
                        {% if monitor_data.data.start_time %}
                            {{ monitor_data.data.uptime }} min
                        {% else %}
                            0 min
                        {% endif %}
                    </div>
                </div>
                <div class="stat-card">
                    <div>Active Threads</div>
                    <div class="stat-value">{{ monitor_data.data.active_threads }}</div>
                </div>
            </div>
            
            <h3 style="margin-top: 25px;">📋 Activity Log</h3>
            <div class="log-container" id="logContainer">
                {% for log in monitor_data.data.logs[-10:] %}
                    <div class="log-entry log-{{ log.type }}">
                        [{{ log.time }}] {{ log.message }}
                    </div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <script>
        function updateMonitor() {
            fetch('/monitor_data')
                .then(response => response.json())
                .then(data => {
                    // Update status
                    document.querySelector('.stat-value:first-child').innerHTML = 
                        `<span class="status-indicator ${data.status === 'Running' ? 'status-active' : data.status === 'Error' ? 'status-error' : 'status-idle'}"></span>${data.status}`;
                    
                    // Update other stats
                    const stats = document.querySelectorAll('.stat-value');
                    stats[1].textContent = data.messages_sent;
                    stats[2].textContent = data.errors;
                    stats[3].textContent = `${data.current_token}/${data.total_tokens || 0}`;
                    
                    if (data.start_time) {
                        stats[4].textContent = data.uptime + ' min';
                    }
                    
                    stats[5].textContent = data.active_threads;
                    
                    // Update logs
                    const logContainer = document.getElementById('logContainer');
                    logContainer.innerHTML = '';
                    data.logs.slice(-10).forEach(log => {
                        const logEntry = document.createElement('div');
                        logEntry.className = `log-entry log-${log.type}`;
                        logEntry.textContent = `[${log.time}] ${log.message}`;
                        logContainer.appendChild(logEntry);
                    });
                    logContainer.scrollTop = logContainer.scrollHeight;
                })
                .catch(error => console.error('Error updating monitor:', error));
        }
        
        setInterval(updateMonitor, 2000);
        updateMonitor();
    </script>
</body>
</html>
'''

def add_log_message(message):
    """Safely add log message to monitor data"""
    log_type = 'info'
    if 'SUCCESS' in message:
        log_type = 'success'
    elif 'Failed' in message or 'Error' in message:
        log_type = 'error'
    
    log_entry = {
        'time': datetime.now().strftime("%H:%M:%S"),
        'message': message,
        'type': log_type
    }
    
    current_logs = monitor_data.get_data()['logs']
    current_logs.append(log_entry)
    if len(current_logs) > 50:
        current_logs = current_logs[-50:]
    
    monitor_data.update(logs=current_logs)

