import os
from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

OLLAMA_PORT = os.environ.get('OLLAMA_PORT', '11434')
OLLAMA_API_BASE = f"http://localhost:{OLLAMA_PORT}/api"

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', '')
    
    try:
        ollama_response = requests.post(f"{OLLAMA_API_BASE}/generate", json={
            "model": "llama3",
            "prompt": prompt
        }, stream=True)
        
        ollama_response.raise_for_status()
        
        # Collect all chunks
        full_response = ""
        for chunk in ollama_response.iter_lines():
            if chunk:
                try:
                    chunk_data = json.loads(chunk.decode('utf-8'))
                    full_response += chunk_data.get('response', '')
                except json.JSONDecodeError:
                    app.logger.error(f"Failed to decode chunk: {chunk}")
        
        return jsonify({"response": full_response})
    except requests.RequestException as e:
        app.logger.error(f"Request to Ollama API failed: {str(e)}")
        return jsonify({"error": "Failed to generate response"}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])
    
    try:
        ollama_response = requests.post(f"{OLLAMA_API_BASE}/chat", json={
            "model": "llama3",
            "messages": messages
        }, stream=True)
        
        ollama_response.raise_for_status()
        
        # Collect all chunks
        full_response = ""
        for chunk in ollama_response.iter_lines():
            if chunk:
                try:
                    chunk_data = json.loads(chunk.decode('utf-8'))
                    full_response += chunk_data.get('message', {}).get('content', '')
                except json.JSONDecodeError:
                    app.logger.error(f"Failed to decode chunk: {chunk}")
        
        return jsonify({"response": full_response})
    except requests.RequestException as e:
        app.logger.error(f"Request to Ollama API failed: {str(e)}")
        return jsonify({"error": "Failed to generate chat response"}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
