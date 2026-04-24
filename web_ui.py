import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
import time

st.set_page_config(page_title="Gyan Setu AI", page_icon="🎓", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []

# (Purana Orbitron CSS yahan paste karein...)
st.markdown("""<style>...</style>""", unsafe_allow_html=True)

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

text = speech_to_text(start_prompt="TAP TO ASK", stop_prompt="LISTENING...", language='en-IN', use_container_width=True, just_once=True, key='gyansetu_mic')

if text:
    st.markdown(f'<div class="chat-container"><b>You:</b> {text}</div>', unsafe_allow_html=True)
    
    with st.spinner("Gyan Setu is thinking..."):
        full_response = ""
        current_sentence = ""
        container = st.empty()
        
        for chunk in aura.ask_stream(text, st.session_state.messages):
            full_response += chunk
            current_sentence += chunk
            
            # UI Update (Rendering)
            container.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_response}▌</div>', unsafe_allow_html=True)
            
            # JAISE-JAISE Logic: Agar sentence khatam hua (., !, ?) toh turant bolo
            if any(punc in chunk for punc in [".", "!", "?", "\n"]):
                if len(current_sentence.strip()) > 10: # Chote words par skip karega
                    aura.speak_sentence(current_sentence)
                    current_sentence = "" # Reset for next sentence
            
            time.sleep(0.01)
        
        # Final render and save
        container.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_response}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "user", "content": text})
        st.session_state.messages.append({"role": "assistant", "content": full_response})

        # Agar aakhri sentence bacha ho toh usey bhi bol do
        if current_sentence.strip():
            aura.speak_sentence(current_sentence)
