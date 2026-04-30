import streamlit as st
import time
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text

st.set_page_config(page_title="Gyan Setu AI", layout="centered")

# --- JAVASCRIPT REAL-TIME VOICE ENGINE ---
# Ismein zero buffering hai. Jo word aayega, wahi turant bola jayega.
st.components.v1.html("""
    <script>
    window.speechQueue = "";
    
    function speak(text) {
        if (!window.speechSynthesis) return;
        let utterance = new SpeechSynthesisUtterance(text);
        
        // Language detection for Browser Voice
        if (/[\\u0900-\\u097F]/.test(text)) {
            utterance.lang = 'hi-IN'; // Hindi Voice
        } else {
            utterance.lang = 'en-IN'; // English Voice
        }
        
        utterance.rate = 1.1; // Natural speed
        window.speechSynthesis.speak(utterance);
    }

    window.parent.addEventListener('message', (e) => {
        if (e.data.type === 'STREAM_WORD') {
            speak(e.data.text);
        }
    });
    </script>
""", height=0)

def stream_to_browser(text):
    st.components.v1.html(f"<script>window.parent.postMessage({{type: 'STREAM_WORD', text: '{text}'}}, '*');</script>", height=0)

st.markdown("<h1 style='text-align: center; color: #00fbff;'>GYAN SETU</h1>", unsafe_allow_html=True)

query_voice = speech_to_text(start_prompt="🎙️ BOLNA SHURU KAREIN", language='en-IN', key='sync_v5')

if query_voice:
    st.markdown(f"**Student:** {query_voice}")
    full_text = ""
    ui_box = st.empty()
    
    # 100% REAL-TIME SYNC LOOP
    for token in aura.ask_stream(query_voice, st.session_state.get('messages', [])):
        full_text += token
        ui_box.markdown(f"<div style='background:#1e1e1e; padding:20px; border-radius:10px; border-left:5px solid #00fbff; font-size:24px;'>{full_text}▒</div>", unsafe_allow_html=True)
        
        # Word-by-word voice trigger
        if any(punc in token for punc in [' ', '.', '।', '!', '?']):
            clean_token = token.replace("'", "").replace('"', "")
            stream_to_browser(clean_token)
        
        time.sleep(0.01) # Ultra-fast typing

    # Save History
    if "messages" not in st.session_state: st.session_state.messages = []
    st.session_state.messages.append({"role": "user", "content": query_voice})
    st.session_state.messages.append({"role": "assistant", "content": full_text})
