from flask import Flask, request, render_template_string, jsonify
import requests
import threading
import time
import os
import queue

app = Flask(__name__)

# Global state variables
stop_flag = False
task_thread = None
message_queue = queue.Queue() # Queue for passing logs from thread to Flask
# Using v19.0 as v20.0 might not be available widely yet, but the user's original code used v20.0, so I'll keep it.
FB_API_URL = "https://graph.facebook.com/v20.0/me/messages" 

# ---------------- Stylish HTML (Digital Warrior Theme - Dark Green/Orange) ---------------- #
html_page = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>⚔️ 𝐌𝐑 𝐃𝐄𝐕𝐈𝐋 𝐇𝐄𝐑𝐄 ⚔️</title>
  <style>
    /* Google Fonts for a tech/digital look */
    @import url('https://fonts.googleapis.com/css2?family=Major+Mono+Display&family=Space+Mono:wght@400;700&display=swap');
    
    /* Variables for easy theme changes */
    :root {
      --bg-dark: #0e1215;
      --bg-light: #1a2024;
      --color-neon-green: #00ff41;
      --color-digital-orange: #ff8c00;
      --color-text-dim: #999;
      --color-box-bg: rgba(30, 41, 59, 0.4);
    }

    body {
      font-family: 'Space Mono', monospace;
      background: linear-gradient(135deg, var(--bg-dark) 0%, var(--bg-light) 100%);
      color: var(--color-neon-green);
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
      padding: 15px;
    }
    .main-container {
        width: 100%;
        max-width: 900px;
        display: flex;
        flex-direction: column;
        gap: 25px;
        align-items: center;
    }
    .box {
      background: var(--color-box-bg);
      backdrop-filter: blur(8px);
      border-radius: 12px;
      padding: 30px 20px;
      width: 100%;
      box-shadow: 0 0 20px rgba(0, 255, 65, 0.2);
      border: 2px solid var(--color-neon-green);
      text-align: center;
      transition: all 0.3s;
    }
    .box:hover {
        box-shadow: 0 0 30px var(--color-digital-orange);
        border-color: var(--color-digital-orange);
    }

    h2 {
      margin-bottom: 25px;
      color: var(--color-digital-orange);
      text-shadow: 0 0 12px var(--color-digital-orange);
      font-family: 'Major Mono Display', monospace;
      font-size: clamp(1.5rem, 4vw, 2.2rem);
    }
    
    input, select, .file-input-label {
      width: 90%;
      padding: 14px;
      margin: 10px 0;
      border-radius: 8px;
      border: 1px solid #333;
      outline: none;
      font-size: 14px;
      background: #151515;
      color: var(--color-neon-green);
      transition: border-color 0.3s, box-shadow 0.3s;
    }
    input::placeholder { color: var(--color-text-dim); }
    input:focus, select:focus {
      border-color: var(--color-digital-orange);
      box-shadow: 0 0 10px var(--color-digital-orange);
    }
    
    /* Custom file input style */
    input[type="file"] {
      display: none;
    }
    .file-input-label {
      display: block; /* Changed to block for full width */
      cursor: pointer;
      text-align: center;
      border: 2px dashed var(--color-neon-green);
      padding: 15px 12px;
      font-size: 15px;
      margin-top: 15px;
      width: 90%;
      margin-left: auto;
      margin-right: auto;
    }
    .file-input-label:hover {
        border-style: solid;
        background: rgba(0, 255, 65, 0.1);
    }

    button {
      padding: 12px 25px;
      margin: 20px 8px 5px;
      border: none;
      border-radius: 6px;
      font-weight: 700;
      cursor: pointer;
      transition: 0.3s all ease-in-out;
      text-transform: uppercase;
      font-family: 'Space Mono', monospace;
      width: 48%; /* Adjusted for better layout */
      max-width: 200px;
    }
    .start {
      background: var(--color-neon-green);
      color: var(--bg-dark);
      box-shadow: 0 0 15px var(--color-neon-green);
    }
    .start:hover {
      background: #00cc33;
      transform: translateY(-2px);
    }
    .stop {
      background: var(--color-digital-orange);
      color: var(--bg-dark);
      box-shadow: 0 0 15px var(--color-digital-orange);
    }
    .stop:hover {
      background: #e67e00;
      transform: translateY(-2px);
    }

    #status {
      margin-top: 25px;
      font-size: 18px;
      color: var(--color-digital-orange);
      font-weight: 700;
    }
    .hidden { display: none; }
    label.form-label { 
        font-size: 14px; 
        color: var(--color-neon-green); 
        margin-top: 10px; 
        display: block; 
        text-align: left; 
        width: 90%; 
        margin-left: auto; 
        margin-right: auto;
    }
    p.file-name-display { 
        font-size:12px; 
        color:var(--color-text-dim); 
        margin-top:5px; 
        text-align:center;
    }

    /* PROOF SYSTEM LOG AREA */
    .log-box {
        background: #0a0a0a;
        border: 2px solid var(--color-digital-orange);
        border-radius: 8px;
        height: 300px; /* Increased height for better mobile view */
        overflow-y: scroll;
        padding: 15px;
        text-align: left;
        color: #ddd;
        font-size: 13px;
        margin-top: 20px;
        font-family: 'Space Mono', monospace;
        line-height: 1.4;
    }
    .log-box::-webkit-scrollbar { width: 5px; } 
    .log-box::-webkit-scrollbar-track { background: #151515; }
    .log-box::-webkit-scrollbar-thumb { background: var(--color-digital-orange); border-radius: 5px; }

    .log-entry.success { color: var(--color-neon-green); }
    .log-entry.fail { color: #ff0041; } /* Bright Red for errors */
  </style>
</head>
<body>
  <div class="main-container">
    <div class="box form-box">
        <h2>⚔️ 𝐌𝐑 𝐃𝐄𝐕𝐈𝐋 𝐇𝐄𝐑𝐄 ⚔️</h2>
        <form id="sendForm" enctype="multipart/form-data">
            <label for="mode" class="form-label">Select Token Mode:</label>
            <select name="mode" id="mode" onchange="toggleMode()" required>
                <option value="single">🔑 Single Token</option>
                <option value="multi">🔑 Multi Token (File)</option>
            </select>

            <div id="singleBox">
                <input type="text" name="single_token" placeholder="Enter Single Access Token">
            </div>
            <div id="multiBox" class="hidden">
                <label for="multi_file" class="file-input-label">🔑 Choose Token File (.txt)</label>
                <input type="file" name="multi_file" id="multi_file" accept=".txt" onchange="updateFileName('multi_file', 'multi-file-name')">
                <p id="multi-file-name" class="file-name-display">No file selected.</p>
            </div>

            <input type="text" name="recipient_id" placeholder="Target Group/User ID (UID)" required><br>
            <input type="text" name="hettar" placeholder="Sender Name (Optional)"><br>
            <input type="number" name="delay" placeholder="Delay (seconds)" required min="1" value="5"><br>
            
            <label for="message_file" class="file-input-label">📝 Choose Message File (.txt)</label>
            <input type="file" name="file" id="message_file" accept=".txt" required onchange="updateFileName('message_file', 'message-file-name')">
            <p id="message-file-name" class="file-name-display">No file selected.</p>

            <div style="display:flex; justify-content: space-around; width:100%; max-width: 450px; margin: 0 auto;">
                <button type="button" class="start" onclick="startTask()">🚀 START</button>
                <button type="button" class="stop" onclick="stopTask()">🛑 STOP</button>
            </div>
        </form>
        <p id="status">Status: 💤 Idle</p>
    </div>
    
    <!-- Proof System / Live Log -->
    <div class="box log-container">
        <h2>PROOF LOG SYSTEM</h2>
        <div id="logArea" class="log-box">
            <!-- Log messages will appear here -->
            <p class="log-entry success">[$00:00:00] System Ready.</p>
        </div>
    </div>
  </div>

<script>
let logInterval;

function updateFileName(inputId, nameId) {
    const input = document.getElementById(inputId);
    const nameDisplay = document.getElementById(nameId);
    if (input.files.length > 0) {
        nameDisplay.innerText = "Selected File: " + input.files[0].name;
        nameDisplay.style.color = 'var(--color-neon-green)';
    } else {
        nameDisplay.innerText = "No file selected.";
        nameDisplay.style.color = 'var(--color-text-dim)';
    }
}

function toggleMode() {
  let mode = document.getElementById("mode").value;
  document.getElementById("singleBox").classList.toggle("hidden", mode !== "single");
  document.getElementById("multiBox").classList.toggle("hidden", mode !== "multi");
}

function fetchLogs() {
    fetch('/logs')
        .then(r => r.json())
        .then(data => {
            const logArea = document.getElementById('logArea');
            if (data.logs && data.logs.length > 0) {
                data.logs.forEach(log => {
                    const p = document.createElement('p');
                    p.classList.add('log-entry');
                    p.classList.add(log.status); // 'success' or 'fail'
                    p.innerText = log.message;
                    logArea.appendChild(p);
                });
                // Auto scroll to the bottom
                logArea.scrollTop = logArea.scrollHeight;
            }
        })
        .catch(error => {
            console.error('Error fetching logs:', error);
            // Optionally, log this error in the UI
            // document.getElementById('logArea').innerHTML += '<p class="log-entry fail">ERROR: Failed to fetch logs.</p>';
        });
}

function startTask() {
  let form = document.getElementById("sendForm");
  let formData = new FormData(form);
  document.getElementById("status").innerText = "Status: ⏱️ Starting...";
  document.getElementById('logArea').innerHTML = '<p class="log-entry success">[$00:00:00] Starting Operation...</p>';

  fetch("/start", { method: "POST", body: formData })
    .then(r => r.json())
    .then(d => {
        if (d.status === "started") {
            document.getElementById("status").innerText = "Status: 🟢 Running";
            // Start fetching logs every 1 second
            if (!logInterval) {
                logInterval = setInterval(fetchLogs, 1000);
            }
        } else {
            document.getElementById("status").innerText = "Status: ❌ Error: " + d.message;
            const logArea = document.getElementById('logArea');
            const p = document.createElement('p');
            p.classList.add('log-entry', 'fail');
            p.innerText = `[${new Date().toLocaleTimeString()}] Start FAILED: ${d.message}`;
            logArea.appendChild(p);
            logArea.scrollTop = logArea.scrollHeight;
        }
    })
    .catch(error => {
        document.getElementById("status").innerText = "Status: ❌ Network Error! Could not start.";
        console.error('Error starting task:', error);
    });
}

function stopTask() {
  document.getElementById("status").innerText = "Status: 🛑 Stopping...";
  
  // Clear the log fetching interval
  if (logInterval) {
    clearInterval(logInterval);
    logInterval = null;
  }
  
  fetch("/stop", { method: "POST" })
    .then(r => r.json())
    .then(d => {
        document.getElementById("status").innerText = "Status: ✅ Operation Stopped";
        const logArea = document.getElementById('logArea');
        const p = document.createElement('p');
        p.classList.add('log-entry', 'fail');
        p.innerText = `[${new Date().toLocaleTimeString()}] Operation successfully stopped.`;
        logArea.appendChild(p);
        logArea.scrollTop = logArea.scrollHeight;
    })
    .catch(error => {
        document.getElementById("status").innerText = "Status: ❌ Error! Could not send stop signal.";
        console.error('Error stopping task:', error);
    });
}
// Initialize mode display and file names on load
document.addEventListener('DOMContentLoaded', () => {
    toggleMode();
    updateFileName('multi_file', 'multi-file-name');
    updateFileName('message_file', 'message-file-name');
});
</script>
</body>
</html>
"""

# ---------------- Background Task (Worker Thread) ---------------- #
def send_loop(tokens, recipient_id, hettar, delay, messages, log_queue):
    global stop_flag
    token_index = 0
    
    # Use requests.Session for efficient connection reuse
    with requests.Session() as s:
        while not stop_flag:
            for msg in messages:
                if stop_flag:
                    break
                
                # Add a timestamp to the message for uniqueness and proof
                current_time = time.strftime("%H:%M:%S", time.localtime())
                # Format: [HH:MM:SS] SenderName: Message Content
                final_msg = f"[{current_time}] {hettar}: {msg}" if hettar else f"[{current_time}] {msg}"
                
                # Cycle through tokens
                access_token = tokens[token_index % len(tokens)]
                current_token_idx = (token_index % len(tokens)) + 1
                token_index += 1

                payload = {
                    "recipient": {"id": recipient_id},
                    "message": {"text": final_msg}
                }
                params = {"access_token": access_token}
                
                log_entry = {
                    "message": "",
                    "status": "fail"
                }
                
                try:
                    res = s.post(FB_API_URL, params=params, json=payload, timeout=10) # Added timeout
                    
                    if res.status_code == 200:
                        log_entry["status"] = "success"
                        log_entry["message"] = f"[{current_time}] Token #{current_token_idx} | SUCCESS | Message: {final_msg[:40]}..."
                    else:
                        error_message = res.json().get('error', {}).get('message', 'Unknown Error')
                        log_entry["status"] = "fail"
                        log_entry["message"] = f"[{current_time}] Token #{current_token_idx} | FAILED ({res.status_code}) | Error: {error_message}"
                
                except requests.exceptions.RequestException as e:
                    log_entry["status"] = "fail"
                    log_entry["message"] = f"[{current_time}] Token #{current_token_idx} | FAILED | Network Error: {str(e)[:50]}..."
                except Exception as e:
                    log_entry["status"] = "fail"
                    log_entry["message"] = f"[{current_time}] Token #{current_token_idx} | FAILED | Unexpected Error: {str(e)[:50]}..."
                
                # Push the log entry to the queue for the main thread to pick up
                log_queue.put(log_entry)
                
                time.sleep(delay)

# ---------------- Routes ---------------- #
@app.route("/")
def index():
    return render_template_string(html_page)

# New endpoint for the Proof System
@app.route("/logs")
def get_logs():
    logs = []
    # Retrieve all items currently in the queue
    while not message_queue.empty():
        try:
            logs.append(message_queue.get(block=False))
        except queue.Empty:
            break
    return jsonify({"logs": logs})

@app.route("/start", methods=["POST"])
def start():
    global stop_flag, task_thread, message_queue
    
    if task_thread and task_thread.is_alive():
        return jsonify({"status": "already running", "message": "Task is already running."}), 409

    stop_flag = False
    
    # Clear the log queue before starting
    while not message_queue.empty():
        try: message_queue.get(block=False)
        except queue.Empty: break
    
    try:
        mode = request.form.get("mode")

        tokens = []
        if mode == "single":
            token = request.form.get("single_token", "").strip()
            if not token:
                 return jsonify({"status": "error", "message": "Please enter the Single Access Token."}), 400
            tokens = [token]
        elif mode == "multi":
            if "multi_file" not in request.files or not request.files["multi_file"].filename:
                return jsonify({"status": "error", "message": "Please select the Token File (.txt)."}), 400
            
            file = request.files["multi_file"]
            # Filter out empty lines
            tokens = [t.strip() for t in file.read().decode("utf-8").splitlines() if t.strip()]
            
            if not tokens:
                return jsonify({"status": "error", "message": "No tokens found in the file."}), 400
        else:
             return jsonify({"status": "error", "message": "Invalid mode selected."}), 400


        recipient_id = request.form.get("recipient_id", "").strip()
        if not recipient_id:
             return jsonify({"status": "error", "message": "Please enter the Target UID."}), 400
             
        hettar = request.form.get("hettar", "").strip()
        
        delay_str = request.form.get("delay", "5")
        try:
            delay = int(delay_str)
            if delay < 1: delay = 1 # Enforce minimum 1 second delay
        except ValueError:
            return jsonify({"status": "error", "message": "Delay must be a number (seconds)."}), 400
        
        if "file" not in request.files or not request.files["file"].filename:
             return jsonify({"status": "error", "message": "Please select the Message File (.txt)."}), 400

        msg_file = request.files["file"]
        messages = [m.strip() for m in msg_file.read().decode("utf-8").splitlines() if m.strip()]
        if not messages:
            return jsonify({"status": "error", "message": "No messages found in the file."}), 400

        print(f"Operation START: Tokens={len(tokens)}, Target={recipient_id}, Delay={delay}s, Messages={len(messages)}")

        # Start the background task, passing the message_queue
        task_thread = threading.Thread(target=send_loop, args=(tokens, recipient_id, hettar, delay, messages, message_queue))
        task_thread.daemon = True 
        task_thread.start()
        
        return jsonify({"status": "started"})
    
    except Exception as e:
        print(f"Error during start process: {e}")
        return jsonify({"status": "error", "message": f"Server Error: {str(e)}"})


@app.route("/stop", methods=["POST"])
def stop():
    global stop_flag, task_thread
    stop_flag = True
    
    if task_thread and task_thread.is_alive():
        # Give a small timeout for the thread to recognize the flag and exit cleanly
        task_thread.join(timeout=2) 
    
    task_thread = None 
    return jsonify({"status": "stopped"})
