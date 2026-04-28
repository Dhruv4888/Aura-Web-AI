import streamlit as st
import streamlit.components.v1 as components
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
import time

# --- UI CONFIG ---
st.set_page_config(page_title="Gyan Setu AI", page_icon="🎓", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CSS ---
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
    }
    .user-box { border-left: 5px solid #ffffff; background: #2d3748; }
    #MainMenu, header, footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display:none;}
    </style>
    """, unsafe_allow_html=True)

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

# Function to inject invisible Speech HTML
def speak_now(text, lang):
    # Escape quotes for JS
    safe_text = text.replace('"', '\\"').replace("'", "\\'")
    html_code = f"""
        <script>
            var msg = new SpeechSynthesisUtterance("{safe_text}");
            msg.lang = "{lang}";
            window.speechSynthesis.speak(msg);
        </script>
    """
    # Key change: Use unique key for every sentence to force execution
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
        
        # Detect language once for the session
        is_hindi = aura.is_hindi(text)
        lang_code = "hi-IN" if is_hindi else "en-US"
        
        for chunk in aura.ask_stream(text, st.session_state.messages):
            if chunk == "||SYNC_SPEECH||":
                if sentence_buffer.strip():
                    # Play voice immediately for this sentence
                    speak_now(sentence_buffer.strip(), lang_code)
                    sentence_buffer = ""
            else:
                full_display_text += chunk
                sentence_buffer += chunk
                # Update text in UI
                container.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_display_text}▌</div>', unsafe_allow_html=True)
        
        container.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_display_text}</div>', unsafe_allow_html=True)
        
        st.session_state.messages.append({"role": "user", "content": text})
        st.session_state.messages.append({"role": "assistant", "content": full_display_text})
else:
    st.markdown('<p style="text-align:center; color:#555; margin-top:20px;">Ready for your academic questions...</p>', unsafe_allow_html=True)
