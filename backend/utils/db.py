import os
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "pii_protection_db"

# Fallback database structure using local JSON file
class JSONScanLogs:
    def __init__(self, filepath="data/logs_db.json"):
        self.filepath = filepath
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _read(self):
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write(self, data):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"DEBUG: Failed to write to JSON db: {e}")

    def insert_one(self, document):
        doc = dict(document)
        if isinstance(doc.get("timestamp"), datetime):
            doc["timestamp"] = doc["timestamp"].isoformat()
        
        data = self._read()
        data.append(doc)
        self._write(data)
        return doc

    def find(self, filter_query=None, projection=None):
        data = self._read()
        try:
            # Parse ISO string back to datetime/formatted string or sort directly
            data.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        except Exception:
            pass
        return data

    def drop(self):
        self._write([])

class MockDb:
    def __init__(self):
        self.scan_logs = JSONScanLogs()

def get_db():
    try:
        # Create a client with a 1.5s timeout for fast fallback
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1500)
        # Force a connection check to verify if the server is actually running
        client.admin.command('ping')
        return client[DB_NAME]
    except (ServerSelectionTimeoutError, ConnectionFailure):
        print("WARNING: MongoDB is offline. Falling back to local JSON database (data/logs_db.json).")
        return MockDb()
    except Exception as e:
        print(f"WARNING: Unexpected error connecting to MongoDB: {e}. Falling back to local JSON database.")
        return MockDb()

def log_scan(file_name: str, pii_found: list, user_id: str = "guest"):
    db = get_db()
    
    # Privacy: Mask the filename so the vault itself doesn't leak PII names
    masked_name = f"SECURE_DOC_{datetime.now().strftime('%H%M%S')}.dat"
    
    log_entry = {
        "file_name": masked_name,
        "original_name_masked": True,
        "pii_types": list(set([p['type'] for p in pii_found])),
        "count": len(pii_found),
        "timestamp": datetime.now(),
        "user_id": user_id
    }
    
    db.scan_logs.insert_one(log_entry)
    print(f"DEBUG: Logged scan for {masked_name}")

def get_logs():
    db = get_db()
    logs = db.scan_logs.find({}, {"_id": 0})
    # Handle slicing and limit manually if mock, limit to 100
    try:
        return list(logs)[:100]
    except Exception:
        return list(logs)

def clear_logs():
    print("DEBUG: Initiating vault wipe...")
    db = get_db()
    db.scan_logs.drop()
    
    # Also clear local file storage for security
    import shutil
    for folder in ["data/uploads", "data/sanitized"]:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                os.makedirs(folder, exist_ok=True)
                print(f"DEBUG: Cleared folder {folder}")
            except Exception as e:
                print(f"DEBUG: Failed to clear {folder}: {e}")
    print("DEBUG: Vault wipe complete.")

