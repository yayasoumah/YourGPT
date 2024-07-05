import subprocess
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

LLAMAFILE_PATH = "/mistral-7b-instruct-v0.2.Q4_0.llamafile"

def run_llamafile(prompt):
    command = [LLAMAFILE_PATH, "--temp", "0.7", "-p", prompt]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout.strip()

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', '')
    
    response = run_llamafile(prompt)
    
    return jsonify({"response": response})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])
    
    # Construct a prompt from the messages
    prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
    prompt += "\nassistant:"
    
    response = run_llamafile(prompt)
    
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
