from flask import Flask, render_template, request, jsonify
import schedule
import time
from datetime import datetime
import threading
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Store scheduled messages
scheduled_messages = []

class MessageScheduler:
    @staticmethod
    def send_message(text):
        """Send a scheduled message"""
        current_time = datetime.now().strftime('%H:%M')
        logger.info(f"Sending message at {current_time}: {text}")
        return True

    @staticmethod
    def convert_time_format(time_str):
        """Convert 12-hour format to 24-hour format"""
        try:
            if "pm" in time_str.lower():
                time_str = time_str.lower().replace("pm", "").strip()
                hour = int(time_str.split(":")[0])
                if hour != 12:
                    hour += 12
                return f"{hour:02d}:{time_str.split(':')[1].strip()}"
            else:
                return time_str.lower().replace("am", "").strip()
        except Exception as e:
            logger.error(f"Time conversion error: {e}")
            raise ValueError("Invalid time format")

    @staticmethod
    def schedule_message(time_str, text):
        """Schedule a message for delivery"""
        try:
            # Validate time format
            datetime.strptime(time_str, '%H:%M')
            
            schedule.every().day.at(time_str).do(MessageScheduler.send_message, text)
            scheduled_messages.append({
                'time': time_str,
                'message': text,
                'status': 'scheduled',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            logger.info(f"Message scheduled for {time_str}: {text}")
            return True, f"Message scheduled for {time_str}"
        except ValueError as e:
            logger.error(f"Scheduling error: {e}")
            return False, "Invalid time format. Please use HH:MM format"
        except Exception as e:
            logger.error(f"Scheduling error: {e}")
            return False, f"Failed to schedule message: {str(e)}"

def run_scheduler():
    """Background thread to run the scheduler"""
    logger.info("Scheduler thread started")
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            time.sleep(5)  # Wait before retrying

@app.route('/')
def home():
    """Render the home page"""
    logger.debug("Home page accessed")
    return render_template('index.html')

@app.route('/schedule', methods=['POST'])
def schedule_endpoint():
    """Handle message scheduling requests"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400

        time_str = data.get('time')
        message = data.get('message')

        if not time_str or not message:
            return jsonify({
                'status': 'error',
                'message': 'Time and message are required'
            }), 400

        logger.debug(f"Scheduling request - Time: {time_str}, Message: {message}")
        success, response = MessageScheduler.schedule_message(time_str, message)

        if success:
            return jsonify({
                'status': 'success',
                'message': response
            })
        return jsonify({
            'status': 'error',
            'message': response
        }), 400

    except Exception as e:
        logger.error(f"Schedule endpoint error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@app.route('/messages')
def get_messages():
    """Get all scheduled messages"""
    try:
        logger.debug(f"Retrieving messages. Count: {len(scheduled_messages)}")
        return jsonify(scheduled_messages)
    except Exception as e:
        logger.error(f"Error retrieving messages: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve messages'
        }), 500

def process_command(command):
    """Process command-line scheduling commands"""
    if command.lower() == 'exit':
        return False

