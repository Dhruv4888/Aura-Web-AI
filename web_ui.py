import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
import time
import base64

# --- UI CONFIG ---
st.set_page_config(page_title="Gyan Setu AI", page_icon="🎓", layout="centered")

# Session state initialize
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CSS (High-End Orbitron Theme) ---
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
    /* Mic Button Styling */
    button[data-testid="stBaseButton-secondary"] {
        background-color: #00fbff !important;
        color: #0b0e14 !important;
        border-radius: 50% !important;
        width: 150px !important;
        height: 150px !important;
        border: 6px solid #1a202c !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: bold !important;
        margin: 0 auto !important;
        display: flex !important;
        box-shadow: 0 0 40px rgba(0, 251, 255, 0.3) !important;
        transition: 0.3s ease-in-out;
    }
    button[data-testid="stBaseButton-secondary"]:hover {
        transform: scale(1.05);
        box-shadow: 0 0 60px rgba(0, 251, 255, 0.6) !important;
    }
    .chat-container {
        background: #1a202c;
        padding: 25px;
        border-radius: 12px;
        border-left: 6px solid #00fbff;
        color: #e2e8f0;
        margin-top: 25px;
        font-family: 'Rajdhani', sans-serif;
        line-height: 1.7;
        font-size: 20px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.3);
    }
    .user-box { border-left: 6px solid #ffffff; background: #2d3748; }
    #MainMenu, header, footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display:none;}
    </style>
    """, unsafe_allow_html=True)

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

# Audio feedback engine (Invisible)
def play_audio(b64_data):
    audio_html = f"""
        <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64_data}" type="audio/mp3">
        </audio>
    """
    st.components.v1.html(audio_html, height=0)

# Input Section
text = speech_to_text(
    start_prompt="TAP TO SPEAK", 
    stop_prompt="RECORDING...", 
    language='en-IN', 
    use_container_width=True,
    just_once=True, 
    key='gyansetu_main_mic'
)

if text:
    st.markdown(f'<div class="chat-container user-box"><b>Student:</b> {text}</div>', unsafe_allow_html=True)
    
    with st.spinner("Processing Knowledge..."):
        full_display_text = ""
        current_sentence = ""
        container = st.empty()
        
        # Generator for streaming
        for chunk in aura.ask_stream(text, st.session_state.messages):
            if chunk == "||SYNC_SIGNAL||":
                if current_sentence.strip():
                    # Fast Audio Generation
                    audio_b64 = aura.get_audio_data(current_sentence.strip())
                    if audio_b64:
                        play_audio(audio_b64)
                        
                        # Dynamic Delay Logic: Words per minute basis
                        # Audio speed is +15%, so 0.05s per character is ideal for sync
                        delay = len(current_sentence) * 0.052 
                        time.sleep(delay)
                    
                    current_sentence = "" 
            else:
                full_display_text += chunk
                current_sentence += chunk
                # Visual cursor effect for smooth rendering
                container.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_display_text}█</div>', unsafe_allow_html=True)
        
        # Final display update
        container.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_display_text}</div>', unsafe_allow_html=True)
        
        # Store context
        st.session_state.messages.append({"role": "user", "content": text})
        st.session_state.messages.append({"role": "assistant", "content": full_display_text})
else:
    st.markdown('<p style="text-align:center; color:#4a5568; font-family:Orbitron; margin-top:30px;">SYSTEM READY // AWAITING VOICE INPUT</p>', unsafe_allow_html=True)
