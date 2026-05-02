import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
import asyncio
import re

# --- GLOBAL ACADEMIC ENGINE CONFIGURATION ---
st.set_page_config(
    page_title="Gyan Setu AI - Global Academic Mentor", 
    page_icon="🎓", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- THE FUTURISTIC ORBITRON INTERFACE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    .stApp { background: radial-gradient(circle at center, #0f172a 0%, #020617 100%) !important; }
    h1 { 
        color: #00fbff !important; font-family: 'Orbitron', sans-serif !important; 
        text-align: center !important; font-size: 65px !important; 
        text-shadow: 0 0 40px #00fbff, 0 0 15px rgba(0, 251, 255, 0.4);
        margin-top: -85px; letter-spacing: 12px; text-transform: uppercase; font-weight: 900;
    }
    button[data-testid="stBaseButton-secondary"] {
        background-color: #00fbff !important; color: #0b0e14 !important;
        border-radius: 50% !important; width: 175px !important; height: 175px !important;
        border: 15px solid #1e293b !important; font-family: 'Orbitron', sans-serif !important;
        font-weight: 900 !important; margin: 45px auto !important;
        display: flex !important; justify-content: center !important; align-items: center !important;
        box-shadow: 0 0 70px rgba(0, 251, 255, 0.3) !important;
        transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    }
    .chat-container {
        background: rgba(15, 23, 42, 0.95); padding: 50px; border-radius: 35px;
        border-left: 20px solid #00fbff; color: #f1f5f9; margin-top: 40px;
        font-family: 'Rajdhani', sans-serif; line-height: 2.1; font-size: 28px;
        box-shadow: 30px 30px 80px rgba(0,0,0,0.8); backdrop-filter: blur(25px);
    }
    .user-box { border-left: 20px solid #ffffff; background: rgba(30, 41, 59, 0.95); }
    #MainMenu, header, footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display:none;}
    </style>
    """, unsafe_allow_html=True)

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

def inject_isolated_audio(b64_data, chunk_id):
    audio_markup = f"""
        <div id="vocal-unit-{chunk_id}" style="display:none;">
            <audio id="audio-core-{chunk_id}" autoplay="true">
                <source src="data:audio/mp3;base64,{b64_data}" type="audio/mp3">
            </audio>
        </div>
    """
    st.components.v1.html(audio_markup, height=0)

async def play_audio_task(text_block, counter):
    """Background audio processing."""
    vocal_hex = await aura.generate_voice_async(text_block)
    if vocal_hex:
        inject_isolated_audio(vocal_hex, counter)

async def process_interaction(query):
    full_transcription = ""
    chunk_buffer = ""
    ui_anchor = st.empty()
    audio_counter = 0
    
    # CRITICAL FIX: 'async for' for asynchronous generators
    async for alphabet in aura.ask_stream(query, st.session_state.messages):
        if alphabet == "||SYNC_SIGNAL||":
            if chunk_buffer.strip():
                audio_counter += 1
                # Triggering background audio task
                asyncio.create_task(play_audio_task(chunk_buffer.strip(), audio_counter))
                chunk_buffer = ""
        else:
            full_transcription += alphabet
            chunk_buffer += alphabet
            ui_anchor.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_transcription}▒</div>', unsafe_allow_html=True)
            await asyncio.sleep(0.005) # Yield for UI update

    ui_anchor.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_transcription}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": query})
    st.session_state.messages.append({"role": "assistant", "content": full_transcription})

# --- UI INPUT ---
query_voice = speech_to_text(
    start_prompt="TAP TO SPEAK", stop_prompt="GYAN SETU IS PROCESSING...", 
    language='en-IN', use_container_width=True, just_once=True, key='v14_final_sync'
)

if query_voice:
    st.markdown(f'<div class="chat-container user-box"><b>Student:</b> {query_voice}</div>', unsafe_allow_html=True)
    with st.spinner("Analyzing..."):
        # This handles the top-level async execution
        asyncio.run(process_interaction(query_voice))
else:
    st.markdown("""
        <div style="text-align:center; padding:60px;">
            <div style="color:#00fbff; font-family:Orbitron; letter-spacing:5px; font-weight:900; font-size:22px;">
                SYSTEM ONLINE: GYAN SETU
            </div>
        </div>
    """, unsafe_allow_html=True)
