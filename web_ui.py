import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
import time
import base64

# --- MASTER UI CONFIG ---
st.set_page_config(page_title="Gyan Setu AI", page_icon="🎓", layout="centered")

# Persistence of Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CSS (Futuristic Academic Interface) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500&display=swap');
    .stApp { background-color: #0b0e14 !important; }
    h1 { 
        color: #00fbff !important; 
        font-family: 'Orbitron', sans-serif !important; 
        text-align: center !important; 
        font-size: 55px !important; 
        text-shadow: 0 0 25px #00fbff;
        margin-top: -60px;
        letter-spacing: 5px;
    }
    /* Advanced Voice Hub Style */
    button[data-testid="stBaseButton-secondary"] {
        background-color: #00fbff !important;
        color: #0b0e14 !important;
        border-radius: 50% !important;
        width: 140px !important;
        height: 140px !important;
        border: 8px solid #1a202c !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: bold !important;
        margin: 0 auto !important;
        display: flex !important;
        box-shadow: 0 0 45px rgba(0, 251, 255, 0.4) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    button[data-testid="stBaseButton-secondary"]:hover {
        transform: scale(1.1) rotate(5deg);
        box-shadow: 0 0 65px rgba(0, 251, 255, 0.7) !important;
    }
    .chat-container {
        background: #1a202c;
        padding: 30px;
        border-radius: 18px;
        border-left: 8px solid #00fbff;
        color: #e2e8f0;
        margin-top: 25px;
        font-family: 'Rajdhani', sans-serif;
        line-height: 1.8;
        font-size: 22px;
        box-shadow: 10px 10px 30px rgba(0,0,0,0.5);
    }
    .user-box { border-left: 8px solid #ffffff; background: #2d3748; }
    #MainMenu, header, footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display:none;}
    </style>
    """, unsafe_allow_html=True)

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

# Sequential Audio Injection Logic
def trigger_vocal_sync(b64_data):
    """Injects auto-playing audio component without manual controls"""
    audio_html = f"""
        <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64_data}" type="audio/mp3">
        </audio>
    """
    # Using height=0 and scrolling=False to keep UI clean
    st.components.v1.html(audio_html, height=0)

# Input Section (Voice Focused)
input_text = speech_to_text(
    start_prompt="TAP TO SPEAK", 
    stop_prompt="CAPTURING AUDIO...", 
    language='en-IN', 
    use_container_width=True,
    just_once=True, 
    key='gyansetu_v5_sync'
)

if input_text:
    # Display the student's question immediately
    st.markdown(f'<div class="chat-container user-box"><b>Student:</b> {input_text}</div>', unsafe_allow_html=True)
    
    with st.spinner("Gyan Setu is formulating a response..."):
        full_response = ""
        buffer_sentence = ""
        response_container = st.empty()
        
        # Incremental Streaming with Overlap Prevention
        for chunk in aura.ask_stream(input_text, st.session_state.messages):
            if chunk == "||SYNC_SIGNAL||":
                if buffer_sentence.strip():
                    # Generate audio for the completed chunk
                    voice_data = aura.get_audio_data(buffer_sentence.strip())
                    if voice_data:
                        trigger_vocal_sync(voice_data)
                        
                        # OVERLAP PROTECTION LOGIC:
                        # Calculated delay based on sentence length + fixed processing overhead
                        # 0.058 is the 'Sweet Spot' for +15% rate Edge-TTS
                        execution_delay = (len(buffer_sentence) * 0.058) + 0.3
                        time.sleep(execution_delay)
                    
                    buffer_sentence = "" 
            else:
                full_response += chunk
                buffer_sentence += chunk
                # Visual rendering with animated cursor
                response_container.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_response}▒</div>', unsafe_allow_html=True)
        
        # Final cleanup for the visual output
        response_container.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_response}</div>', unsafe_allow_html=True)
        
        # Memory storage for future context
        st.session_state.messages.append({"role": "user", "content": input_text})
        st.session_state.messages.append({"role": "assistant", "content": full_response})
else:
    st.markdown('<p style="text-align:center; color:#555; font-family:Orbitron; margin-top:40px; letter-spacing:2px;">AWAITING COMMAND // STANDBY</p>', unsafe_allow_html=True)
