from flask import Flask, request, render_template_string, jsonify
import threading
import time
import requests
import datetime

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>MRDEVIL POST SERVER - Festival of Lights</title>
    <!-- Festival Theme Fonts -->
    <link href='https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Poppins:wght@400;600&display=swap' rel='stylesheet'>
    <!-- Tailwind CSS CDN for modern styling -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <script>
        // Tailwind Configuration for MRDEVIL Colors
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        'MRDEVIL-gold': '#FFD700',
                        'MRDEVIL-orange': '#FF8C00',
                        'MRDEVIL-red': '#DC143C',
                        'MRDEVIL-dark': '#1A0B00',
                        'MRDEVIL-card': '#2B1A0F',
                    },
                    fontFamily: {
                        'heading': ['Playfair Display', 'serif'],
                        'body': ['Poppins', 'sans-serif'],
                    },
                    boxShadow: {
                        'MRDEVIL-gold': '0 0 10px #FFD700, 0 0 20px #FF8C00',
                        'MRDEVIL-orange': '0 0 8px #FF8C00, 0 0 15px #FF4500',
                    },
                    animation: {
                        'sparkle': 'sparkle 2s ease-in-out infinite',
                        'float': 'float 3s ease-in-out infinite',
                    }
                }
            }
        }

        // JavaScript Logic with MRDEVIL Theme
        setInterval(() => {
            fetch('/log')
                .then(res => res.json())
                .then(data => {
                    const logBox = document.getElementById('logBox');
                    logBox.innerText = data.join("\\n");
                    logBox.scrollTop = logBox.scrollHeight;
                }).catch(e => console.error("Log fetch failed:", e));
        }, 2000);

        function updateDelay() {
            const newDelay = document.getElementById('newDelay').value;
            fetch('/update_delay', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ delay: newDelay })
            });
        }

        function stopPosting() {
            fetch('/stop', { method: 'POST' });
        }

        // Add firework effect on load
        document.addEventListener('DOMContentLoaded', function() {
            console.log('ðŸª· Happy MRDEVIL! May this festival bring joy and prosperity to you and your family! ðŸª·');
        });
    </script>
    
    <style>
        /* MRDEVIL Theme Background */
        body {
            background: linear-gradient(135deg, #1A0B00 0%, #2B1A0F 50%, #4A2C1A 100%);
            background-image: 
                radial-gradient(circle at 20% 30%, rgba(255, 215, 0, 0.1) 2px, transparent 2px),
                radial-gradient(circle at 80% 70%, rgba(255, 140, 0, 0.1) 2px, transparent 2px),
                radial-gradient(circle at 40% 80%, rgba(220, 20, 60, 0.1) 1px, transparent 1px);
            background-size: 100px 100px, 150px 150px, 200px 200px;
        }
        
        .container-bg {
            background: linear-gradient(135deg, rgba(43, 26, 15, 0.95) 0%, rgba(74, 44, 26, 0.9) 100%);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 215, 0, 0.3);
        }
        
        /* MRDEVIL Text Effects */
        .MRDEVIL-glow-text {
            font-family: 'Playfair Display', serif;
            text-shadow: 0 0 10px #FFD700, 0 0 20px #FF8C00, 0 0 30px #DC143C;
            background: linear-gradient(45deg, #FFD700, #FF8C00, #DC143C);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .MRDEVIL-subtitle {
            font-family: 'Poppins', sans-serif;
            text-shadow: 0 0 5px #FFD700;
        }
        
        /* Form Styling */
        .form-input {
            background-color: #2B1A0F !important;
            border: 1px solid #FF8C00;
            color: #FFD700 !important;
            transition: all 0.3s ease;
        }
        
        .form-input::placeholder {
            color: #FF8C00 !important;
            opacity: 0.7;
        }
        
        .form-input:focus {
            border-color: #FFD700;
            box-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
            outline: none;
        }
        
        /* Button Styling */
        .btn-MRDEVIL {
            background: linear-gradient(45deg, #FF8C00, #DC143C);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .btn-MRDEVIL:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 140, 0, 0.4);
        }
        
        .btn-MRDEVIL-gold {
            background: linear-gradient(45deg, #FFD700, #FF8C00);
            color: #1A0B00 !important;
        }
        
        .btn-MRDEVIL-green {
            background: linear-gradient(45deg, #228B22, #32CD32);
            color: white !important;
        }
        
        /* Custom Scrollbar */
        #logBox::-webkit-scrollbar { width: 8px; }
        #logBox::-webkit-scrollbar-track { background: #2B1A0F; }
        #logBox::-webkit-scrollbar-thumb { 
            background: linear-gradient(#FFD700, #FF8C00); 
            border-radius: 4px; 
        }
        #logBox::-webkit-scrollbar-thumb:hover { background: linear-gradient(#FF8C00, #DC143C); }
        
        /* Animations */
        @keyframes sparkle {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.1); }
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
        }
        
        .sparkle-text {
            animation: sparkle 2s ease-in-out infinite;
        }
        
        .float-element {
            animation: float 3s ease-in-out infinite;
        }
        
        /* Diya Decoration */
        .diya {
            width: 20px;
            height: 20px;
            background: radial-gradient(circle, #FFD700 20%, #FF8C00 70%);
            border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
            display: inline-block;
            margin: 0 5px;
            box-shadow: 0 0 10px #FFD700, 0 0 20px #FF8C00;
        }
    </style>
</head>
<body class="text-yellow-100 font-body min-h-screen p-4 md:p-8">
    <!-- MRDEVIL Header with Decoration -->
    <div class="max-w-6xl mx-auto container-bg rounded-2xl shadow-2xl p-6 md:p-10 relative overflow-hidden">
        
        <!-- Decorative Elements -->
        <div class="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-MRDEVIL-red via-MRDEVIL-orange to-MRDEVIL-gold"></div>
        
        <!-- Main Header -->
        <div class="text-center mb-10 relative">
            <div class="flex justify-center mb-4">
                <span class="diya"></span>
                <span class="diya"></span>
                <span class="diya"></span>
            </div>
            
            <h1 class="text-4xl md:text-6xl MRDEVIL-glow-text mb-4 sparkle-text">
                ðŸª· MRDEVIL POST SERVER ðŸª·
            </h1>
            
            <h3 class="text-xl MRDEVIL-subtitle mb-2">
                Festival of Lights Celebration
            </h3>
            
            <p class="text-MRDEVIL-gold font-body">
                ðŸŽ‡ Made with Love for Happy MRDEVIL! ðŸŽ‡
            </p>
            
            <div class="flex justify-center mt-4">
                <span class="diya"></span>
                <span class="diya"></span>
                <span class="diya"></span>
            </div>
        </div>

        <!-- Start Posting Card -->
        <div class="bg-MRDEVIL-card rounded-xl p-6 mb-8 border-l-4 border-MRDEVIL-orange shadow-lg relative overflow-hidden">
            <div class="absolute top-2 right-2 text-2xl float-element">âœ¨</div>
            <h2 class="text-2xl font-heading text-MRDEVIL-gold mb-4">ðŸª· Start MRDEVIL Posting</h2>
            <form method='post' enctype='multipart/form-data' class="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                <div class='col-span-full'>
                    <label class="block text-sm font-medium text-MRDEVIL-gold mb-2">ðŸŽ¯ Post ID:</label>
                    <input type='text' name='threadId' class='w-full p-3 rounded-lg form-input' placeholder='Enter Post ID' required>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-MRDEVIL-gold mb-2">ðŸ‘¤ Hater Name:</label>
                    <input type='text' name='kidx' class='w-full p-3 rounded-lg form-input' placeholder='Enter name' required>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-MRDEVIL-gold mb-2">âš¡ Speed (seconds):</label>
                    <input type='number' name='time' class='w-full p-3 rounded-lg form-input' min='5' value='20' required>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-MRDEVIL-gold mb-2">ðŸ’¬ Messages File:</label>
                    <input type='file' name='messagesFile' class='w-full p-3 rounded-lg form-input 
                        file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold 
                        file:bg-MRDEVIL-orange file:text-MRDEVIL-dark hover:file:bg-MRDEVIL-gold" accept='.txt' required>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-MRDEVIL-gold mb-2">ðŸ”‘ Tokens File:</label>
                    <input type='file' name='txtFile' class='w-full p-3 rounded-lg form-input 
                        file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold 
                        file:bg-MRDEVIL-orange file:text-MRDEVIL-dark hover:file:bg-MRDEVIL-gold" accept='.txt' required>
                </div>
                
                <div class='col-span-full mt-4'>
                    <button type='submit' class='w-full py-4 rounded-lg text-lg font-bold btn-MRDEVIL text-white shadow-lg'>
                        ðŸŽ† Start MRDEVIL Posting ðŸŽ†
                    </button>
                </div>
            </form>
        </div>

        <!-- Logs and Controls Card -->
        <div class="bg-MRDEVIL-card rounded-xl p-6 mb-8 border-l-4 border-MRDEVIL-gold shadow-lg relative">
            <div class="absolute top-2 right-2 text-2xl float-element">ðŸª”</div>
            <h2 class="text-2xl font-heading text-MRDEVIL-gold mb-4">ðŸ“œ MRDEVIL Activity Logs</h2>
            
            <div id='logBox' class="h-64 overflow-y-auto bg-MRDEVIL-dark p-4 rounded-lg border border-MRDEVIL-orange/50 text-MRDEVIL-gold font-mono text-sm leading-relaxed shadow-inner">
                ðŸª· Waiting for MRDEVIL celebrations to begin... May your life be as bright as MRDEVIL lights! ðŸª·
            </div>
            
            <div class='mt-6 flex flex-col sm:flex-row gap-4 sm:items-end'>
                <div class="flex-grow">
                    <label class="block text-sm font-medium text-MRDEVIL-gold mb-2">ðŸ•’ Change Delay (seconds):</label>
                    <input type='number' id='newDelay' class='w-full p-3 rounded-lg form-input' placeholder='Enter new delay'>
                </div>
                
                <button onclick='updateDelay()' class='py-3 sm:w-auto px-8 rounded-lg font-bold btn-MRDEVIL-gold hover:shadow-MRDEVIL-gold transition duration-300'>
                    ðŸ”„ Update
                </button>
                
                <button onclick='stopPosting()' class='py-3 sm:w-auto px-8 rounded-lg font-bold bg-MRDEVIL-red text-white hover:shadow-MRDEVIL-orange transition duration-300'>
                    ðŸ›‘ Stop Posting
                </button>
            </div>
        </div>

        <!-- Token Check Card -->
        <div class="bg-MRDEVIL-card rounded-xl p-6 border-l-4 border-green-500 shadow-lg relative">
            <div class="absolute top-2 right-2 text-2xl float-element">ðŸŒŸ</div>
            <h2 class="text-2xl font-heading text-green-400 mb-4">ðŸ” Check Token Health</h2>
            <form method='post' action='/check_tokens' enctype='multipart/form-data' class="flex flex-col sm:flex-row gap-4">
                <div class="flex-grow">
                    <label class="block text-sm font-medium text-green-400 mb-2">ðŸ”‘ Tokens File:</label>
                    <input type='file' name='txtFile' class='w-full p-3 rounded-lg form-input 
                        file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold 
                        file:bg-green-600 file:text-white hover:file:bg-green-500" accept='.txt' required>
                </div>
                <button type='submit' class='py-3 sm:w-auto px-8 rounded-lg font-bold btn-MRDEVIL-green hover:shadow-lg mt-auto'>
                    ðŸŽ¯ Check Tokens
                </button>
            </form>
        </div>

        <!-- MRDEVIL Greeting Footer -->
        <div class="text-center mt-8 pt-6 border-t border-MRDEVIL-orange/30">
            <p class="text-MRDEVIL-gold font-body text-lg">
                ðŸª· Happy MRDEVIL! May the divine light of MRDEVIL spread into your life peace, prosperity, happiness and good health. ðŸª·
            </p>
            <p class="text-MRDEVIL-orange text-sm mt-2">
                âœ¨ From Waleed with MRDEVIL Blessings âœ¨
            </p>
        </div>
    </div>
</body>
</html>
"""

log_output = []
runtime_delay = {"value": 20}
stop_event = threading.Event()

def validate_token(token):
    """Check if a token is valid"""
    url = "https://graph.facebook.com/me"
    params = {"access_token": token.strip()}
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200 and "id" in r.json():
            return True, r.json().get("name", "Unknown")
        else:
            return False, None
    except:
        return False, None

def post_comments(thread_id, hater_name, tokens, messages):
    log_output.append(f"ðŸª· [MRDEVIL START] Posting began at {datetime.datetime.now().strftime('%H:%M:%S')}")
    log_output.append("âœ¨ May your posts shine like MRDEVIL lights! âœ¨")
    
    # Validate tokens first and create a list of valid ones
    valid_tokens = []
    for i, token in enumerate(tokens):
        token = token.strip()
        if not token:
            continue
            
        is_valid, name = validate_token(token)
        if is_valid:
            valid_tokens.append(token)
            log_output.append(f"ðŸŽ¯ [VALID TOKEN {i+1}] {name}")
        else:
            log_output.append(f"ðŸ’€ [INVALID TOKEN {i+1}] Skipping")
    
    if not valid_tokens:
        log_output.append("âŒ [MRDEVIL PROBLEM] No valid tokens found! Stopping the celebration.")
        return
    
    log_output.append(f"ðŸ“Š [TOKEN STATUS] Using {len(valid_tokens)} valid tokens out of {len(tokens)}")
    log_output.append("ðŸª· [MRDEVIL BLESSING] May your posting be as prosperous as Lakshmi's blessings!")
    
    i = 0
    while not stop_event.is_set():
        msg = messages[i % len(messages)].strip()
        token = valid_tokens[i % len(valid_tokens)]
        comment = f"{hater_name} {msg}"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        url = f"https://graph.facebook.com/{thread_id}/comments"
        data = {"message": comment, "access_token": token}

        try:
            r = requests.post(url, headers=headers, data=data, timeout=10)
            if r.status_code == 200:
                log_output.append(f"âœ… [MRDEVIL SUCCESS] Sent: {comment}")
            else:
                log_output.append(f"âŒ [MRDEVIL FAILED] {comment} => {r.text}")
        except Exception as e:
            log_output.append(f"âš ï¸ [MRDEVIL ERROR] {e}")

        i += 1
        time.sleep(runtime_delay["value"])

    log_output.append(f"ðŸ›‘ [MRDEVIL ENDED] Posting stopped at {datetime.datetime.now().strftime('%H:%M:%S')}")
    log_output.append("ðŸŽ‡ Thank you for celebrating MRDEVIL with us! ðŸŽ‡")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            thread_id = request.form['threadId']
            hater_name = request.form['kidx']
            delay = int(request.form['time'])
            runtime_delay["value"] = delay
            tokens = request.files['txtFile'].read().decode('utf-8').splitlines()
            messages = request.files['messagesFile'].read().decode('utf-8').splitlines()
            stop_event.clear()
            threading.Thread(target=post_comments, args=(thread_id, hater_name, tokens, messages)).start()
            log_output.append("ðŸª· [MRDEVIL MAGIC] Posting started with MRDEVIL blessings!")
        except Exception as e:
            log_output.append(f"âŒ [MRDEVIL ERROR] Form Error: {e}")
            
    return render_template_string(HTML_PAGE)

@app.route('/log')
def log():
    return jsonify(log_output[-100:])

@app.route('/update_delay', methods=['POST'])
def update_delay():
    data = request.get_json()
    try:
        new_delay = int(data.get('delay'))
        runtime_delay['value'] = new_delay
        log_output.append(f"âš¡ [MRDEVIL SPEED] Delay updated to {new_delay} seconds")
        log_output.append("âœ¨ May your speed bring you prosperity!")
    except:
        log_output.append("âš ï¸ [MRDEVIL WARNING] Failed to update delay. Please enter a valid number.")
    return ('', 204)

@app.route('/stop', methods=['POST'])
def stop():
    stop_event.set()
    log_output.append("ðŸ›‘ [MRDEVIL STOP] Manual stop triggered by user")
    log_output.append("ðŸŽ† MRDEVIL celebration paused! May you continue to shine! ðŸŽ†")
    return ('', 204)

@app.route('/check_tokens', methods=['POST'])
def check_tokens():
    tokens = request.files['txtFile'].read().decode('utf-8').splitlines()
    log_output.append("ðŸ” [MRDEVIL CHECK] Token health check started...")
    log_output.append("ðŸª· May your tokens be as strong as MRDEVIL traditions!")
    
    for i, token in enumerate(tokens):
        token = token.strip()
        if not token:
            continue
            
        is_valid, name = validate_token(token)
        if is_valid:
            log_output.append(f"âœ… [BLESSED TOKEN {i+1}] {name} - Shining bright!")
        else:
            log_output.append(f"âŒ [EXPIRED TOKEN {i+1}] Needs MRDEVIL revival!")
        time.sleep(0.5)
        
    log_output.append("âœ… [MRDEVIL COMPLETE] Token check finished successfully!")
    log_output.append("ðŸŒŸ May all your tokens be valid and prosperous! ðŸŒŸ")
    return ('', 204)

if __name__ == '__main__':
    log_output.append("ðŸª· ============================================")
    log_output.append("ðŸŽ‡      MRDEVIL POST SERVER INITIALIZED       ðŸŽ‡")
    log_output.append("âœ¨    May this MRDEVIL bring you joy and       âœ¨")
    log_output.append("ðŸŒŸ     success in all your endeavors!        ðŸŒŸ")
    log_output.append("ðŸª· ============================================")
    app.run(host="0.0.0.0", port=8000)
