from flask import Flask, render_template, request, jsonify
import schedule
import time
from datetime import datetime
import threading
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Store scheduled messages
scheduled_messages = []

def send_message(text):
    current_time = datetime.now().strftime('%H:%M')
    logger.info(f"Sending message at {current_time}: {text}")
    return True

def schedule_message(time_str, text):
    try:
        datetime.strptime(time_str, '%H:%M')
        schedule.every().day.at(time_str).do(send_message, text)
        scheduled_messages.append({
            'time': time_str,
            'message': text,
            'status': 'scheduled',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        logger.info(f"Message scheduled for {time_str}: {text}")
        return True, f"Message scheduled for {time_str}"
    except Exception as e:
        logger.error(f"Scheduling error: {e}")
        return False, str(e)

def run_scheduler():
    logger.info("Scheduler thread started")
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/schedule', methods=['POST'])
def schedule_endpoint():
    try:
        data = request.get_json()
        time_str = data.get('time')
        message = data.get('message')
        
        if not time_str or not message:
            return jsonify({'status': 'error', 'message': 'Missing time or message'}), 400
            
        success, response = schedule_message(time_str, message)
        if success:
            return jsonify({'status': 'success', 'message': response})
        return jsonify({'status': 'error', 'message': response}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/messages')
def get_messages():
    return jsonify(scheduled_messages)

if __name__ == '__main__':
    # Start scheduler thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Get port from environment variable (Heroku sets this automatically)
    port = int(os.environ.get('PORT', 5000))
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port)
