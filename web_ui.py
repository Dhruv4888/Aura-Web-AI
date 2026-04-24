import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
import time

# --- ORIGINAL UI CSS ---
st.set_page_config(page_title="Gyan Setu AI", page_icon="🎓", layout="centered")
if "messages" not in st.session_state: st.session_state.messages = []

st.markdown("""<style> (Purana Orbitron CSS yahan rahega) </style>""", unsafe_allow_html=True)
st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

text = speech_to_text(start_prompt="TAP TO ASK", stop_prompt="LISTENING...", language='en-IN', use_container_width=True, just_once=True, key='gyansetu_mic')

if text:
    st.markdown(f'<div class="chat-container"><b>You:</b> {text}</div>', unsafe_allow_html=True)
    
    with st.spinner("Gyan Setu is thinking..."):
        full_response = ""
        container = st.empty()
        
        # Word-by-word Rendering
        for chunk in aura.ask_stream(text, st.session_state.messages):
            full_response += chunk
            container.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_response}▌</div>', unsafe_allow_html=True)
            time.sleep(0.01)
        
        # Final render
        container.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_response}</div>', unsafe_allow_html=True)
        
        # Voice Trigger (Single Playback)
        aura.speak(full_response)
        
        st.session_state.messages.append({"role": "user", "content": text})
        st.session_state.messages.append({"role": "assistant", "content": full_response})
