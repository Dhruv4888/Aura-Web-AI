import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
import time
import base64

# --- MASTER ACADEMIC ENGINE CONFIGURATION ---
# Setting up a high-performance centered layout for the mentor interface
st.set_page_config(
    page_title="Gyan Setu AI - Senior Academic Mentor", 
    page_icon="🎓", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Deep State Management: Initializing chat memory for contextual continuity
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- ADVANCED FUTURISTIC UI (THE ORBITRON CORE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    
    /* Deep Space Gradient Background */
    .stApp { 
        background: radial-gradient(circle at 50% 50%, #10141d 0%, #05070a 100%) !important; 
    }
    
    /* Neon Glow Title Styling */
    h1 { 
        color: #00fbff !important; 
        font-family: 'Orbitron', sans-serif !important; 
        text-align: center !important; 
        font-size: 65px !important; 
        text-shadow: 0 0 40px #00fbff, 0 0 15px rgba(0, 251, 255, 0.6);
        margin-top: -85px;
        letter-spacing: 10px;
        text-transform: uppercase;
        font-weight: 900;
    }
    
    /* The Central Neural Voice Hub (Mic Button) */
    button[data-testid="stBaseButton-secondary"] {
        background-color: #00fbff !important;
        color: #0b0e14 !important;
        border-radius: 50% !important;
        width: 170px !important;
        height: 170px !important;
        border: 12px solid #1a202c !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900 !important;
        margin: 40px auto !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        box-shadow: 0 0 60px rgba(0, 251, 255, 0.3) !important;
        transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        cursor: pointer;
        font-size: 18px !important;
    }
    
    button[data-testid="stBaseButton-secondary"]:hover {
        transform: scale(1.15) rotate(-3deg);
        box-shadow: 0 0 90px rgba(0, 251, 255, 0.75) !important;
        border-color: #00fbff !important;
    }
    
    /* Academic Response Container Styling */
    .chat-container {
        background: rgba(26, 32, 44, 0.98);
        padding: 45px;
        border-radius: 30px;
        border-left: 15px solid #00fbff;
        color: #f8fafc;
        margin-top: 40px;
        font-family: 'Rajdhani', sans-serif;
        line-height: 2.1;
        font-size: 28px;
        box-shadow: 25px 25px 60px rgba(0,0,0,0.8);
        border-right: 2px solid rgba(0, 251, 255, 0.15);
        backdrop-filter: blur(15px);
    }
    
    .user-box { 
        border-left: 15px solid #ffffff; 
        background: rgba(45, 55, 72, 0.95); 
        box-shadow: 15px 15px 40px rgba(0,0,0,0.5);
        font-weight: 600;
    }
    
    /* UI Clean-up (Hiding default Streamlit elements) */
    #MainMenu, header, footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display:none;}
    
    /* Custom Scrollbar for Futuristic Feel */
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: #0b0e14; }
    ::-webkit-scrollbar-thumb { background: #00fbff; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

# HIGH-PRECISION AUDIO INJECTION LOGIC
def play_vocal_chunk(b64_data):
    """Injects an isolated auto-playing audio component for granular voice control."""
    audio_markup = f"""
        <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64_data}" type="audio/mp3">
        </audio>
    """
    st.components.v1.html(audio_markup, height=0)

# VOICE ACQUISITION INTERFACE
# This component captures the student's inquiry via microphone.
student_voice = speech_to_text(
    start_prompt="TAP TO SPEAK", 
    stop_prompt="GYAN SETU IS LISTENING...", 
    language='en-IN', 
    use_container_width=True,
    just_once=True, 
    key='gyansetu_core_v9'
)

if student_voice:
    # Immediate visual confirmation of user input
    st.markdown(f'<div class="chat-container user-box"><b>Student:</b> {student_voice}</div>', unsafe_allow_html=True)
    
    with st.spinner("Gyan Setu is analyzing the academic query..."):
        full_response_text = ""
        current_sentence_buffer = ""
        response_render_area = st.empty()
        
        # SEQUENTIAL SYNC LOGIC: Prevents overlapping by hard-locking the loop
        for text_fragment in aura.ask_stream(student_voice, st.session_state.messages):
            if text_fragment == "||SYNC_SIGNAL||":
                if current_sentence_buffer.strip():
                    # Generate high-quality voice data for the current accumulated block
                    vocal_payload = aura.get_audio_data(current_sentence_buffer.strip())
                    
                    if vocal_payload:
                        play_vocal_chunk(vocal_payload)
                        
                        # THE OVERLAP KILLER (Dynamic Time Calibration):
                        # Math equations and symbols require slower vocalization.
                        # Base delay (0.078s per char) + Static overhead (0.75s) for breathing space.
                        # This ensures the browser's audio buffer is empty before the next chunk.
                        char_count = len(current_sentence_buffer)
                        
                        # Extra safety: If symbols like '=', '+', '²' are present, increase delay.
                        symbol_check = any(s in current_sentence_buffer for s in ['=', '+', '-', '*', '/', '²'])
                        base_multiplier = 0.085 if symbol_check else 0.072
                        
                        safe_delay = (char_count * base_multiplier) + 0.75
                        time.sleep(safe_delay)
                    
                    current_sentence_buffer = "" 
            else:
                full_response_text += text_fragment
                current_sentence_buffer += text_fragment
                # Incremental UI rendering with academic typing effect
                response_render_area.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_response_text}▒</div>', unsafe_allow_html=True)
        
        # Final rendering to ensure text stability and remove cursor
        response_render_area.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_response_text}</div>', unsafe_allow_html=True)
        
        # Context Archiving for future reasoning
        st.session_state.messages.append({"role": "user", "content": student_voice})
        st.session_state.messages.append({"role": "assistant", "content": full_response_text})
else:
    # Standby Mode UI
    st.markdown('<p style="text-align:center; color:#556677; font-family:Orbitron; margin-top:70px; font-weight:bold; letter-spacing:4px;">MENTOR READY // AWAITING VOICE INPUT</p>', unsafe_allow_html=True)
