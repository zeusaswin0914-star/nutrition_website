from pymongo import MongoClient
from pprint import pprint

uri = 'mongodb://localhost:27017/'
client = MongoClient(uri)
db = client['nutrition_db']
col = db['predictions']
print('Querying:', uri, 'DB:nutrition_db', 'Collection:predictions')
doc = col.find_one(sort=[('created_at', -1)])
if not doc:
    print('No documents found')
else:
    pprint(doc)
