import streamlit as st
import streamlit.components.v1 as components
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
import os
import base64

# --- UI CONFIG ---
st.set_page_config(page_title="Gyan Setu AI", page_icon="🎓", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CSS (No length cuts) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #0b0e14 !important; }
    h1 { 
        color: #00fbff !important; 
        font-family: 'Orbitron', sans-serif !important; 
        text-align: center !important; 
        font-size: 50px !important; 
        text-shadow: 0 0 20px #00fbff;
        margin-top: -50px;
    }
    .chat-container {
        background: #1a202c;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #00fbff;
        color: white;
        margin-top: 20px;
        font-family: 'Arial', sans-serif;
        line-height: 1.6;
    }
    .user-box { border-left: 5px solid #ffffff; background: #2d3748; }
    #MainMenu, header, footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display:none;}
    </style>
    """, unsafe_allow_html=True)

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

# Advanced Audio Queue Controller (JavaScript)
def play_audio_sequence(audio_base64):
    """Injects audio into a browser-side queue to prevent overlap"""
    html_code = f"""
        <script>
            if (!window.audioQueue) window.audioQueue = [];
            if (!window.isAudioPlaying) window.isAudioPlaying = false;

            function playNext() {{
                if (window.audioQueue.length === 0) {{
                    window.isAudioPlaying = false;
                    return;
                }}
                window.isAudioPlaying = true;
                let audioData = window.audioQueue.shift();
                let audio = new Audio("data:audio/mp3;base64," + audioData);
                audio.onended = playNext;
                audio.play();
            }}

            window.audioQueue.push("{audio_base64}");
            if (!window.isAudioPlaying) playNext();
        </script>
    """
    components.html(html_code, height=0, width=0)

# Mic Tool
text = speech_to_text(
    start_prompt="TAP TO ASK", 
    stop_prompt="LISTENING...", 
    language='en-IN', 
    use_container_width=True,
    just_once=True, 
    key='gyansetu_mic'
)

if text:
    st.markdown(f'<div class="chat-container user-box"><b>Student:</b> {text}</div>', unsafe_allow_html=True)
    
    with st.spinner("Gyan Setu is analyzing..."):
        full_display_text = ""
        sentence_buffer = ""
        container = st.empty()
        
        for chunk in aura.ask_stream(text, st.session_state.messages):
            if chunk == "||SYNC_SPEECH||":
                if sentence_buffer.strip():
                    # 1. Generate High Quality Edge-TTS
                    audio_file = aura.get_audio_link(sentence_buffer.strip())
                    if audio_file:
                        with open(audio_file, "rb") as f:
                            data = base64.b64encode(f.read()).decode()
                            # 2. Push to JS Queue for seamless play
                            play_audio_sequence(data)
                        os.remove(audio_file)
                    sentence_buffer = ""
            else:
                full_display_text += chunk
                sentence_buffer += chunk
                container.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_display_text}▌</div>', unsafe_allow_html=True)
        
        container.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_display_text}</div>', unsafe_allow_html=True)
        
        st.session_state.messages.append({"role": "user", "content": text})
        st.session_state.messages.append({"role": "assistant", "content": full_display_text})
else:
    st.markdown('<p style="text-align:center; color:#555; margin-top:20px;">Ready for your academic queries...</p>', unsafe_allow_html=True)
