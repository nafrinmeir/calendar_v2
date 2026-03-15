from flask import Flask, render_template
import os

app = Flask(__name__)

API_URL = os.getenv("API_URL", "http://localhost:5001")
# קורא את מספר הגרסה
APP_VERSION = os.getenv("APP_VERSION", "v1.0")

@app.route('/')
def index():
    # מעביר את הגרסה ל-HTML
    return render_template('index.html', api_url=API_URL, app_version=APP_VERSION)

@app.route('/health')
def health():
    return {"status": "Healthy", "service": "Calendar Frontend", "version": APP_VERSION}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
