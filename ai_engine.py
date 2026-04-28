import streamlit as st
import streamlit.components.v1 as components
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
import time
import base64

# --- UI CONFIG ---
st.set_page_config(page_title="Gyan Setu AI", page_icon="🎓", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CSS (Full Length) ---
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
    button[data-testid="stBaseButton-secondary"] {
        background-color: #00fbff !important;
        color: #0b0e14 !important;
        border-radius: 100px !important;
        width: 180px !important;
        height: 180px !important;
        border: 8px solid #1a202c !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: bold !important;
        display: block !important;
        margin: 0 auto !important;
        box-shadow: 0 0 30px rgba(0, 251, 255, 0.4) !important;
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
        font-size: 18px;
    }
    .user-box { border-left: 5px solid #ffffff; background: #2d3748; }
    #MainMenu, header, footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display:none;}
    </style>
    """, unsafe_allow_html=True)

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

# --- THE FIX: GLOBAL AUDIO LOCK ENGINE ---
def play_queued_audio(b64_data, index):
    # Har sentence ke liye ek unique Iframe jo parent window (browser) ki queue use karega
    js_code = f"""
    <script>
    (function() {{
        // Browser ki global window mein queue check karna
        if (!window.parent.audioQueue) window.parent.audioQueue = [];
        if (typeof window.parent.isAudioPlaying === 'undefined') window.parent.isAudioPlaying = false;

        function processQueue() {{
            if (window.parent.audioQueue.length === 0 || window.parent.isAudioPlaying) return;

            window.parent.isAudioPlaying = true;
            let nextAudioB64 = window.parent.audioQueue.shift();
            let audio = new Audio("data:audio/mp3;base64," + nextAudioB64);
            
            audio.onended = function() {{
                window.parent.isAudioPlaying = false;
                processQueue();
            }};

            audio.play().catch(e => {{
                window.parent.isAudioPlaying = false;
                processQueue();
            }});
        }}

        // Naye audio ko queue mein daalna
        window.parent.audioQueue.push("{b64_data}");
        processQueue();
    }})();
    </script>
    """
    # Unique key ensures Streamlit doesn't overwrite the previous component too fast
    components.html(js_code, height=0, width=0)

# --- MAIN APP LOGIC ---
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
        current_sentence = ""
        container = st.empty()
        sentence_count = 0
        
        for chunk in aura.ask_stream(text, st.session_state.messages):
            if chunk == "||SYNC_SIGNAL||":
                if current_sentence.strip():
                    audio_b64 = aura.get_audio_data(current_sentence.strip())
                    if audio_b64:
                        sentence_count += 1
                        # Unique call for each sentence
                        play_queued_audio(audio_b64, sentence_count)
                    current_sentence = "" 
            else:
                full_display_text += chunk
                current_sentence += chunk
                container.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_display_text}▌</div>', unsafe_allow_html=True)
        
        container.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_display_text}</div>', unsafe_allow_html=True)
        
        st.session_state.messages.append({"role": "user", "content": text})
        st.session_state.messages.append({"role": "assistant", "content": full_display_text})
else:
    st.markdown('<p style="text-align:center; color:#555; margin-top:20px;">Ready for your academic queries...</p>', unsafe_allow_html=True)
