import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
import time
import base64

# --- ACADEMIC CORE CONFIG ---
st.set_page_config(page_title="Gyan Setu AI", page_icon="🎓", layout="centered")

# State Management for Session Continuity
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CSS (High-Performance Scientific Interface) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;600&display=swap');
    .stApp { background-color: #0b0e14 !important; }
    h1 { 
        color: #00fbff !important; 
        font-family: 'Orbitron', sans-serif !important; 
        text-align: center !important; 
        font-size: 55px !important; 
        text-shadow: 0 0 30px #00fbff;
        margin-top: -70px;
        letter-spacing: 6px;
    }
    /* Voice Interface Hub */
    button[data-testid="stBaseButton-secondary"] {
        background-color: #00fbff !important;
        color: #0b0e14 !important;
        border-radius: 50% !important;
        width: 150px !important;
        height: 150px !important;
        border: 10px solid #1a202c !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: bold !important;
        margin: 0 auto !important;
        display: flex !important;
        box-shadow: 0 0 50px rgba(0, 251, 255, 0.4) !important;
        transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.3s ease;
    }
    button[data-testid="stBaseButton-secondary"]:hover {
        transform: scale(1.08);
        box-shadow: 0 0 70px rgba(0, 251, 255, 0.6) !important;
    }
    .chat-container {
        background: #1a202c;
        padding: 35px;
        border-radius: 20px;
        border-left: 10px solid #00fbff;
        color: #f8fafc;
        margin-top: 30px;
        font-family: 'Rajdhani', sans-serif;
        line-height: 1.9;
        font-size: 24px;
        box-shadow: 15px 15px 40px rgba(0,0,0,0.6);
    }
    .user-box { border-left: 10px solid #cbd5e1; background: #2d3748; }
    #MainMenu, header, footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display:none;}
    </style>
    """, unsafe_allow_html=True)

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

def play_vocal_output(b64_data):
    """Injects a hidden audio component that plays once per sentence trigger."""
    audio_tag = f"""
        <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64_data}" type="audio/mp3">
        </audio>
    """
    st.components.v1.html(audio_tag, height=0)

# Main Interaction Entry Point
captured_speech = speech_to_text(
    start_prompt="TAP TO SPEAK", 
    stop_prompt="ANALYZING VOICE...", 
    language='en-IN', 
    use_container_width=True,
    just_once=True, 
    key='gyansetu_master_v7'
)

if captured_speech:
    # Display the student's prompt with distinct formatting
    st.markdown(f'<div class="chat-container user-box"><b>Student:</b> {captured_speech}</div>', unsafe_allow_html=True)
    
    with st.spinner("Gyan Setu is processing your academic query..."):
        full_text_stream = ""
        sentence_accumulator = ""
        display_box = st.empty()
        
        # Execute streaming logic with integrated vocal synchronization
        for fragment in aura.ask_stream(captured_speech, st.session_state.messages):
            if fragment == "||SYNC_SIGNAL||":
                if sentence_accumulator.strip():
                    # Generate and trigger audio for the current block
                    voice_b64 = aura.get_audio_data(sentence_accumulator.strip())
                    if voice_b64:
                        play_vocal_output(voice_b64)
                        
                        # ADVANCED SYNC PROTECTION:
                        # Character-length based delay optimized for +15% TTS speed.
                        # Added 0.45s static overhead to prevent overlaps on math symbols.
                        vocal_delay = (len(sentence_accumulator) * 0.062) + 0.45
                        time.sleep(vocal_delay)
                    
                    sentence_accumulator = "" 
            else:
                full_text_stream += fragment
                sentence_accumulator += fragment
                # Dynamic visual rendering with an active cursor effect
                display_box.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_text_stream}█</div>', unsafe_allow_html=True)
        
        # Final render to remove the cursor and stabilize output
        display_box.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_text_stream}</div>', unsafe_allow_html=True)
        
        # Persistence: Updating the session state for historical context
        st.session_state.messages.append({"role": "user", "content": captured_speech})
        st.session_state.messages.append({"role": "assistant", "content": full_text_stream})
else:
    st.markdown('<p style="text-align:center; color:#64748b; font-family:Orbitron; margin-top:50px; font-weight:bold;">// AWAITING STUDENT INPUT //</p>', unsafe_allow_html=True)
