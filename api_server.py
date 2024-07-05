from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', '')
    
    ollama_response = requests.post('http://localhost:11434/api/generate', json={
        'model': 'yourgpt',
        'prompt': prompt
    })
    
    return jsonify(ollama_response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
