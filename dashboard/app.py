from flask import Flask, render_template
import requests
import os

app = Flask(__name__)

# כתובות פנימיות - לאיסוף סטטוסים בתוך הרשת של קוברנטיס
FRONT_URL = os.getenv("FRONT_URL", "http://calendar-front:5002/health")
API_URL = os.getenv("API_URL", "http://calendar-api:5001/health")

# כתובות חיצוניות - עבור הלינקים שהמשתמש לוחץ עליהם בדפדפן
EXT_FRONT_URL = os.getenv("EXT_FRONT_URL", "http://localhost:5002")
EXT_API_URL = os.getenv("EXT_API_URL", "http://localhost:5001")

def check_service(url):
    try:
        response = requests.get(url, timeout=2)
        return response.json() if response.status_code == 200 else {"status": "Unhealthy"}
    except:
        return {"status": "Down"}

@app.route('/')
def dashboard():
    front_status = check_service(FRONT_URL)
    api_status = check_service(API_URL)
    
    db_status = {"status": api_status.get("database", "Down")} if api_status.get("status") != "Down" else {"status": "Down"}
    
    return render_template('index.html', 
                           front=front_status, 
                           api=api_status, 
                           db=db_status,
                           ext_front=EXT_FRONT_URL,
                           ext_api=EXT_API_URL)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)