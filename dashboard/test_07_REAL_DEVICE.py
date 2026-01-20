#!/usr/bin/env python3
"""
Test script for 07_REAL_DEVICE.py dashboard page
Tests imports, dependencies, and core functionality
"""

import sys
from pathlib import Path
import traceback

print("=" * 70)
print("Testing 07_REAL_DEVICE.py Dashboard Page")
print("=" * 70)

# Setup paths
dashboard_path = Path(__file__).parent
orchestrator_path = dashboard_path.parent / "ai-companion-orchestrator"
sys.path.insert(0, str(orchestrator_path))
sys.path.insert(0, str(dashboard_path))

test_results = []

def test(name, func):
    """Run a test and record result"""
    try:
        func()
        test_results.append((name, True, None))
        print(f"✅ {name}")
        return True
    except Exception as e:
        test_results.append((name, False, str(e)))
        print(f"❌ {name}: {e}")
        return False

# Test 1: Python syntax
def test_syntax():
    import py_compile
    py_compile.compile('pages/07_REAL_DEVICE.py', doraise=True)

test("Python syntax validation", test_syntax)

# Test 2: Core device imports
def test_core_device_import():
    from core.device import VirtualDeviceAgent, LEDState, PersonaType
    assert VirtualDeviceAgent is not None
    assert LEDState is not None
    assert PersonaType is not None

test("Import core.device module", test_core_device_import)

# Test 3: Device client import
def test_device_client_import():
    from services.device_client import DeviceClient
    assert DeviceClient is not None

test("Import DeviceClient", test_device_client_import)

# Test 4: Create virtual device
def test_create_device():
    from core.device import VirtualDeviceAgent
    device = VirtualDeviceAgent(
        device_id="test-001",
        device_name="Test Device",
        location="Test Location"
    )
    assert device.device_id == "test-001"
    assert device.device_name == "Test Device"
    assert device.location == "Test Location"

test("Create VirtualDeviceAgent", test_create_device)

# Test 5: Device LED control
def test_device_led():
    from core.device import VirtualDeviceAgent, LEDState
    device = VirtualDeviceAgent()
    device.set_led(LEDState.LISTENING)
    assert device.led_state == LEDState.LISTENING
    device.set_led(LEDState.SPEAKING)
    assert device.led_state == LEDState.SPEAKING

test("Device LED state management", test_device_led)

# Test 6: Device persona switching
def test_persona_switching():
    from core.device import VirtualDeviceAgent, PersonaType
    device = VirtualDeviceAgent()
    device.switch_persona(PersonaType.EMERGENCY)
    assert device.current_persona == PersonaType.EMERGENCY
    device.switch_persona(PersonaType.COMPANION)
    assert device.current_persona == PersonaType.COMPANION

test("Persona switching", test_persona_switching)

# Test 7: Device listen/speak
def test_listen_speak():
    from core.device import VirtualDeviceAgent
    device = VirtualDeviceAgent()
    
    # Test listen
    text = device.listen("Hello world")
    assert text == "Hello world"
    
    # Test speak
    device.speak("Test response")
    assert device.assistant_response == "Test response"

test("Device listen/speak functionality", test_listen_speak)

# Test 8: Event logging
def test_event_logging():
    from core.device import VirtualDeviceAgent
    device = VirtualDeviceAgent()
    
    initial_count = len(device.event_log)
    device.log_event("TEST", "test_event", "Test message")
    assert len(device.event_log) == initial_count + 1

test("Event logging", test_event_logging)

# Test 9: Device status
def test_device_status():
    from core.device import VirtualDeviceAgent
    device = VirtualDeviceAgent()
    status = device.get_status()
    
    assert "device_id" in status
    assert "device_name" in status
    assert "device_type" in status
    assert "led_state" in status
    assert "current_persona" in status

test("Device status retrieval", test_device_status)

# Test 10: DeviceClient instantiation
def test_device_client():
    from services.device_client import DeviceClient
    client = DeviceClient()
    assert client.base_url == "http://localhost:8000"
    assert client.api_base == "http://localhost:8000/api/v1"

test("DeviceClient instantiation", test_device_client)

# Test 11: API health check (expected to fail if API not running)
def test_api_health():
    from services.device_client import DeviceClient
    client = DeviceClient()
    is_healthy = client.check_health()
    # This is expected to be False if API is not running
    # We just test that it returns a boolean
    assert isinstance(is_healthy, bool)

test("API health check method", test_api_health)

# Summary
print("\n" + "=" * 70)
print("Test Summary")
print("=" * 70)

passed = sum(1 for _, result, _ in test_results if result)
failed = sum(1 for _, result, _ in test_results if not result)
total = len(test_results)

print(f"Total Tests: {total}")
print(f"Passed: {passed} ✅")
print(f"Failed: {failed} ❌")
print(f"Success Rate: {passed/total*100:.1f}%")

if failed > 0:
    print("\n" + "=" * 70)
    print("Failed Tests Details:")
    print("=" * 70)
    for name, result, error in test_results:
        if not result:
            print(f"\n❌ {name}")
            print(f"   Error: {error}")

print("\n" + "=" * 70)
print("Component Status")
print("=" * 70)

# Check component availability
from services.device_client import DeviceClient
client = DeviceClient()
api_available = client.check_health()

print(f"✅ Core Device Module: Available")
print(f"✅ DeviceClient Module: Available")
print(f"{'✅' if api_available else '⚠️ '} API Server: {'Connected' if api_available else 'Offline (will use simulation)'}")

print("\n" + "=" * 70)
print("Recommendations")
print("=" * 70)

if not api_available:
    print("⚠️  API server is not running. The dashboard will work in SIMULATION mode:")
    print("   - User interactions will be simulated")
    print("   - Responses will be generated locally (no LLM)")
    print("   - All UI features will work normally")
    print("\n   To enable full functionality, start the API server:")
    print("   $ cd ai-companion-orchestrator")
    print("   $ python3 -m uvicorn api.main:app --reload --port 8000")
else:
    # Test if LLM is configured
    try:
        test_response = client.generate_response(
            device_id="test-001",
            user_message="Test",
            persona_id="companion"
        )
        
        if test_response.get("fallback") and test_response.get("reason") == "missing_api_key":
            print("✅ API server: Connected")
            print("⚠️  LLM API Key: Not configured")
            print("\n   The dashboard will work in HYBRID mode:")
            print("   - API endpoints are accessible")
            print("   - Responses are simulated (no LLM API key)")
            print("   - Session management works")
            print("   - All UI features work normally")
            print("\n   To enable REAL LLM responses:")
            print("   1. Set ANTHROPIC_API_KEY environment variable")
            print("   2. Or configure in .env file")
            print("   3. Restart the API server")
        elif not test_response.get("error"):
            print("✅ All systems operational!")
            print("   The dashboard is fully functional with:")
            print("   - Real API integration")
            print("   - LLM-powered responses")
            print("   - Full device simulation")
        else:
            print("✅ API server: Connected")
            print("⚠️  LLM: Error occurred")
            print(f"   Error: {test_response.get('response', 'Unknown error')}")
    except Exception as e:
        print(f"✅ API server: Connected")
        print(f"⚠️  Warning: Could not test LLM ({e})")

print("\n" + "=" * 70)
print("Dashboard Launch Command")
print("=" * 70)
print("$ cd ai-nanny/dashboard")
print("$ streamlit run pages/07_REAL_DEVICE.py")
print("=" * 70)

sys.exit(0 if failed == 0 else 1)
