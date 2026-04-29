import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
import time
import base64
import re

# --- MASTER ACADEMIC INTERFACE CONFIGURATION ---
# Setting up the foundation for the Class 1-12 Global Mentor Platform.
st.set_page_config(
    page_title="Gyan Setu AI - Global Academic Mentor", 
    page_icon="🎓", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Deep Session State: Managing memory for complex subject derivations.
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- ULTIMATE FUTURISTIC ACADEMIC CSS (THE CORE V12) ---
# This CSS ensures the UI remains professional for all 1-12 grade subjects.
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    
    /* Global Cosmic Backdrop */
    .stApp { 
        background: radial-gradient(circle at center, #0f172a 0%, #020617 100%) !important; 
    }
    
    /* Kinetic Neon Header */
    h1 { 
        color: #00fbff !important; 
        font-family: 'Orbitron', sans-serif !important; 
        text-align: center !important; 
        font-size: 68px !important; 
        text-shadow: 0 0 45px #00fbff, 0 0 15px rgba(0, 251, 255, 0.6);
        margin-top: -95px;
        letter-spacing: 15px;
        text-transform: uppercase;
        font-weight: 900;
        animation: neon-pulse 2.5s ease-in-out infinite alternate;
    }
    
    @keyframes neon-pulse {
        from { opacity: 0.8; text-shadow: 0 0 20px #00fbff; }
        to { opacity: 1; text-shadow: 0 0 50px #00fbff, 0 0 25px #00fbff; }
    }
    
    /* The Neural Voice Hub: High-Response Mic Button */
    button[data-testid="stBaseButton-secondary"] {
        background-color: #00fbff !important;
        color: #0b0e14 !important;
        border-radius: 50% !important;
        width: 185px !important;
        height: 185px !important;
        border: 18px solid #1e293b !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900 !important;
        margin: 55px auto !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        box-shadow: 0 0 75px rgba(0, 251, 255, 0.4) !important;
        transition: all 0.7s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        cursor: pointer;
    }
    
    button[data-testid="stBaseButton-secondary"]:hover {
        transform: scale(1.12) rotate(3deg);
        box-shadow: 0 0 110px rgba(0, 251, 255, 0.85) !important;
        border-color: #ffffff !important;
    }
    
    /* Academic Output Container: Logic-First Design */
    .chat-container {
        background: rgba(15, 23, 42, 0.98);
        padding: 55px;
        border-radius: 40px;
        border-left: 22px solid #00fbff;
        color: #f1f5f9;
        margin-top: 50px;
        font-family: 'Rajdhani', sans-serif;
        line-height: 2.3;
        font-size: 32px;
        box-shadow: 35px 35px 90px rgba(0,0,0,0.9);
        border-right: 3px solid rgba(0, 251, 255, 0.15);
        backdrop-filter: blur(30px);
    }
    
    .user-box { 
        border-left: 22px solid #ffffff; 
        background: rgba(30, 41, 59, 0.98); 
        box-shadow: 20px 20px 60px rgba(0,0,0,0.6);
        font-weight: 700;
    }
    
    /* Precision UI Overrides */
    #MainMenu, header, footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display:none;}
    
    /* The Scholar Scrollbar */
    ::-webkit-scrollbar { width: 14px; }
    ::-webkit-scrollbar-track { background: #020617; }
    ::-webkit-scrollbar-thumb { 
        background: linear-gradient(#00fbff, #004d4f); 
        border-radius: 12px; 
        border: 3px solid #020617;
    }
    </style>
    """, unsafe_allow_html=True)

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

# --- THE VOCAL ISOLATION PROTOCOL ---
# This logic ensures each audio chunk is played in a strictly controlled environment.
def play_sync_audio(b64_data, chunk_id):
    """
    Injects an HTML5 audio instance with unique IDs to prevent 
    browser-level mixing of overlapping voices.
    """
    audio_tag = f"""
        <div id="vocal-wrapper-{chunk_id}" style="display:none;">
            <audio id="vocal-player-{chunk_id}" autoplay="true">
                <source src="data:audio/mp3;base64,{b64_data}" type="audio/mp3">
            </audio>
            <script>
                var player = document.getElementById('vocal-player-{chunk_id}');
                player.playbackRate = 1.0; 
                // Ensure browser doesn't stack audio
                player.onplay = function() {{ console.log('Playing chunk {chunk_id}'); }};
            </script>
        </div>
    """
    st.components.v1.html(audio_tag, height=0)

# (Next Hissa isme Logic aur Interaction handle karega...)
# --- CORE ACADEMIC INTERACTION HUB ---
# capturing high-fidelity student voice input for Class 1-12 curriculum analysis.
student_voice_input = speech_to_text(
    start_prompt="START ACADEMIC INQUIRY", 
    stop_prompt="GYAN SETU IS ANALYZING...", 
    language='en-IN', 
    use_container_width=True,
    just_once=True, 
    key='gyan_setu_v12_final_lock'
)

if student_voice_input:
    # Rendering the student's question with distinct mentor-grade styling.
    st.markdown(f'<div class="chat-container user-box"><b>Student:</b> {student_voice_input}</div>', unsafe_allow_html=True)
    
    with st.spinner("Synthesizing Subject Matter Expertise..."):
        full_academic_response = ""
        current_sentence_buffer = ""
        response_render_target = st.empty()
        vocal_sequence_id = 0
        
        # THE SYNC GATE: Iterating through the AI Mentor's stream.
        # This loop is designed to prevent 'Voice Stacking' by blocking the next yield 
        # until the current audio is theoretically finished.
        for response_fragment in aura.ask_stream(student_voice_input, st.session_state.messages):
            if response_fragment == "||SYNC_SIGNAL||":
                if current_sentence_buffer.strip():
                    vocal_sequence_id += 1
                    
                    # Converting the current logical block into high-fidelity vocal data.
                    # This could be a math step, a history date, or a science law.
                    audio_payload_b64 = aura.get_audio_data(current_sentence_buffer.strip())
                    
                    if audio_payload_b64:
                        # Executing the vocal isolation injection from Part 1.
                        play_sync_audio(audio_payload_b64, vocal_sequence_id)
                        
                        # --- THE ULTIMATE ANTI-OVERLAP CALCULATION (BLOCKING LOGIC) ---
                        # 1. Base Multiplier: 0.088s per character (Calculated for Gyan Setu's +8% rate).
                        # 2. Math/Physics Penalty: Equations have high 'phonetic weight'.
                        # 3. History/Theory Buffer: Narrative pauses require extra time.
                        
                        math_symbols = ['=', '+', '-', 'x', '/', '²', '³', '(', ')', '^']
                        symbol_count = sum(1 for char in current_sentence_buffer if char in math_symbols)
                        
                        # If symbols are present, the AI is likely solving an equation.
                        # We increase the multiplier to 0.125s for math steps.
                        dynamic_multiplier = 0.125 if symbol_count > 0 else 0.088
                        
                        # Extra breathing room for every complex symbol (0.35s per symbol).
                        symbol_overhead = symbol_count * 0.35
                        
                        # The "Hard-Lock" Duration: 
                        # (Length * Speed) + Math Overhead + 1.2s Static Browser Buffer.
                        # We use 1.2s as the minimum safety gap between any two sentences.
                        lock_duration = (len(current_sentence_buffer) * dynamic_multiplier) + symbol_overhead + 1.2
                        
                        # CRITICAL: This line stops the entire Python thread. 
                        # It forces the system to WAIT until the user has heard the full sentence.
                        time.sleep(lock_duration)
                    
                    # Resetting buffer for the next logical sentence or math step.
                    current_sentence_buffer = "" 
            else:
                full_academic_response += response_fragment
                current_sentence_buffer += response_fragment
                
                # Real-time UI rendering with a scholarly typing cursor.
                response_render_target.markdown(
                    f'<div class="chat-container"><b>Gyan Setu:</b> {full_academic_response}▒</div>', 
                    unsafe_allow_html=True
                )
        
        # Finalization: Removing the cursor and stabilizing the output box.
        response_render_target.markdown(
            f'<div class="chat-container"><b>Gyan Setu:</b> {full_academic_response}</div>', 
            unsafe_allow_html=True
        )
        
        # Subject Context Archiving: Storing interaction for Class 1-12 curriculum continuity.
        st.session_state.messages.append({"role": "user", "content": student_voice_input})
        st.session_state.messages.append({"role": "assistant", "content": full_academic_response})

else:
    # STANDBY INTERFACE: Displayed when the mentor is awaiting input.
    st.markdown("""
        <div style="text-align:center; padding:70px; border: 2px dashed rgba(0, 251, 255, 0.2); border-radius: 30px; margin-top: 50px;">
            <div style="color:#00fbff; font-family:Orbitron; letter-spacing:6px; font-weight:900; font-size:22px; text-shadow: 0 0 10px #00fbff;">
                ACADEMIC MENTOR: ONLINE
            </div>
            <div style="color:#94a3b8; font-family:Rajdhani; font-size:24px; margin-top:15px; font-weight:500;">
                Math • Physics • Chemistry • History • Science (Class 1-12)
            </div>
            <p style="color:#475569; font-family:Rajdhani; font-size:18px; margin-top:10px;">
                Ready to explain concepts in English or Hindi.
            </p>
        </div>
    """, unsafe_allow_html=True)

# --- END OF GYAN SETU V12 ULTIMATE WEB_UI ---
