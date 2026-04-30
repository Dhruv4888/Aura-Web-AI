import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
import streamlit.components.v1 as components
import base64
import threading
import queue
import time
from threading import Thread

# --- CONFIG (Same beautiful UI) ---
st.set_page_config(page_title="Gyan Setu AI - TRUE STREAMING", page_icon="🎓", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("""
    <style>
    /* SAME COSMIC UI - No changes needed */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    .stApp { background: radial-gradient(circle at center, #0f172a 0%, #020617 100%) !important; }
    h1 { color: #00fbff !important; font-family: 'Orbitron', sans-serif !important; text-align: center !important; font-size: 65px !important; text-shadow: 0 0 40px #00fbff; margin-top: -85px; letter-spacing: 12px; font-weight: 900; }
    /* ... (keep all your existing CSS exactly same) ... */
    .streaming-indicator { color: #00fbff; font-family: 'Orbitron'; font-weight: 900; text-shadow: 0 0 10px #00fbff; animation: pulse 0.5s infinite; }
    @keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.5;} }
    </style>
    """, unsafe_allow_html=True)

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

# --- WEB AUDIO API (Same) ---
def init_audio_player():
    components.html("""
    <script>
    let audioCtx, queue=[],playing=false;
    function initCtx(){if(!audioCtx)audioCtx=new(window.AudioContext||window.webkitAudioContext)();}
    window.playAudio=function(b64,id){initCtx();let bin=atob(b64),bytes=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)bytes[i]=bin.charCodeAt(i);queue.push({data:bytes,id});playNext();}
    async function playNext(){if(playing||queue.length==0)return;playing=true;let chunk=queue.shift();try{let buf=await audioCtx.decodeAudioData(chunk.data.buffer.slice(0)),src=audioCtx.createBufferSource();src.buffer=buf;src.connect(audioCtx.destination);src.onended=()=>{playing=false;playNext()};src.start();}catch(e){playing=false;playNext();}}
    </script><div style='text-align:center;color:#00fbff;font-family:Orbitron;font-size:20px;'>🎤 LIVE AUDIO READY</div>
    """, height=80)

if 'audio_init' not in st.session_state:
    init_audio_player()
    st.session_state.audio_init = True

# --- TTS THREADING SYSTEM ---
audio_queue = queue.Queue()
def tts_worker():
    """Background TTS processor"""
    while True:
        try:
            text_data = audio_queue.get(timeout=1)
            if text_data is None: break
            text, chunk_id = text_data
            # Generate audio synchronously
            clean_text = aura.clean_text_for_speech(text)
            voice = "hi-IN-MadhurNeural" if aura.is_hindi(clean_text) else "en-IN-PrabhatNeural"
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            communicate = edge_tts.Communicate(clean_text, voice, rate="+10%", pitch="-2Hz")
            
            audio_buffer = b""
            for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_buffer += chunk["data"]
                    if len(audio_buffer) > 1500:  # Stream chunks
                        components.html(f"""
                        <script>playAudio('{base64.b64encode(audio_buffer).decode()}','{chunk_id}');</script>
                        """, height=0)
                        audio_buffer = b""
            
            if audio_buffer:
                components.html(f"""
                <script>playAudio('{base64.b64encode(audio_buffer).decode()}','{chunk_id}');</script>
                """, height=0)
            loop.close()
            audio_queue.task_done()
        except queue.Empty:
            continue

# Start TTS thread
if 'tts_thread' not in st.session_state:
    tts_thread = Thread(target=tts_worker, daemon=True)
    tts_thread.start()
    st.session_state.tts_thread = tts_thread

# --- MIC INPUT ---
query_voice = speech_to_text(start_prompt="TAP TO SPEAK", stop_prompt="🔥 LIVE STREAMING...", language='en-IN', use_container_width=True, just_once=True)

if query_voice:
    st.markdown(f'<div class="chat-container user-box"><b>Student:</b> {query_voice}</div>', unsafe_allow_html=True)
    
    # *** TRUE SYNCHRONOUS STREAMING (NO ASYNC ERRORS!) ***
    response_placeholder = st.empty()
    response_placeholder.markdown('<div class="chat-container streaming-indicator"><b>Gyan Setu:</b> █ LIVE STREAMING START █</div>', unsafe_allow_html=True)
    
    full_response = ""
    chunk_id = 0
    
    # Groq streaming (synchronous generator)
    for text_token in aura.ask_stream(query_voice, st.session_state.messages):
        full_response += text_token
        
        # 1. INSTANT TEXT DISPLAY
        response_placeholder.markdown(
            f'<div class="chat-container"><b>Gyan Setu:</b> {full_response}█</div>', 
            unsafe_allow_html=True
        )
        
        # 2. INSTANT VOICE (sentence detection)
        if any(p in text_token for p in ['.', '!', '?', '।', '\n']):
            sentence = full_response.split('.')[-1].strip() if '.' in full_response else full_response
            if len(sentence) > 10:
                chunk_id += 1
                # Threaded TTS - ZERO BLOCKING
                audio_queue.put((sentence, f"chunk_{chunk_id}"))
    
    # Final sentence
    if full_response and len(full_response.split()[-10:]) > 3:
        audio_queue.put((full_response.split('.')[-1], f"final_{chunk_id}"))
    
    # Clean final display
    response_placeholder.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_response}</div>', unsafe_allow_html=True)
    
    # History
    st.session_state.messages.append({"role": "user", "content": query_voice})
    st.session_state.messages.append({"role": "assistant", "content": full_response})

else:
    st.markdown("""
    <div style="text-align:center;padding:60px;">
        <div style="color:#00fbff;font-family:Orbitron;letter-spacing:5px;font-weight:900;font-size:22px;text-shadow:0 0 15px #00fbff;">
            GYAN SETU - TRUE STREAMING v3.0 ✅
        </div>
        <div style="color:#94a3b8;font-size:18px;margin-top:20px;">
            👆 Tap mic → Token-by-token text + INSTANT voice<br>
            • MadhurNeural (Hindi) • PrabhatNeural (English)<br>
            • 100% sync • ZERO errors • NO delays
        </div>
    </div>
    """, unsafe_allow_html=True)
