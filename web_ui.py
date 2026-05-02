import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
import asyncio
import re

# --- GLOBAL CONFIGURATION ---
st.set_page_config(
    page_title="Gyan Setu AI - Final Sync", 
    page_icon="🎓", 
    layout="centered"
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- THE ORBITRON UI (STRICT INTEGRITY) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Rajdhani:wght@500;700&display=swap');
    .stApp { background: radial-gradient(circle at center, #0f172a 0%, #020617 100%) !important; }
    h1 { 
        color: #00fbff !important; font-family: 'Orbitron', sans-serif !important; 
        text-align: center !important; font-size: 65px !important; 
        text-shadow: 0 0 40px #00fbff; margin-top: -85px; letter-spacing: 12px;
    }
    .chat-container {
        background: rgba(15, 23, 42, 0.95); padding: 45px; border-radius: 30px;
        border-left: 15px solid #00fbff; color: #f1f5f9; font-family: 'Rajdhani';
        font-size: 26px; line-height: 1.8; margin-top: 30px;
    }
    .user-box { border-left: 15px solid #ffffff; background: rgba(30, 41, 59, 0.95); }
    #MainMenu, header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

def inject_audio_script(b64_data, chunk_id):
    """Direct DOM injection for immediate playback."""
    audio_markup = f"""
        <div id="vocal-{chunk_id}" style="display:none;">
            <audio id="aud-{chunk_id}" autoplay="true">
                <source src="data:audio/mp3;base64,{b64_data}" type="audio/mp3">
            </audio>
        </div>
    """
    st.components.v1.html(audio_markup, height=0)

async def audio_queue_manager(text_block, counter):
    """
    The Final Guard: Fetches audio and waits for its duration 
    before allowing the next one. NO OVERLAP.
    """
    vocal_hex, duration = await aura.generate_voice_async(text_block)
    if vocal_hex:
        inject_audio_script(vocal_hex, counter)
        # Is waqt tak wait karo jab tak audio khatam na ho jaye
        await asyncio.sleep(duration)

async def process_interaction(query):
    full_transcription = ""
    chunk_buffer = ""
    ui_anchor = st.empty()
    audio_counter = 0
    
    # Text aur Audio Tasks ka parallel management
    audio_tasks = []

    async for alphabet in aura.ask_stream(query, st.session_state.messages):
        if alphabet == "||SYNC_SIGNAL||":
            if chunk_buffer.strip():
                audio_counter += 1
                # Task ko queue mein dalo (Sequential execution via await inside)
                task = asyncio.create_task(audio_queue_manager(chunk_buffer.strip(), audio_counter))
                audio_tasks.append(task)
                chunk_buffer = ""
        else:
            full_transcription += alphabet
            chunk_buffer += alphabet
            # Instant typing render
            ui_anchor.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_transcription}▒</div>', unsafe_allow_html=True)
            await asyncio.sleep(0.001) 

    # Final cleanup of typing UI
    ui_anchor.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_transcription}</div>', unsafe_allow_html=True)
    
    # Wait for all background audio tasks to finish before ending session
    if audio_tasks:
        await asyncio.gather(*audio_tasks)
        
    st.session_state.messages.append({"role": "user", "content": query})
    st.session_state.messages.append({"role": "assistant", "content": full_transcription})

# --- EXECUTION ---
query_voice = speech_to_text(
    start_prompt="TAP TO SPEAK", stop_prompt="PROCESSING...", 
    language='en-IN', use_container_width=True, just_once=True, key='v15_final_push'
)

if query_voice:
    st.markdown(f'<div class="chat-container user-box"><b>Student:</b> {query_voice}</div>', unsafe_allow_html=True)
    asyncio.run(process_interaction(query_voice))
else:
    st.markdown('<div style="text-align:center; color:#00fbff; font-family:Orbitron; margin-top:50px;">READY FOR SESSION</div>', unsafe_allow_html=True)
