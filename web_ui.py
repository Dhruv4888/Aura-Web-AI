import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
from streamlit_js_eval import streamlit_js_eval

# --- UI CONFIG ---
st.set_page_config(page_title="Gyan Setu AI", page_icon="🎓", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CSS (Orbitron & Academic Theme) ---
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

# JavaScript function to handle browser voice (Queued Speech)
def speak_via_js(text, lang_code):
    js_code = f"""
    (function() {{
        const msg = new SpeechSynthesisUtterance("{text}");
        msg.lang = "{lang_code}";
        msg.rate = 1.0;
        window.speechSynthesis.speak(msg);
    }})();
    """
    streamlit_js_eval(code=js_code, key=f"speak_{hash(text)}")

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
        
        # Detect language for browser voice
        is_hindi = aura.is_hindi(text)
        lang_code = "hi-IN" if is_hindi else "en-US"
        
        for chunk in aura.ask_stream(text, st.session_state.messages):
            if chunk == "||SYNC_SPEECH||":
                if sentence_buffer.strip():
                    # Clean special characters for JS string
                    clean_chunk = sentence_buffer.replace('"', '').replace("'", "").strip()
                    speak_via_js(clean_chunk, lang_code)
                    sentence_buffer = ""
            else:
                full_display_text += chunk
                sentence_buffer += chunk
                container.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_display_text}▌</div>', unsafe_allow_html=True)
        
        container.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_display_text}</div>', unsafe_allow_html=True)
        
        st.session_state.messages.append({"role": "user", "content": text})
        st.session_state.messages.append({"role": "assistant", "content": full_display_text})
else:
    st.markdown('<p style="text-align:center; color:#555; margin-top:20px;">Ready for your academic questions...</p>', unsafe_allow_html=True)
