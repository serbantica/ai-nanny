import streamlit as st
import sys
from pathlib import Path
import time
from datetime import datetime

# Add parent directory to path for imports
orchestrator_path = Path(__file__).parent.parent.parent / "ai-companion-orchestrator"
sys.path.insert(0, str(orchestrator_path))
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.device import VirtualDeviceAgent, LEDState, PersonaType
    DEVICE_MODULE_AVAILABLE = True
except ImportError as e:
    DEVICE_MODULE_AVAILABLE = False
    print(f"Device module not available: {e}")

try:
    from services.device_client import DeviceClient
    API_CLIENT_AVAILABLE = True
except ImportError:
    API_CLIENT_AVAILABLE = False

# -----------------------------
# App config
# -----------------------------
st.set_page_config(
    page_title="AI Nanny - Virtual Device",
    page_icon="🧠",
    layout="wide"
)

# -----------------------------
# Session state init
# -----------------------------
if "virtual_device" not in st.session_state and DEVICE_MODULE_AVAILABLE:
    st.session_state.virtual_device = VirtualDeviceAgent(
        device_id="virtual-kitchen-001",
        device_name="Kitchen Speaker",
        location="Kitchen"
    )

if "event_log" not in st.session_state:
    st.session_state.event_log = []

if "assistant_text" not in st.session_state:
    st.session_state.assistant_text = ""

if "led_state" not in st.session_state:
    st.session_state.led_state = "Idle"

if "current_persona" not in st.session_state:
    st.session_state.current_persona = "companion"

if "latency_ms" not in st.session_state:
    st.session_state.latency_ms = 820

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "api_available" not in st.session_state:
    st.session_state.api_available = False

# -----------------------------
# API Client
# -----------------------------
if API_CLIENT_AVAILABLE:
    if "device_client" not in st.session_state:
        st.session_state.device_client = DeviceClient()
        st.session_state.api_available = st.session_state.device_client.check_health()
else:
    st.session_state.api_available = False

# -----------------------------
# Device Interface
# -----------------------------
if DEVICE_MODULE_AVAILABLE:
    device = st.session_state.virtual_device
    
    # Sync session state with device state
    st.session_state.led_state = device.led_state.value
    st.session_state.current_persona = device.current_persona.value
    st.session_state.assistant_text = device.assistant_response
else:
    # Fallback: Use simple class
    class FallbackDevice:
        def __init__(self):
            self.device_name = "Kitchen Speaker"
            self.led_state = st.session_state.led_state
            self.current_persona = st.session_state.current_persona
        
        def listen(self, text):
            return text
        
        def speak(self, text):
            st.session_state.assistant_text = text
        
        def set_led(self, state):
            st.session_state.led_state = state
        
        def switch_persona(self, persona):
            st.session_state.current_persona = persona
        
        def get_status(self):
            return {
                "device_name": self.device_name,
                "is_connected": True,
                "led_state": st.session_state.led_state,
                "current_persona": st.session_state.current_persona
            }
    
    device = FallbackDevice()

# -----------------------------
# Utility
# -----------------------------
def log_event(source, message):
    ts = datetime.now().strftime("%H:%M:%S")
    event_str = f"[{ts}] [{source}] {message}"
    st.session_state.event_log.append(event_str)
    
    # Also log to device if available
    if DEVICE_MODULE_AVAILABLE and hasattr(device, 'log_event'):
        device.log_event(source, "event", message)

def get_llm_response(user_text, persona, device_id="virtual-kitchen-001"):
    """
    Get LLM response - tries real API first, falls back to simulated response
    """
    # Try real API if available
    if st.session_state.api_available and API_CLIENT_AVAILABLE:
        try:
            start_time = time.time()
            result = st.session_state.device_client.generate_response(
                device_id=device_id,
                user_message=user_text,
                persona_id=persona,
                session_id=st.session_state.session_id
            )
            
            # Calculate actual latency
            latency = int((time.time() - start_time) * 1000)
            st.session_state.latency_ms = latency
            
            if not result.get("error"):
                # Update session ID if provided
                if "session_id" in result:
                    st.session_state.session_id = result["session_id"]
                
                return result.get("response", "No response generated.")
            else:
                # API error, fall through to fake response
                if not result.get("fallback"):
                    log_event("API", f"Error: {result.get('response', 'Unknown error')}")
        
        except Exception as e:
            log_event("API", f"Exception: {str(e)}")
    
    # Fallback to simulated responses
    log_event("SYSTEM", "Using simulated response (API not available)")
    responses = {
        "companion": f"I'm here as your companion. You said: '{user_text}'. How else can I help you today?",
        "activity": f"Let's get active! Regarding '{user_text}', I suggest we do some light exercises together.",
        "emergency": f"🚨 Emergency mode: I heard '{user_text}'. Are you okay? Should I call for help?",
        "entertainer": f"Time for fun! About '{user_text}', let me tell you a joke or play some music!",
        "storyteller": f"Once upon a time, someone said '{user_text}'... Let me tell you a story about that.",
        "medication_nurse": f"It's time to check your medication. You mentioned '{user_text}'. Have you taken your pills?"
    }
    return responses.get(persona, f"({persona}) I heard: '{user_text}'. How can I help?")

# -----------------------------
# Layout
# -----------------------------
st.title("🧠 AI Nanny - Virtual Device (Digital Twin)")

# Info banner
status_cols = st.columns([2, 1])
with status_cols[0]:
    if DEVICE_MODULE_AVAILABLE:
        device_status = device.get_status()
        st.info(f"✅ Device: **{device_status['device_name']}** (ID: `{device_status['device_id']}`)")
    else:
        st.warning("⚠️ Running in fallback mode - device module not loaded")

with status_cols[1]:
    if st.session_state.api_available:
        st.success("🌐 API Connected")
    else:
        st.error("🌐 API Offline (using simulation)")

col_left, col_center, col_right = st.columns([1.1, 2.2, 1.4])

# =====================================================
# LEFT PANEL — DEVICE
# =====================================================
with col_left:
    st.markdown("## 🧩 Device Panel")

    st.metric("Device", device.device_name if DEVICE_MODULE_AVAILABLE else "Kitchen Speaker")
    st.text("Type: Raspberry Pi 4")
    st.text("OS: Raspberry Pi OS")
    st.text("Agent: v0.3.1")

    if DEVICE_MODULE_AVAILABLE:
        device_status = device.get_status()
        if device_status['is_connected']:
            st.success("Status: Connected")
        else:
            st.error("Status: Disconnected")
    else:
        st.success("Status: Connected")
    
    st.metric("Latency", f"{st.session_state.latency_ms} ms")

    st.markdown("### 💡 LED State")
    led_options = ["Idle", "Listening", "Speaking", "Thinking", "Error"]
    current_led = st.session_state.led_state
    
    if current_led not in led_options:
        current_led = "Idle"
    
    st.radio(
        "",
        led_options,
        index=led_options.index(current_led),
        disabled=True,
        key="led_display"
    )
    
    # Device info
    if DEVICE_MODULE_AVAILABLE:
        with st.expander("📊 Device Details"):
            st.json(device.get_status())

# =====================================================
# CENTER PANEL — INTERACTION
# =====================================================
with col_center:
    st.markdown("## 🎤 Microphone Input")
    
    mic_mode = st.radio(
        "Input mode",
        ["Text (Simulated STT)", "Audio File (stub)"],
        horizontal=True
    )
    
    user_text = ""
    if mic_mode == "Text (Simulated STT)":
        user_text = st.text_input(
            "Simulated STT Output",
            placeholder="Say something to the device…"
        )
    else:
        st.file_uploader("Upload WAV (not processed in demo)", type=["wav"])
        st.caption("STT pipeline stubbed for demo")

    st.markdown("## 🎭 Persona Buttons (GPIO-equivalent)")
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("🟢 Companion", use_container_width=True):
            if DEVICE_MODULE_AVAILABLE:
                device.switch_persona(PersonaType.COMPANION)
            else:
                device.switch_persona("companion")

    with c2:
        if st.button("🔵 Activity", use_container_width=True):
            if DEVICE_MODULE_AVAILABLE:
                device.switch_persona(PersonaType.ACTIVITY)
            else:
                device.switch_persona("activity")

    with c3:
        if st.button("🔴 Emergency", use_container_width=True):
            if DEVICE_MODULE_AVAILABLE:
                device.switch_persona(PersonaType.EMERGENCY)
            else:
                device.switch_persona("emergency")
    
    # Additional persona buttons
    c4, c5, c6 = st.columns(3)
    
    with c4:
        if st.button("🎭 Entertainer", use_container_width=True):
            if DEVICE_MODULE_AVAILABLE:
                device.switch_persona(PersonaType.ENTERTAINER)
            else:
                device.switch_persona("entertainer")
    
    with c5:
        if st.button("📖 Storyteller", use_container_width=True):
            if DEVICE_MODULE_AVAILABLE:
                device.switch_persona(PersonaType.STORYTELLER)
            else:
                device.switch_persona("storyteller")
    
    with c6:
        if st.button("💊 Med Nurse", use_container_width=True):
            if DEVICE_MODULE_AVAILABLE:
                device.switch_persona(PersonaType.MEDICATION_NURSE)
            else:
                device.switch_persona("medication_nurse")
    
    st.caption(f"Current persona: **{st.session_state.current_persona}**")

    st.markdown("## ▶ Interaction")

    if st.button("Send to Device", type="primary", use_container_width=True) and user_text:
        # Set device to listening state
        if DEVICE_MODULE_AVAILABLE:
            device.set_led(LEDState.LISTENING)
        else:
            device.set_led("Listening")
        
        # Listen to user input
        heard = device.listen(user_text)

        # Simulate LLM request
        log_event("LLM", "request_sent to orchestrator")
        
        if DEVICE_MODULE_AVAILABLE:
            device.set_led(LEDState.THINKING)
        else:
            device.set_led("Thinking")
        
        # Generate response (uses real API if available)
        response = get_llm_response(
            heard,
            st.session_state.current_persona,
            device_id=device.device_id if DEVICE_MODULE_AVAILABLE else "virtual-kitchen-001"
        )
        time.sleep(0.3)

        log_event("LLM", "response_ready")
        
        # Speak response
        device.speak(response)
        
        # Update UI
        st.rerun()

    st.markdown("## 🔊 Speaker Output")
    st.text_area(
        "Assistant says",
        st.session_state.assistant_text,
        height=300,
        disabled=True
    )

    if st.session_state.assistant_text:
        st.caption("Speaking… ▇▇▆▅▃")

# =====================================================
# RIGHT PANEL — SYSTEM
# =====================================================
with col_right:
    st.markdown("## 📡 Event Bus")
    
    # Show events from device if available
    if DEVICE_MODULE_AVAILABLE:
        recent_events = device.get_recent_events(15)
        for evt in recent_events:
            st.code(str(evt), language="log")
    else:
        for evt in st.session_state.event_log[-15:]:
            st.code(evt, language="log")
    
    # Clear events button
    if st.button("🗑️ Clear Events"):
        st.session_state.event_log.clear()
        if DEVICE_MODULE_AVAILABLE:
            device.event_log.clear()
        st.rerun()

    with st.expander("🔧 Hardware Mapping"):
        st.table({
            "Virtual Demo": [
                "Text input",
                "Persona buttons (6)",
                "Audio playback",
                "LED state display",
                "Event logging"
            ],
            "Physical Raspberry Pi": [
                "Mic + STT (Whisper)",
                "GPIO buttons (6 pins)",
                "ALSA speaker + TTS",
                "GPIO RGB LED",
                "Event bus to cloud"
            ]
        })

    with st.expander("📦 Installation (Simulated)"):
        st.code(
            """$ curl https://install.ai-nanny.io | bash
✔ OS detected: Raspberry Pi OS
✔ Audio devices found
✔ Mic: ReSpeaker 2-Mics
✔ Speaker: USB Audio
✔ Registering device...
✔ Device ID: dev-9f23a
✔ Connected to Orchestrator""",
            language="bash"
        )

# -----------------------------
# Footer
# -----------------------------
st.divider()
st.caption(
    "🎯 This dashboard is a **digital twin** of the physical device. "
    "Same orchestration logic, same agent behavior - only I/O is virtualized. "
    "Deploy the same code to a Raspberry Pi for real-world operation."
)

# Architecture info
with st.expander("📐 Architecture Overview"):
    st.markdown("""
    ### Device Agent Architecture
    
    ```
    ┌─────────────────────────────────────┐
    │   Virtual Device (Dashboard)        │
    │  - Simulated STT/TTS                │
    │  - Button interface                 │
    │  - LED state visualization          │
    └──────────────┬──────────────────────┘
                   │
                   ▼
    ┌─────────────────────────────────────┐
    │   Device Agent (Core Module)        │
    │  - Event logging                    │
    │  - Persona management               │
    │  - State tracking                   │
    │  - Abstraction layer                │
    └──────────────┬──────────────────────┘
                   │
                   ▼
    ┌─────────────────────────────────────┐
    │   Physical Device (Raspberry Pi)    │
    │  - Real microphone (STT)            │
    │  - Real speaker (TTS)               │
    │  - GPIO buttons                     │
    │  - RGB LED control                  │
    └─────────────────────────────────────┘
    ```
    
    ### Key Features:
    - ✅ Unified device abstraction
    - ✅ Event-driven architecture
    - ✅ Persona switching (6 personas)
    - ✅ LED state management
    - ✅ Latency tracking
    - ✅ Event bus integration
    
    ### Files Created:
    - `core/device/agent.py` - Device agent implementations
    - `core/device/__init__.py` - Module exports
    """)
