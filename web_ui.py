import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
import time
import base64
import json

# --- MASTER ACADEMIC INTERFACE CONFIGURATION ---
# Setting up a high-performance centered layout for the senior mentor persona.
st.set_page_config(
    page_title="Gyan Setu AI - Senior Academic Mentor", 
    page_icon="🎓", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Deep Session State: Initializing persistent memory for conversational context.
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- EXTENDED FUTURISTIC ACADEMIC CSS (STRICT VISUAL LOGIC) ---
# This section defines the entire visual identity of the Gyan Setu platform.
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    
    /* Global Background: Deep Cosmic Gradient */
    .stApp { 
        background: radial-gradient(circle at 50% 50%, #10141d 0%, #05070a 100%) !important; 
    }
    
    /* Header: Glowing Neon Title with Kinetic Shadow */
    h1 { 
        color: #00fbff !important; 
        font-family: 'Orbitron', sans-serif !important; 
        text-align: center !important; 
        font-size: 65px !important; 
        text-shadow: 0 0 45px #00fbff, 0 0 15px rgba(0, 251, 255, 0.6);
        margin-top: -90px;
        letter-spacing: 12px;
        text-transform: uppercase;
        font-weight: 900;
        animation: glow 3s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { text-shadow: 0 0 20px #00fbff; }
        to { text-shadow: 0 0 50px #00fbff, 0 0 20px #00fbff; }
    }
    
    /* The Vocal Hub (Mic Button): Large, Tactile, and Interactive */
    button[data-testid="stBaseButton-secondary"] {
        background-color: #00fbff !important;
        color: #0b0e14 !important;
        border-radius: 50% !important;
        width: 180px !important;
        height: 180px !important;
        border: 15px solid #1a202c !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900 !important;
        margin: 50px auto !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        box-shadow: 0 0 65px rgba(0, 251, 255, 0.4) !important;
        transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        cursor: pointer;
        font-size: 20px !important;
    }
    
    button[data-testid="stBaseButton-secondary"]:hover {
        transform: scale(1.15) rotate(5deg);
        box-shadow: 0 0 100px rgba(0, 251, 255, 0.8) !important;
        border-color: #ffffff !important;
    }
    
    /* Academic Mentor Chat Container: High Contrast for Readability */
    .chat-container {
        background: rgba(26, 32, 44, 0.98);
        padding: 50px;
        border-radius: 35px;
        border-left: 18px solid #00fbff;
        color: #f8fafc;
        margin-top: 45px;
        font-family: 'Rajdhani', sans-serif;
        line-height: 2.2;
        font-size: 30px;
        box-shadow: 30px 30px 70px rgba(0,0,0,0.8);
        border-right: 3px solid rgba(0, 251, 255, 0.2);
        backdrop-filter: blur(20px);
    }
    
    .user-box { 
        border-left: 18px solid #ffffff; 
        background: rgba(45, 55, 72, 0.98); 
        box-shadow: 15px 15px 45px rgba(0,0,0,0.6);
        font-weight: 700;
    }
    
    /* Tooltip and Interface Cleanup */
    #MainMenu, header, footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display:none;}
    
    /* Advanced Scrollbar Management */
    ::-webkit-scrollbar { width: 12px; }
    ::-webkit-scrollbar-track { background: #0b0e14; }
    ::-webkit-scrollbar-thumb { 
        background: linear-gradient(#00fbff, #005f61); 
        border-radius: 15px; 
    }
    </style>
    """, unsafe_allow_html=True)

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

# --- ADVANCED JS AUDIO SYNC COMPONENT ---
# This function creates an isolated JavaScript event listener for every audio chunk.
# It prevents the next chunk from playing until the current one is finished.
def play_vocal_sync(b64_data, chunk_id):
    """
    Injects an HTML5 audio element with an 'onended' hook.
    This communicates with the browser's audio buffer to ensure zero-overlap.
    """
    audio_sync_html = f"""
        <div id="wrapper-{chunk_id}" style="display:none;">
            <audio id="vocal-engine-{chunk_id}" autoplay="true">
                <source src="data:audio/mp3;base64,{b64_data}" type="audio/mp3">
            </audio>
            <script>
                var player = document.getElementById('vocal-engine-{chunk_id}');
                // Force higher volume and clear playback
                player.volume = 1.0;
                player.onended = function() {{
                    // Send signal to parent window that this chunk is complete
                    window.parent.postMessage({{type: 'vocal_done', id: {chunk_id}}}, '*');
                }};
            </script>
        </div>
    """
    st.components.v1.html(audio_sync_html, height=0)

# --- CORE INTERACTION LOGIC ---
# Capturing high-fidelity voice input from the student.
student_input = speech_to_text(
    start_prompt="TAP TO SPEAK", 
    stop_prompt="GYAN SETU IS ANALYZING...", 
    language='en-IN', 
    use_container_width=True,
    just_once=True, 
    key='gyansetu_v10_ultimate'
)

if student_input:
    # Rendering student's query in the specialized academic box.
    st.markdown(f'<div class="chat-container user-box"><b>Student Inquiry:</b> {student_input}</div>', unsafe_allow_html=True)
    
    with st.spinner("Accessing Mentor Knowledge Base..."):
        full_transcript = ""
        sentence_buffer = ""
        visual_render_area = st.empty()
        vocal_chunk_index = 0
        
        # STREAMING EXECUTION WITH VOCAL ISOLATION
        for response_chunk in aura.ask_stream(student_input, st.session_state.messages):
            if response_chunk == "||SYNC_SIGNAL||":
                if sentence_buffer.strip():
                    vocal_chunk_index += 1
                    
                    # Generate audio bytes for the current logical step or equation part.
                    voice_b64 = aura.get_audio_data(sentence_buffer.strip())
                    
                    if voice_b64:
                        # Playing the audio with the JS-controlled isolation layer.
                        play_vocal_sync(voice_b64, vocal_chunk_index)
                        
                        # ANTI-OVERLAP CALIBRATION (THE SAFETY LOCK)
                        # We calculate a hard delay based on phonetic complexity.
                        # Equations require 30% more time than standard prose.
                        math_chars = ['=', '+', '-', 'x', '/', '²', '³', '(', ')']
                        is_math = any(char in sentence_buffer for char in math_chars)
                        
                        # Precision Timing Multiplier
                        # Standard: 0.082s per char | Math: 0.115s per char
                        multiplier = 0.115 if is_math else 0.082
                        
                        # Calculated Wait + 0.9s Static Buffer for "OnEnded" signal breathing room.
                        safety_wait = (len(sentence_buffer) * multiplier) + 0.9
                        time.sleep(safety_wait)
                    
                    sentence_buffer = "" 
            else:
                full_transcript += response_chunk
                sentence_buffer += response_chunk
                # Real-time visual feedback with a specialized academic cursor.
                visual_render_area.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_transcript}▒</div>', unsafe_allow_html=True)
        
        # Finalization of the response area.
        visual_render_area.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_transcript}</div>', unsafe_allow_html=True)
        
        # Archiving interaction in session memory.
        st.session_state.messages.append({"role": "user", "content": student_input})
        st.session_state.messages.append({"role": "assistant", "content": full_transcript})

else:
    # Standby Interface for Academic Mentor.
    st.markdown("""
        <div style="text-align:center; margin-top:60px;">
            <p style="color:#475569; font-family:Orbitron; font-weight:bold; letter-spacing:5px; font-size:18px;">
                SYSTEM: ACTIVE // STATUS: READY
            </p>
            <p style="color:#2d3748; font-family:Rajdhani; font-size:22px;">
                Standing by for academic inquiry...
            </p>
        </div>
    """, unsafe_allow_html=True)

# --- END OF GYAN SETU CORE UI ---
