import logging
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MODEL_STATUS = "NOT_STARTED"
MODEL_PROCESS = None

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({"status": MODEL_STATUS})

@app.route('/generate', methods=['POST'])
def generate():
    global MODEL_STATUS
    if MODEL_STATUS != "READY":
        return jsonify({"error": "Model is not ready yet"}), 503
    
    data = request.json
    prompt = data.get('prompt', '')
    
    try:
        response = subprocess.run([
            "curl", "-X", "POST", "http://localhost:8080/completion",
            "-H", "Content-Type: application/json",
            "-d", f'{{"prompt": "{prompt}", "n_predict": 128}}'
        ], capture_output=True, text=True)
        return jsonify({"response": response.stdout})
    except Exception as e:
        logging.error(f"Error in generate: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)