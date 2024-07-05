from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

OLLAMA_API_BASE = "http://localhost:11434/api"

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', '')
    
    ollama_response = requests.post(f"{OLLAMA_API_BASE}/generate", json={
        "model": "llama3",
        "prompt": prompt
    })
    
    if ollama_response.status_code == 200:
        return jsonify(ollama_response.json())
    else:
        return jsonify({"error": "Failed to generate response"}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])
    
    ollama_response = requests.post(f"{OLLAMA_API_BASE}/chat", json={
        "model": "llama3",
        "messages": messages
    })
    
    if ollama_response.status_code == 200:
        return jsonify(ollama_response.json())
    else:
        return jsonify({"error": "Failed to generate chat response"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
