import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
import time

st.set_page_config(page_title="Gyan Setu AI", page_icon="🎓", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []

# (CSS same rahega, Orbitron theme wala)
st.markdown("""<style>...</style>""", unsafe_allow_html=True) # Purana CSS yahan rahega

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

text = speech_to_text(
    start_prompt="TAP TO ASK", 
    stop_prompt="LISTENING...", 
    language='en-IN', 
    use_container_width=True,
    just_once=True, 
    key='gyansetu_mic'
)

if text:
    st.markdown(f'<div class="chat-container"><b>You:</b> {text}</div>', unsafe_allow_html=True)
    
    with st.chat_message("assistant", avatar="🎓"):
        # Placeholder for streaming text
        full_response = ""
        message_placeholder = st.empty()
        
        # Stream text and get the full content
        for chunk in aura.ask_stream(text, st.session_state.messages):
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
            time.sleep(0.01) # Small delay for smooth effect
        
        message_placeholder.markdown(full_response)
        
        # Save to memory
        st.session_state.messages.append({"role": "user", "content": text})
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        # Trigger Voice
        with st.spinner("Generating Voice..."):
            aura.speak(full_response)
else:
    st.markdown('<p style="text-align:center; color:#555; margin-top:20px;">Ready for your questions...</p>', unsafe_allow_html=True)
