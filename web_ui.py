import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
import time
import base64
import re

# --- GLOBAL ACADEMIC ENGINE CONFIGURATION ---
# Setting up the high-authority mentor workspace for Class 1-12.
st.set_page_config(
    page_title="Gyan Setu AI - Global Academic Mentor", 
    page_icon="🎓", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Persistent Session Memory: Ensures the AI remembers the flow of complex derivations.
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- THE FUTURISTIC ORBITRON INTERFACE (UI INTEGRITY) ---
# Keeping the UI exactly as per your preference with the deep cosmic aesthetic.
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    
    /* Deep Cosmic Aesthetic */
    .stApp { 
        background: radial-gradient(circle at center, #0f172a 0%, #020617 100%) !important; 
    }
    
    /* Neon Title Design */
    h1 { 
        color: #00fbff !important; 
        font-family: 'Orbitron', sans-serif !important; 
        text-align: center !important; 
        font-size: 65px !important; 
        text-shadow: 0 0 40px #00fbff, 0 0 15px rgba(0, 251, 255, 0.5);
        margin-top: -85px;
        letter-spacing: 12px;
        text-transform: uppercase;
        font-weight: 900;
    }
    
    /* The Central Audio-Visual Hub (Mic Button) */
    button[data-testid="stBaseButton-secondary"] {
        background-color: #00fbff !important;
        color: #0b0e14 !important;
        border-radius: 50% !important;
        width: 175px !important;
        height: 175px !important;
        border: 15px solid #1e293b !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900 !important;
        margin: 45px auto !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        box-shadow: 0 0 70px rgba(0, 251, 255, 0.35) !important;
        transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        cursor: pointer;
    }
    
    button[data-testid="stBaseButton-secondary"]:hover {
        transform: scale(1.1) rotate(-2deg);
        box-shadow: 0 0 100px rgba(0, 251, 255, 0.8) !important;
        border-color: #ffffff !important;
    }
    
    /* Mentor Output Box: High Readability for All Subjects */
    .chat-container {
        background: rgba(15, 23, 42, 0.95);
        padding: 50px;
        border-radius: 35px;
        border-left: 20px solid #00fbff;
        color: #f1f5f9;
        margin-top: 40px;
        font-family: 'Rajdhani', sans-serif;
        line-height: 2.1;
        font-size: 28px;
        box-shadow: 30px 30px 80px rgba(0,0,0,0.85);
        border-right: 2px solid rgba(0, 251, 255, 0.1);
        backdrop-filter: blur(25px);
    }
    
    .user-box { 
        border-left: 20px solid #ffffff; 
        background: rgba(30, 41, 59, 0.95); 
        box-shadow: 15px 15px 50px rgba(0,0,0,0.6);
    }
    
    /* Minimalist Cleanup */
    #MainMenu, header, footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display:none;}
    
    /* Smooth Scrollbar */
    ::-webkit-scrollbar { width: 12px; }
    ::-webkit-scrollbar-track { background: #020617; }
    ::-webkit-scrollbar-thumb { 
        background: linear-gradient(#00fbff, #005f61); 
        border-radius: 10px; 
    }
    </style>
    """, unsafe_allow_html=True)

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

# --- THE BLOCKING SYNC MECHANISM ---
# This function handles the injection and execution of voice chunks.
def inject_isolated_audio(b64_data, chunk_id):
    """
    Directly injects the audio data into the DOM.
    Each chunk is assigned a unique ID to prevent overlap at the browser layer.
    """
    audio_markup = f"""
        <div id="vocal-unit-{chunk_id}" style="display:none;">
            <audio id="audio-core-{chunk_id}" autoplay="true">
                <source src="data:audio/mp3;base64,{b64_data}" type="audio/mp3">
            </audio>
        </div>
    """
    st.components.v1.html(audio_markup, height=0)

# --- GLOBAL VOICE ACQUISITION ---
# Capturing the student's voice input with English/Hindi support.
query_voice = speech_to_text(
    start_prompt="START ACADEMIC SESSION", 
    stop_prompt="GYAN SETU IS PROCESSING...", 
    language='en-IN', 
    use_container_width=True,
    just_once=True, 
    key='core_engine_v12_final'
)

if query_voice:
    # Render user query with bold mentor styling.
    st.markdown(f'<div class="chat-container user-box"><b>Student:</b> {query_voice}</div>', unsafe_allow_html=True)
    
    with st.spinner("Synthesizing solution..."):
        full_transcription = ""
        chunk_buffer = ""
        ui_anchor = st.empty()
        audio_counter = 0
        
        # LOGIC GATE: Processing the mentor's concise and fast stream.
        for text_fragment in aura.ask_stream(query_voice, st.session_state.messages):
            if text_fragment == "||SYNC_SIGNAL||":
                if chunk_buffer.strip():
                    audio_counter += 1
                    
                    # Convert the current concise step into vocal data.
                    vocal_hex = aura.get_audio_data(chunk_buffer.strip())
                    
                    if vocal_hex:
                        inject_isolated_audio(vocal_hex, audio_counter)
                        
                        # --- ENHANCED DYNAMIC SYNC LOGIC ---
                        # Calculating phonological weight for all Class 1-12 subjects.
                        
                        # Detect math symbols for specialized timing
                        math_symbols = re.findall(r'[0-9\+\-\=\^\/x²³\(\)]', chunk_buffer)
                        complexity_score = len(math_symbols)
                        text_length = len(chunk_buffer)
                        
                        # Multiplier adjustment for +10% rate in engine
                        # Standard char speed: 0.082s. Math symbol speed: 0.3s.
                        timing_multiplier = 0.082
                        extra_symbol_pause = complexity_score * 0.30
                        
                        # FINAL BLOCKING CALCULATION:
                        # (Chars * Speed) + (Math Overhead) + Buffer (1.0s for fast processing)
                        # Reduced from 1.1s to 1.0s for the new faster engine.
                        calculated_wait = (text_length * timing_multiplier) + extra_symbol_pause + 1.0
                        
                        # Execution Pause: Locks the next chunk until current is spoken.
                        time.sleep(calculated_wait)
                    
                    chunk_buffer = "" 
            else:
                full_transcription += text_fragment
                chunk_buffer += text_fragment
                # Scholarly typing effect for visual engagement.
                ui_anchor.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_transcription}▒</div>', unsafe_allow_html=True)
        
        # UI Stabilization: Cleaning up the final response.
        ui_anchor.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_transcription}</div>', unsafe_allow_html=True)
        
        # Update session history for contextual continuity.
        st.session_state.messages.append({"role": "user", "content": query_voice})
        st.session_state.messages.append({"role": "assistant", "content": full_transcription})

else:
    # Standby Interface: Welcoming the student to the platform.
    st.markdown("""
        <div style="text-align:center; padding:60px;">
            <div style="color:#00fbff; font-family:Orbitron; letter-spacing:5px; font-weight:900; font-size:22px; text-shadow: 0 0 15px rgba(0, 251, 255, 0.4);">
                SYSTEM ONLINE: GYAN SETU
            </div>
            <div style="color:#94a3b8; font-family:Rajdhani; font-size:20px; margin-top:10px;">
                Ready for Class 1-12 Academic Mentorship
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- END OF V12 MASTER UI ---
