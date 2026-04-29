import streamlit as st
import time
import base64
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text

# --- 1. PAGE CONFIG & COSMIC UI ---
st.set_page_config(page_title="Gyan Setu AI", page_icon="🎓", layout="centered")

# Custom CSS for the "Gyan Setu" Professional Look
st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: white; }
    .stMarkdown { font-family: 'Inter', sans-serif; }
    .chat-bubble {
        padding: 20px; border-radius: 15px; margin-bottom: 10px;
        border-left: 5px solid #00fbff; background: rgba(255, 255, 255, 0.05);
    }
    .user-bubble {
        border-left: 5px solid #ff00ff; background: rgba(255, 255, 255, 0.02);
    }
    h1 { text-align: center; color: #00fbff; text-shadow: 0px 0px 10px #00fbff; font-size: 3rem; }
    </style>
""", unsafe_allow_html=True)

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

# --- 2. JAVASCRIPT AUDIO ENGINE (The Secret Weapon) ---
# This script creates an 'Audio Queue' in the browser so sounds don't overlap 
# and play immediately as they arrive.
def inject_audio_script():
    js_code = """
    <script>
    if (!window.audioQueue) {
        window.audioQueue = [];
        window.isPlaying = false;
    }

    function playNext() {
        if (window.audioQueue.length > 0 && !window.isPlaying) {
            window.isPlaying = true;
            let audioBase64 = window.audioQueue.shift();
            let audio = new Audio("data:audio/mp3;base64," + audioBase64);
            audio.onended = function() {
                window.isPlaying = false;
                playNext();
            };
            audio.play();
        }
    }

    window.parent.addEventListener('message', function(event) {
        if (event.data.type === 'PLAY_AUDIO') {
            window.audioQueue.push(event.data.data);
            playNext();
        }
    });
    </script>
    """
    st.components.v1.html(js_code, height=0)

inject_audio_script()

def trigger_audio_js(b64_data):
    """Sends audio data to the JavaScript queue without refreshing the UI."""
    js_trigger = f"""
        <script>
        window.parent.postMessage({{type: 'PLAY_AUDIO', data: '{b64_data}'}}, '*');
        </script>
    """
    st.components.v1.html(js_trigger, height=0)

# --- 3. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. VOICE INPUT ---
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    query_voice = speech_to_text(
        start_prompt="🎧 TAP TO ASK GYAN SETU",
        stop_prompt="STOPPING...",
        language='en-IN',
        use_container_width=True,
        key='v12_final'
    )

# --- 5. THE SYNC LOGIC (The Heart) ---
if query_voice:
    # Display User Query
    st.markdown(f'<div class="chat-bubble user-bubble"><b>Student:</b> {query_voice}</div>', unsafe_allow_html=True)
    
    full_response = ""
    sentence_to_speak = ""
    ui_placeholder = st.empty()
    
    # Starting the Engine Stream
    # Logic: Text flows token-by-token, Audio triggers sentence-by-sentence
    for chunk in aura.ask_stream(query_voice, st.session_state.messages):
        
        if chunk == "||SENTENCE_COMPLETE_SIGNAL||":
            if sentence_to_speak.strip():
                # BACKGROUND PROCESS: Fetch audio while text keeps printing
                with st.spinner(""): # Hidden spinner for a second
                    audio_b64 = aura.get_audio_data(sentence_to_speak.strip())
                    if audio_b64:
                        trigger_audio_js(audio_b64)
                sentence_to_speak = "" # Reset buffer for next sentence
        
        else:
            full_response += chunk
            sentence_to_speak += chunk
            # Smooth Typing Effect
            ui_placeholder.markdown(f'<div class="chat-bubble"><b>Gyan Setu:</b> {full_response}▒</div>', unsafe_allow_html=True)
            
            # Intelligent Delay: Adjusts typing speed to feel natural
            if len(chunk) > 1:
                time.sleep(0.02)
            else:
                time.sleep(0.01)

    # Final Save to History
    st.session_state.messages.append({"role": "user", "content": query_voice})
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- 6. FOOTER ---
st.markdown("<br><hr><center><small>Powered by Gyan Setu Engine | Parallel Voice Sync v4.0</small></center>", unsafe_allow_html=True)
