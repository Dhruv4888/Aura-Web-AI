import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
import time
import base64

# --- MASTER ACADEMIC CONFIGURATION ---
st.set_page_config(
    page_title="Gyan Setu AI - Mentor", 
    page_icon="🎓", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Deep Session Memory for Chat Continuity
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- HIGH-END FUTURISTIC CSS (EXTENDED) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;600;700&display=swap');
    
    /* Main Background with Deep Tech Theme */
    .stApp { 
        background: radial-gradient(circle at center, #10141d 0%, #0b0e14 100%) !important; 
    }
    
    /* Glowing Title Styling */
    h1 { 
        color: #00fbff !important; 
        font-family: 'Orbitron', sans-serif !important; 
        text-align: center !important; 
        font-size: 60px !important; 
        text-shadow: 0 0 35px #00fbff, 0 0 10px rgba(0, 251, 255, 0.5);
        margin-top: -80px;
        letter-spacing: 8px;
        text-transform: uppercase;
    }
    
    /* Advanced Mic Hub Button Customization */
    button[data-testid="stBaseButton-secondary"] {
        background-color: #00fbff !important;
        color: #0b0e14 !important;
        border-radius: 50% !important;
        width: 160px !important;
        height: 160px !important;
        border: 12px solid #1a202c !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900 !important;
        margin: 0 auto !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        box-shadow: 0 0 55px rgba(0, 251, 255, 0.35) !important;
        transition: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        cursor: pointer;
    }
    
    button[data-testid="stBaseButton-secondary"]:hover {
        transform: scale(1.1) rotate(3deg);
        box-shadow: 0 0 85px rgba(0, 251, 255, 0.6) !important;
        border-color: #00fbff !important;
    }
    
    /* Professional Chat Container Styling */
    .chat-container {
        background: rgba(26, 32, 44, 0.95);
        padding: 40px;
        border-radius: 25px;
        border-left: 12px solid #00fbff;
        color: #f1f5f9;
        margin-top: 35px;
        font-family: 'Rajdhani', sans-serif;
        line-height: 1.95;
        font-size: 26px;
        box-shadow: 20px 20px 50px rgba(0,0,0,0.7);
        border-right: 1px solid rgba(0, 251, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .user-box { 
        border-left: 12px solid #e2e8f0; 
        background: rgba(45, 55, 72, 0.9); 
        box-shadow: 10px 10px 30px rgba(0,0,0,0.4);
    }
    
    /* Clean UI Overrides */
    #MainMenu, header, footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display:none;}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0b0e14; }
    ::-webkit-scrollbar-thumb { background: #00fbff; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

# Functional Audio Trigger Component
def execute_voice_block(b64_data):
    """Generates an isolated HTML audio instance to prevent parallel execution."""
    audio_markup = f"""
        <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64_data}" type="audio/mp3">
        </audio>
    """
    st.components.v1.html(audio_markup, height=0)

# Voice Input Interface
voice_query = speech_to_text(
    start_prompt="TAP TO SPEAK", 
    stop_prompt="GYAN SETU IS LISTENING...", 
    language='en-IN', 
    use_container_width=True,
    just_once=True, 
    key='gyansetu_v8_final'
)

if voice_query:
    # Displaying user query with academic mentor formatting
    st.markdown(f'<div class="chat-container user-box"><b>Student:</b> {voice_query}</div>', unsafe_allow_html=True)
    
    with st.spinner("Processing Knowledge Base..."):
        full_transcript = ""
        current_sentence_chunk = ""
        ui_renderer = st.empty()
        
        # Real-time Stream Handling with Hard-Sync Logic
        for response_chunk in aura.ask_stream(voice_query, st.session_state.messages):
            if response_chunk == "||SYNC_SIGNAL||":
                if current_sentence_chunk.strip():
                    # Process current chunk into vocal output
                    voice_payload = aura.get_audio_data(current_sentence_chunk.strip())
                    if voice_payload:
                        execute_voice_block(voice_payload)
                        
                        # ANTI-OVERLAP CALIBRATION:
                        # Character length (len) * delay (0.075) + extra 0.6s buffer for math symbols
                        # This ensures the browser has cleared the audio buffer before the next play.
                        vocal_duration_buffer = (len(current_sentence_chunk) * 0.075) + 0.6
                        time.sleep(vocal_duration_buffer)
                    
                    current_sentence_chunk = "" 
            else:
                full_transcript += response_chunk
                current_sentence_chunk += response_chunk
                # UI rendering with futuristic typing indicator
                ui_renderer.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_transcript}▒</div>', unsafe_allow_html=True)
        
        # Final UI update for clarity
        ui_renderer.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_transcript}</div>', unsafe_allow_html=True)
        
        # State archival
        st.session_state.messages.append({"role": "user", "content": voice_query})
        st.session_state.messages.append({"role": "assistant", "content": full_transcript})
else:
    st.markdown('<p style="text-align:center; color:#475569; font-family:Orbitron; margin-top:60px; font-weight:bold; letter-spacing:3px;">SYSTEM ACTIVE // STANDBY FOR INSTRUCTION</p>', unsafe_allow_html=True)
