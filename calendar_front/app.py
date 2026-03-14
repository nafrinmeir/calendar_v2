from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)
API_URL = os.getenv("API_URL", "http://localhost:5001")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"service": "Calendar Frontend", "status": "Healthy"}), 200

@app.route('/')
def index():
    return render_template('index.html', api_url=API_URL)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)