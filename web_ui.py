import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text

st.set_page_config(page_title="AURA AI", page_icon="🎙️")

# CSS Fix: Isse wo faltu text gayab ho jayega
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap" rel="stylesheet">
    <style>
    .stApp { background-color: #0b0e14 !important; color: #00fbff !important; }
    h1 { color: #00fbff; font-family: 'Orbitron', sans-serif; text-align: center; font-size: 60px; text-shadow: 0 0 20px #00fbff; }
    
    /* Mic Button Styling */
    button[data-testid="stBaseButton-secondary"] {
        background-color: #00fbff !important;
        color: #0b0e14 !important;
        border-radius: 100px !important;
        width: 200px !important;
        height: 200px !important;
        border: 10px solid #1a202c !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: bold !important;
        font-size: 24px !important;
        box-shadow: 0 0 30px rgba(0, 251, 255, 0.5) !important;
        display: block;
        margin: 0 auto;
    }

    .chat-box { 
        background: #1a202c; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #00fbff; 
        margin-top: 20px; 
        color: white;
    }
    
    /* Hiding Streamlit header/footer for clean look */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.write("<h1>AURA</h1>", unsafe_allow_html=True)

# Mic Recording Tool
text = speech_to_text(
    start_prompt="TAP", 
    stop_prompt="LISTENING...", 
    language='en-IN', 
    use_container_width=True,
    just_once=True, 
    key='aura_mic'
)

if text:
    st.markdown(f'<div class="chat-box"><b>You:</b> {text}</div>', unsafe_allow_html=True)
    with st.spinner(""):
        response = aura.ask(text)
        st.markdown(f'<div class="chat-box"><b>Aura:</b> {response}</div>', unsafe_allow_html=True)
        aura.speak(response)
else:
    st.markdown('<p style="text-align:center; color:#a0aec0; margin-top:20px;">Tap the button and speak to Aura</p>', unsafe_allow_html=True)
