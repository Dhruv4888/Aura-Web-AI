import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text

st.set_page_config(page_title="AURA AI", page_icon="🎙️", layout="centered")

# CSS Fix: Is baar humne formatting ekdum simple rakhi hai taaki leak na ho
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .stApp { background-color: #0b0e14 !important; }
    
    h1 { 
        color: #00fbff !important; 
        font-family: 'Orbitron', sans-serif !important; 
        text-align: center !important; 
        font-size: 60px !important; 
        text-shadow: 0 0 20px #00fbff;
        margin-top: -50px;
    }
    
    /* Mic Button Style */
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
    }

    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display:none;}
    </style>
    """, unsafe_allow_html=True)

st.write("<h1>AURA</h1>", unsafe_allow_html=True)

# Mic Tool
text = speech_to_text(
    start_prompt="TAP", 
    stop_prompt="LISTENING...", 
    language='en-IN', 
    use_container_width=True,
    just_once=True, 
    key='aura_mic_fixed'
)

if text:
    st.markdown(f'<div class="chat-container"><b>You:</b> {text}</div>', unsafe_allow_html=True)
    with st.spinner(""):
        response = aura.ask(text)
        st.markdown(f'<div class="chat-container"><b>Aura:</b> {response}</div>', unsafe_allow_html=True)
        aura.speak(response)
else:
    st.markdown('<p style="text-align:center; color:#555; margin-top:20px;">Standby Mode...</p>', unsafe_allow_html=True)
