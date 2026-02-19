"""Mongo helper with graceful fallback when pymongo is unavailable.

If `pymongo` is installed and a MongoDB server is reachable, this module
uses a real MongoDB collection. If not, it falls back to an in-memory
list (useful for local development without MongoDB).
"""

from datetime import datetime

_USE_MONGO = False
_client = None
_db = None
_collection = None
_in_memory_store = []

try:
    from pymongo import MongoClient
    _USE_MONGO = True
except Exception:
    MongoClient = None
    _USE_MONGO = False


def init_mongo():
    """Initialize real MongoDB connection if available.

    If pymongo is not installed or connection fails, the function will
    fall back to the in-memory store and print a warning.
    """
    global _client, _db, _collection, _USE_MONGO

    if not _USE_MONGO:
        print("[WARN] pymongo not installed — running with in-memory store")
        return

    try:
        _client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        # Attempt a server info call to confirm connection
        _client.server_info()
        _db = _client["nutrition_db"]
        _collection = _db["predictions"]
        print("[OK] MongoDB connected successfully")
    except Exception as e:
        print("[WARN] MongoDB connection failed — falling back to in-memory store:", e)
        _client = None
        _db = None
        _collection = None
        _USE_MONGO = False


def get_collection():
    """Return the predictions collection or a proxy that writes to memory."""
    if _USE_MONGO and _collection is not None:
        return _collection
    # Return a simple proxy object with insert_one method writing to list
    class _Proxy:
        def insert_one(self, doc):
            _in_memory_store.append(doc)
            return None

        def find(self, *args, **kwargs):
            return list(_in_memory_store)

        def find_one(self, *args, **kwargs):
            return _in_memory_store[0] if _in_memory_store else None

        def sort(self, *args, **kwargs):
            return list(_in_memory_store)

    return _Proxy()


def save_prediction(inputs, prediction, report, recommendations):
    """Save a prediction document either to MongoDB or the in-memory store."""
    col = get_collection()
    document = {
        "inputs": inputs,
        "prediction": prediction,
        "report": report,
        "recommendations": recommendations,
        "created_at": datetime.now()
    }
    try:
        # If real collection, insert_one will return an InsertOneResult
        col.insert_one(document)
    except Exception:
        # Proxy insert_one may return None; ensure we still capture it
        try:
            _in_memory_store.append(document)
        except Exception:
            print("[ERROR] Failed to save prediction")
