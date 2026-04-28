import streamlit as st
import streamlit.components.v1 as components
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
import time

# --- UI CONFIG ---
st.set_page_config(page_title="Gyan Setu AI", page_icon="🎓", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CSS (Bigger Code, Full Length) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #0b0e14 !important; }
    h1 { 
        color: #00fbff !important; 
        font-family: 'Orbitron', sans-serif !important; 
        text-align: center !important; 
        font-size: 50px !important; 
        text-shadow: 0 0 20px #00fbff;
        margin-top: -50px;
    }
    button[data-testid="stBaseButton-secondary"] {
        background-color: #00fbff !important;
        color: #0b0e14 !important;
        border-radius: 100px !important;
        width: 180px !important;
        height: 180px !important;
        border: 8px solid #1a202c !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: bold !important;
        display: block !important;
        margin: 0 auto !important;
        box-shadow: 0 0 30px rgba(0, 251, 255, 0.4) !important;
    }
    .chat-container {
        background: #1a202c;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #00fbff;
        color: white;
        margin-top: 20px;
        font-family: 'Arial', sans-serif;
        line-height: 1.6;
        font-size: 18px;
    }
    .user-box { border-left: 5px solid #ffffff; background: #2d3748; }
    #MainMenu, header, footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display:none;}
    </style>
    """, unsafe_allow_html=True)

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

# --- JAVASCRIPT AUDIO QUEUE ENGINE ---
# Ye script browser mein ek baar load hogi aur overlap ko control karegi
def inject_audio_queue_script():
    js_engine = """
    <script>
    if (!window.audioQueue) {
        window.audioQueue = [];
        window.isAudioPlaying = false;
        console.log("Audio Queue Engine Initialized");
    }

    function playNextInQueue() {
        if (window.audioQueue.length === 0) {
            window.isAudioPlaying = false;
            return;
        }

        window.isAudioPlaying = true;
        let base64Data = window.audioQueue.shift();
        let audio = new Audio("data:audio/mp3;base64," + base64Data);
        
        audio.onended = function() {
            playNextInQueue();
        };

        audio.play().catch(e => {
            console.log("Audio play error:", e);
            playNextInQueue();
        });
    }

    window.addToQueue = function(base64Data) {
        window.audioQueue.push(base64Data);
        if (!window.isAudioPlaying) {
            playNextInQueue();
        }
    }
    </script>
    """
    components.html(js_engine, height=0, width=0)

# Always keep the script active
inject_audio_queue_script()

def trigger_voice_in_queue(base64_data):
    # Base64 ko JavaScript function mein pass karna
    unique_key = f"voice_{time.time()}"
    js_trigger = f"""
    <script>
        if (window.addToQueue) {{
            window.addToQueue("{base64_data}");
        }}
    </script>
    """
    components.html(js_trigger, height=0, width=0)

# --- MAIN APP LOGIC ---
text = speech_to_text(
    start_prompt="TAP TO ASK", 
    stop_prompt="LISTENING...", 
    language='en-IN', 
    use_container_width=True,
    just_once=True, 
    key='gyansetu_mic'
)

if text:
    st.markdown(f'<div class="chat-container user-box"><b>Student:</b> {text}</div>', unsafe_allow_html=True)
    
    with st.spinner("Gyan Setu is analyzing..."):
        full_display_text = ""
        current_sentence = ""
        container = st.empty()
        
        # AI Se chunks nikalna
        for chunk in aura.ask_stream(text, st.session_state.messages):
            if chunk == "||SYNC_SIGNAL||":
                # Ek sentence poora hua, ab iska audio background mein generate karke queue mein daalo
                if current_sentence.strip():
                    audio_b64 = aura.get_audio_data(current_sentence.strip())
                    if audio_b64:
                        trigger_voice_in_queue(audio_b64)
                    current_sentence = "" # Reset buffer for next sentence
            else:
                full_display_text += chunk
                current_sentence += chunk
                # Live rendering in UI
                container.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_display_text}▌</div>', unsafe_allow_html=True)
        
        # Final render
        container.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_display_text}</div>', unsafe_allow_html=True)
        
        # Memory Update
        st.session_state.messages.append({"role": "user", "content": text})
        st.session_state.messages.append({"role": "assistant", "content": full_display_text})
else:
    st.markdown('<p style="text-align:center; color:#555; margin-top:20px;">Ready for your academic questions...</p>', unsafe_allow_html=True)
