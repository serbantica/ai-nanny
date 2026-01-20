#!/usr/bin/env python3
import json

devices = [
  # Facility A (grp_001) - Main Facility
  {
    "id": "dev_fa_kitchen_001",
    "name": "Kitchen Assistant",
    "type": "smart_speaker",
    "group_id": "grp_001",
    "location": "Kitchen - Wing A",
    "status": "online",
    "capabilities": {
      "audio_input": True,
      "audio_output": True,
      "buttons": False,
      "leds": True,
      "display": False,
      "camera": False
    },
    "active_persona_id": "companion",
    "last_heartbeat": "2026-01-20T10:30:00",
    "metadata": {"floor": "1", "wing": "A"},
    "registered_at": "2026-01-20T08:00:00"
  },
  {
    "id": "dev_fa_bedroom_101",
    "name": "Room 101 Tablet",
    "type": "tablet",
    "group_id": "grp_001",
    "location": "Bedroom 101",
    "status": "online",
    "capabilities": {
      "audio_input": True,
      "audio_output": True,
      "buttons": True,
      "leds": False,
      "display": True,
      "camera": True
    },
    "active_persona_id": "medication_nurse",
    "last_heartbeat": "2026-01-20T10:28:00",
    "metadata": {"floor": "1", "wing": "A", "room_number": "101"},
    "registered_at": "2026-01-20T08:15:00"
  },
  {
    "id": "dev_fa_living_room_001",
    "name": "Common Area Speaker",
    "type": "smart_speaker",
    "group_id": "grp_001",
    "location": "Common Living Room",
    "status": "online",
    "capabilities": {
      "audio_input": True,
      "audio_output": True,
      "buttons": False,
      "leds": True,
      "display": False,
      "camera": False
    },
    "active_persona_id": "entertainer",
    "last_heartbeat": "2026-01-20T10:29:00",
    "metadata": {"floor": "1", "wing": "A"},
    "registered_at": "2026-01-20T08:30:00"
  },
  {
    "id": "dev_fa_bedroom_102",
    "name": "Room 102 Pi Hub",
    "type": "raspberry_pi",
    "group_id": "grp_001",
    "location": "Bedroom 102",
    "status": "online",
    "capabilities": {
      "audio_input": True,
      "audio_output": True,
      "buttons": True,
      "leds": True,
      "display": False,
      "camera": True
    },
    "active_persona_id": "companion",
    "last_heartbeat": "2026-01-20T10:25:00",
    "metadata": {"floor": "1", "wing": "A", "room_number": "102"},
    "registered_at": "2026-01-20T09:00:00"
  },
  {
    "id": "dev_fa_hallway_001",
    "name": "Hallway Monitor",
    "type": "tablet",
    "group_id": "grp_001",
    "location": "Main Hallway",
    "status": "offline",
    "capabilities": {
      "audio_input": False,
      "audio_output": True,
      "buttons": True,
      "leds": False,
      "display": True,
      "camera": False
    },
    "active_persona_id": None,
    "last_heartbeat": "2026-01-20T09:15:00",
    "metadata": {"floor": "1", "wing": "A"},
    "registered_at": "2026-01-20T08:45:00"
  },
  
  # Facility B (grp_002) - Secondary Site
  {
    "id": "dev_fb_reception_001",
    "name": "Reception Tablet",
    "type": "tablet",
    "group_id": "grp_002",
    "location": "Reception Desk",
    "status": "online",
    "capabilities": {
      "audio_input": True,
      "audio_output": True,
      "buttons": True,
      "leds": False,
      "display": True,
      "camera": True
    },
    "active_persona_id": "companion",
    "last_heartbeat": "2026-01-20T10:32:00",
    "metadata": {"floor": "Ground", "area": "Reception"},
    "registered_at": "2026-01-19T14:00:00"
  },
  {
    "id": "dev_fb_dining_001",
    "name": "Dining Room Assistant",
    "type": "smart_speaker",
    "group_id": "grp_002",
    "location": "Dining Hall",
    "status": "online",
    "capabilities": {
      "audio_input": True,
      "audio_output": True,
      "buttons": False,
      "leds": True,
      "display": False,
      "camera": False
    },
    "active_persona_id": "entertainer",
    "last_heartbeat": "2026-01-20T10:27:00",
    "metadata": {"floor": "Ground", "area": "Dining"},
    "registered_at": "2026-01-19T14:15:00"
  },
  {
    "id": "dev_fb_bedroom_201",
    "name": "Room 201 Pi Station",
    "type": "raspberry_pi",
    "group_id": "grp_002",
    "location": "Bedroom 201",
    "status": "busy",
    "capabilities": {
      "audio_input": True,
      "audio_output": True,
      "buttons": True,
      "leds": True,
      "display": False,
      "camera": True
    },
    "active_persona_id": "storyteller",
    "last_heartbeat": "2026-01-20T10:31:00",
    "metadata": {"floor": "2", "wing": "B", "room_number": "201"},
    "registered_at": "2026-01-19T15:00:00"
  },
  {
    "id": "dev_fb_bedroom_202",
    "name": "Room 202 Tablet",
    "type": "tablet",
    "group_id": "grp_002",
    "location": "Bedroom 202",
    "status": "online",
    "capabilities": {
      "audio_input": True,
      "audio_output": True,
      "buttons": True,
      "leds": False,
      "display": True,
      "camera": False
    },
    "active_persona_id": None,
    "last_heartbeat": "2026-01-20T10:24:00",
    "metadata": {"floor": "2", "wing": "B", "room_number": "202"},
    "registered_at": "2026-01-19T15:30:00"
  },
  {
    "id": "dev_fb_garden_001",
    "name": "Garden Patio Speaker",
    "type": "smart_speaker",
    "group_id": "grp_002",
    "location": "Garden Patio",
    "status": "offline",
    "capabilities": {
      "audio_input": True,
      "audio_output": True,
      "buttons": False,
      "leds": True,
      "display": False,
      "camera": False
    },
    "active_persona_id": None,
    "last_heartbeat": "2026-01-20T08:00:00",
    "metadata": {"floor": "Ground", "area": "Outdoor"},
    "registered_at": "2026-01-19T16:00:00"
  },
  
  # Test Lab (grp_003)
  {
    "id": "dev_lab_test_001",
    "name": "Test Device Alpha",
    "type": "simulator",
    "group_id": "grp_003",
    "location": "Development Lab",
    "status": "online",
    "capabilities": {
      "audio_input": True,
      "audio_output": True,
      "buttons": True,
      "leds": True,
      "display": True,
      "camera": True
    },
    "active_persona_id": "companion",
    "last_heartbeat": "2026-01-20T10:33:00",
    "metadata": {"environment": "test", "version": "1.0.0"},
    "registered_at": "2026-01-20T07:00:00"
  },
  {
    "id": "dev_lab_test_002",
    "name": "Test Device Beta",
    "type": "simulator",
    "group_id": "grp_003",
    "location": "Development Lab",
    "status": "online",
    "capabilities": {
      "audio_input": True,
      "audio_output": True,
      "buttons": True,
      "leds": True,
      "display": True,
      "camera": True
    },
    "active_persona_id": "medication_nurse",
    "last_heartbeat": "2026-01-20T10:33:00",
    "metadata": {"environment": "test", "version": "1.0.1"},
    "registered_at": "2026-01-20T07:15:00"
  },
  {
    "id": "dev_lab_custom_001",
    "name": "Custom Hardware Prototype",
    "type": "custom",
    "group_id": "grp_003",
    "location": "Hardware Lab",
    "status": "error",
    "capabilities": {
      "audio_input": True,
      "audio_output": True,
      "buttons": True,
      "leds": True,
      "display": True,
      "camera": True
    },
    "active_persona_id": None,
    "last_heartbeat": "2026-01-20T09:45:00",
    "metadata": {"environment": "test", "prototype": True, "error": "Connection timeout"},
    "registered_at": "2026-01-20T07:30:00"
  }
]

filepath = "/Users/serbantica/Library/CloudStorage/OneDrive-IBM/GitHub/AI-Nanny-Project/ai-nanny/ai-companion-orchestrator/data/devices.json"
with open(filepath, "w") as f:
    json.dump(devices, f, indent=2)

print(f"Successfully created {filepath} with {len(devices)} devices")
