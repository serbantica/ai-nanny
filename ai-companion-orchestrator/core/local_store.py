import json
import os
from datetime import datetime
from typing import List, Dict, Any

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
KNOWLEDGE_FILE = os.path.join(DATA_DIR, "knowledge.json")
ACTIVITY_FILE = os.path.join(DATA_DIR, "activity.json")
DEVICES_FILE = os.path.join(DATA_DIR, "devices.json")

class LocalStore:
    """Simple JSON-based local storage for persistence without DB."""
    
    @staticmethod
    def _load(filepath: str, default: Any = None) -> Any:
        if not os.path.exists(filepath):
            return default if default is not None else []
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return default if default is not None else []

    @staticmethod
    def _save(filepath: str, data: Any):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    # --- Knowledge Base ---
    @classmethod
    def add_document(cls, doc_metadata: Dict):
        docs = cls._load(KNOWLEDGE_FILE)
        docs.insert(0, doc_metadata)
        cls._save(KNOWLEDGE_FILE, docs)
        
        # Auto-log activity
        cls.log_activity({
            "type": "Knowledge Import",
            "description": f"Ingested {doc_metadata.get('filename')} ({doc_metadata.get('category')})",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        })

    @classmethod
    def get_documents(cls) -> List[Dict]:
        return cls._load(KNOWLEDGE_FILE)

    # --- Activity Log ---
    @classmethod
    def log_activity(cls, activity: Dict):
        logs = cls._load(ACTIVITY_FILE)
        if "timestamp" not in activity:
            activity["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        logs.insert(0, activity)
        cls._save(ACTIVITY_FILE, logs[:100]) # Keep last 100

    @classmethod
    def get_activities(cls) -> List[Dict]:
        return cls._load(ACTIVITY_FILE)

    # --- Devices (Mock Redis replacement for easy setup) ---
    @classmethod
    def save_device(cls, device_data: Dict):
        devices = cls._load(DEVICES_FILE, default=[])
        # Update existing or append
        existing_idx = next((i for i, d in enumerate(devices) if d['id'] == device_data['id']), -1)
        if existing_idx >= 0:
            devices[existing_idx] = device_data
        else:
            devices.append(device_data)
        cls._save(DEVICES_FILE, devices)
        
        # Log only on new registration? No, simpler to let caller handle logging
        
    @classmethod
    def list_devices(cls) -> List[Dict]:
        return cls._load(DEVICES_FILE, default=[])
