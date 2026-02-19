import requests
from pymongo import MongoClient
import os
import time

print('Posting sample form to /predict...')
data = {
    'age': 35,
    'height': 175,
    'weight': 75,
    'sex': '1',
    'activity': '1',
    'hgb': 14.2,
    'glucose': 95.0,
    'cholesterol': 185.0,
}

try:
    # app.py expects form posts to /upload
    r = requests.post('http://127.0.0.1:5000/upload', data=data, timeout=10)
    print('HTTP', r.status_code)
except Exception as e:
    print('Request error:', e)
    raise SystemExit(1)

time.sleep(0.5)

# Check MongoDB for most recent prediction
uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
dbn = os.environ.get('MONGO_DB', 'nutrition')
print('Connecting to MongoDB:', uri, ' DB:', dbn)
client = MongoClient(uri)
db = client[dbn]
doc = db.predictions.find_one(sort=[('created_at', -1)])
print('Most recent saved document:')
print(doc)
