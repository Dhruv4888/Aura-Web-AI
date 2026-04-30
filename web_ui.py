import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
import asyncio
import streamlit.components.v1 as components
import base64
import json
import time

# --- GLOBAL ACADEMIC ENGINE CONFIGURATION ---
st.set_page_config(
    page_title="Gyan Setu AI - Global Academic Mentor", 
    page_icon="🎓", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Persistent Session Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    
    .stApp { 
        background: radial-gradient(circle at center, #0f172a 0%, #020617 100%) !important; 
    }
    
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
    
    #MainMenu, header, footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display:none;}
    
    ::-webkit-scrollbar { width: 12px; }
    ::-webkit-scrollbar-track { background: #020617; }
    ::-webkit-scrollbar-thumb { 
        background: linear-gradient(#00fbff, #005f61); 
        border-radius: 10px; 
    }
    
    /* STREAMING INDICATOR */
    .streaming-indicator {
        color: #00fbff;
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        text-shadow: 0 0 10px #00fbff;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

# --- TRUE STREAMING AUDIO PLAYER (Web Audio API) ---
def create_streaming_audio_player():
    """Creates REAL-TIME streaming audio player using Web Audio API"""
    js_code = """
    <script>
    let audioContext = null;
    let audioQueue = [];
    let isPlaying = false;
    let currentSource = null;

    function initAudioContext() {
        if (!audioContext) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        return audioContext;
    }

    window.playStreamingAudio = function(b64data, chunkId) {
        initAudioContext();
        
        const binaryString = atob(b64data);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        
        audioQueue.push({data: bytes, id: chunkId});
        processAudioQueue();
    };

    async function processAudioQueue() {
        if (isPlaying || audioQueue.length === 0) return;
        
        isPlaying = true;
        const audioChunk = audioQueue.shift();
        
        try {
            const arrayBuffer = audioChunk.data.buffer;
            const audioBuffer = await audioContext.decodeAudioData(arrayBuffer.slice(0));
            
            const source = audioContext.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(audioContext.destination);
            source.onended = () => {
                isPlaying = false;
                processAudioQueue(); // Auto-play next chunk
            };
            source.start();
            currentSource = source;
        } catch(e) {
            console.error('Audio decode error:', e);
            isPlaying = false;
            processAudioQueue();
        }
    }

    // Stop all audio
    window.stopAllAudio = function() {
        if (currentSource) {
            currentSource.stop();
        }
        audioQueue = [];
        isPlaying = false;
    };
    </script>
    
    <div id="streaming-status" style="text-align:center; color:#00fbff; font-family:Orbitron; font-size:20px;">
        🎤 Live Voice Streaming Ready
    </div>
    """
    components.html(js_code, height=100)

# Initialize streaming player
if 'audio_initialized' not in st.session_state:
    create_streaming_audio_player()
    st.session_state.audio_initialized = True

# --- VOICE INPUT ---
query_voice = speech_to_text(
    start_prompt="TAP TO SPEAK", 
    stop_prompt="GYAN SETU IS PROCESSING...", 
    language='en-IN', 
    use_container_width=True,
    just_once=True, 
    key='core_engine_v12_final'
)

if query_voice:
    st.markdown(f'<div class="chat-container user-box"><b>Student:</b> {query_voice}</div>', unsafe_allow_html=True)
    
    # REAL-TIME STREAMING CONTAINER
    response_container = st.empty()
    
    # **100% TRUE ASYNC STREAMING**
    async def process_realtime_stream():
        text_display = ""
        stream_status = response_container.container()
        
        try:
            text_gen = aura.ask_stream(query_voice, st.session_state.messages)
            
            stream_status.markdown('<div class="chat-container streaming-indicator"><b>Gyan Setu:</b> ░░░░░░░░░░░░ LIVE STREAMING</div>', unsafe_allow_html=True)
            
            async for stream_item in aura.stream_audio_realtime(text_gen):
                if stream_item["type"] == "text":
                    text_display += stream_item["data"]
                    # Live text update
                    stream_status.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {text_display}█</div>', unsafe_allow_html=True)
                
                elif stream_item["type"] == "audio":
                    # IMMEDIATE AUDIO PLAYBACK - NO DELAY!
                    components.html(f"""
                    <script>
                        playStreamingAudio('{stream_item["data"]}', {stream_item["id"]});
                    </script>
                    """, height=0)
            
            # Final clean display
            stream_status.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {text_display}</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Stream Error: {e}")
    
    # Run the async streaming
    asyncio.run(process_realtime_stream())
    
    # Update history
    st.session_state.messages.append({"role": "user", "content": query_voice})
    st.session_state.messages.append({"role": "assistant", "content": text_display})

else:
    st.markdown("""
        <div style="text-align:center; padding:60px;">
            <div style="color:#00fbff; font-family:Orbitron; letter-spacing:5px; font-weight:900; font-size:22px; text-shadow: 0 0 15px rgba(0, 251, 255, 0.4);">
                SYSTEM ONLINE: GYAN SETU - TRUE STREAMING READY
            </div>
            <div style="color:#94a3b8; font-size:18px; margin-top:20px;">
                Tap mic → Instant text + voice streaming (Madhur/Prabhat)
            </div>
        </div>
    """, unsafe_allow_html=True)
