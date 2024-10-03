from flask import Flask, request, jsonify, send_from_directory, session
from flask_session import Session
import json
import os
import time
from openai import OpenAI
from flask_cors import CORS
import sys
from io import StringIO
import logging


app = Flask(__name__)
CORS(app)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

API_KEY = 0 # Your APIKEYHERE
client = OpenAI(api_key=API_KEY)
BOT_ID = "asst_w2AEP1vnmprwp0VxrLae0GgT"

logging.basicConfig(level=logging.DEBUG)

def log_session_data(action, data):
    logging.debug(f"{action} | Session Data: {data}")
    
@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.json['message']
    log_session_data("Received Message", user_message)
    # Rest of your existing logic
    log_session_data("Updated Session", session)
    print(f"Received user message: {user_message}")

    if 'chat_history' not in session:
        session['chat_history'] = []
        print("No chat history found, initializing new session.")

    session['chat_history'].append(f"User: {user_message}")

    if 'thread_id' not in session:
        thread, run = create_thread_and_run(user_message)
        session['thread_id'] = thread.id
        print(f"New thread created with ID: {thread.id}")
    else:
        thread_id = session['thread_id']
        thread = get_thread(thread_id)
        run = submit_message(BOT_ID, thread_id, user_message)
        print(f"Using existing thread ID: {thread_id}")

    run = wait_on_run(run, thread)
    response = get_response(thread)
    session['chat_history'].append(f"Bot: {response}")

    print(f"Current session chat history: {session['chat_history']}")

    return jsonify({"response": response, "thread_id": thread.id})


@app.route('/inspect_session', methods=['GET'])
def inspect_session():
    return jsonify(dict(session))

@app.route('/')
def index():
    session.clear()  # Clear existing session data
    return send_from_directory('static', 'index.html')


@app.route('/run_code', methods=['POST'])
def run_code():
    code = request.json['code']
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    try:
        exec(code)
        sys.stdout = old_stdout
        result = redirected_output.getvalue()
        return jsonify({"result": result})
    except Exception as e:
        sys.stdout = old_stdout
        return jsonify({"error": str(e)})

def create_thread_and_run(user_input):
    try:
        thread = client.beta.threads.create()
        run = submit_message(BOT_ID, thread.id, user_input)
        print(f"New Thread and Run Created: Thread ID {thread.id}, Run ID {run.id}")
        return thread, run
    except Exception as e:
        print(f"Failed to create thread: {str(e)}")
        return None, None

def submit_message(assistant_id, thread_id, user_message):
    try:
        client.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_message)
        run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)
        print(f"Message submitted to Thread {thread_id}, Run {run.id} created")
        return run
    except Exception as e:
        print(f"Failed to submit message or create run: {str(e)}")
        return None

def get_thread(thread_id):
    try:
        thread = client.beta.threads.retrieve(thread_id=thread_id)
        print(f"Retrieved Thread: {thread.id}")
        return thread
    except Exception as e:
        print(f"Error retrieving thread {thread_id}: {str(e)}")
        return None


def wait_on_run(run, thread):
    try:
        while run.status in ["queued", "in_progress"]:
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            time.sleep(1    )  # Consider adjusting this based on expected wait times
    except Exception as e:
        print(f"Error waiting on run: {str(e)}")
        return None  # Optionally, you might handle specific exceptions differently
    return run


def get_response(thread):
    # Set a higher limit to retrieve more messages from the thread
    messages = client.beta.threads.messages.list(thread_id=thread.id, order="asc", limit=100).data
    assistant_messages = [msg for msg in messages if msg.role == 'assistant']
    if assistant_messages:
        last_message = assistant_messages[-1]
        if isinstance(last_message.content, list):
            # Extract the text value from the first TextContentBlock of the last assistant message
            return ' '.join(block.text.value for block in last_message.content if hasattr(block.text, 'value'))
    return "No response."


if __name__ == '__main__':
    app.run(debug=True)
