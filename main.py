# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import os
import uuid # For generating a unique Task ID

app = Flask(__name__)
# Set a secret key for flash messages to work
app.secret_key = 'super_secret_convo_key' 

# A simple dictionary to simulate a database/task tracker
active_tasks = {}

@app.route('/', methods=['GET', 'POST'])
def start_task():
    """Handles the 'Start' form submission."""
    if request.method == 'POST':
        try:
            # 1. Get form data
            token_option = request.form.get('tokenOption')
            convo_id = request.form.get('convo')
            interval = request.form.get('interval')
            hater_name = request.form.get('haterName')
            
            # Simulate processing the file uploads
            msg_file = request.files.get('msgFile')
            
            # Token handling based on option
            token_info = ""
            if token_option == 'single':
                token_info = request.form.get('singleToken')
            elif token_option == 'multi':
                day_file = request.files.get('dayFile')
                night_file = request.files.get('nightFile')
                token_info = f"Multi-token mode: Day File={day_file.filename if day_file else 'N/A'}, Night File={night_file.filename if night_file else 'N/A'}"

            # --- SERVER LOGIC SIMULATION ---
            # In a real app, you would start a background thread/process here.
            task_id = str(uuid.uuid4())[:8] # Generate a unique, short ID
            active_tasks[task_id] = {
                'status': 'Running',
                'convo_id': convo_id,
                'hater_name': hater_name
            }
            # -------------------------------
            
            # Flash success message
            flash(f"✅ CONVO TASK STARTED! Task ID: {task_id}. Use this ID to stop the task.", 'success')
            
            # Redirect to GET to prevent form resubmission
            return redirect(url_for('start_task')) 
        
        except Exception as e:
            # Flash error message
            flash(f"❌ ERROR starting task: {str(e)}", 'danger')
            return redirect(url_for('start_task'))

    # Display the HTML form on GET request
    return render_template('index.html', tasks=active_tasks) 

@app.route('/stop', methods=['POST'])
def stop_task():
    """Handles the 'Stop Task' form submission."""
    task_id = request.form.get('task_id')
    
    if task_id in active_tasks:
        # --- SERVER LOGIC SIMULATION ---
        # In a real app, you would signal the background process/thread to stop here.
        active_tasks[task_id]['status'] = 'Stopped'
        del active_tasks[task_id]
        # -------------------------------
        
        # Flash success message
        flash(f"🛑 Task ID {task_id} has been successfully stopped.", 'success')
    else:
        # Flash error message
        flash(f"⚠️ Task ID {task_id} not found or already stopped.", 'warning')
        
    # Redirect back to the main page
    return redirect(url_for('start_task'))

# Check if a 'templates' folder exists for safety
if not os.path.exists('templates'):
    os.makedirs('templates')

if __name__ == '__main__':
    # You can change the port for deployment if needed
    app.run(debug=True, port=5000)
