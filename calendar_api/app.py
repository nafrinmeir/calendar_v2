from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
CORS(app)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/calendar_db")
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
db = client.get_database()
events_collection = db.events

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/health', methods=['GET'])
def health_check():
    try:
        client.admin.command('ping')
        db_status = "Connected"
    except Exception:
        db_status = "Disconnected"
    return jsonify({"service": "Calendar API", "status": "Healthy", "database": db_status}), 200 if db_status == "Connected" else 500

@app.route('/events', methods=['GET', 'POST'])
def manage_events():
    if request.method == 'POST':
        data = request.json
        if data.get('title') and data.get('start'):
            # שמירת האירוע כולל שעות
            result = events_collection.insert_one({
                "title": data['title'], 
                "start": data['start'],
                "end": data.get('end'),
                "allDay": data.get('allDay', True)
            })
            return jsonify({"message": "Event added", "id": str(result.inserted_id)}), 201
        return jsonify({"error": "Missing data"}), 400
    
    # בשליפת נתונים, אנחנו ממירים את ה-_id של מונגו ל-id רגיל שהיומן יודע לקרוא
    events = []
    for ev in events_collection.find():
        ev['id'] = str(ev['_id'])
        del ev['_id']
        events.append(ev)
    return jsonify(events), 200

# נתיב חדש לעריכה (PUT) ומחיקה (DELETE) לפי ID
@app.route('/events/<event_id>', methods=['PUT', 'DELETE'])
def modify_event(event_id):
    try:
        obj_id = ObjectId(event_id)
    except:
        return jsonify({"error": "Invalid ID format"}), 400

    if request.method == 'DELETE':
        events_collection.delete_one({"_id": obj_id})
        return jsonify({"message": "Deleted"}), 200
    
    if request.method == 'PUT':
        data = request.json
        update_data = {k: v for k, v in data.items() if k in ['title', 'start', 'end', 'allDay']}
        events_collection.update_one({"_id": obj_id}, {"$set": update_data})
        return jsonify({"message": "Updated"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)