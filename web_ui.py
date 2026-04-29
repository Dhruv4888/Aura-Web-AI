import streamlit as st
import time
import base64
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text

st.set_page_config(page_title="Gyan Setu AI", layout="centered")

# --- 1. JAVASCRIPT SYNC ENGINE (Updated for Autoplay) ---
# Ismein humne 'Interaction' lock hataya hai
st.components.v1.html("""
    <script>
    window.audioQueue = [];
    window.isPlaying = false;

    function processQueue() {
        if (window.audioQueue.length > 0 && !window.isPlaying) {
            window.isPlaying = true;
            let base64 = window.audioQueue.shift();
            let audio = new Audio("data:audio/mp3;base64," + base64);
            audio.play().then(() => {
                audio.onended = () => {
                    window.isPlaying = false;
                    processQueue();
                };
            }).catch(e => {
                window.isPlaying = false;
                processQueue();
            });
        }
    }

    window.parent.addEventListener('message', (e) => {
        if (e.data.type === 'SYNC_VOICE') {
            window.audioQueue.push(e.data.data);
            processQueue();
        }
    });
    </script>
""", height=0)

def play_now(b64):
    st.components.v1.html(f"<script>window.parent.postMessage({{type: 'SYNC_VOICE', data: '{b64}'}}, '*');</script>", height=0)

# --- 2. UI HEADER ---
st.markdown("<h1 style='text-align: center; color: #00fbff;'>GYAN SETU</h1>", unsafe_allow_html=True)

query_voice = speech_to_text(start_prompt="🎙️ ASK ANYTHING", language='en-IN', key='final_v4')

if query_voice:
    st.markdown(f"**Student:** {query_voice}")
    full_text = ""
    current_sentence = ""
    ui_box = st.empty()
    
    # 3. STREAMING & SYNCING
    # Jaise hi text genrate hoga, voice saath chalegi
    for chunk in aura.ask_stream(query_voice, st.session_state.get('messages', [])):
        if chunk == "||SENTENCE_COMPLETE_SIGNAL||":
            if current_sentence.strip():
                # Get audio in background
                audio_b64 = aura.get_audio_data(current_sentence.strip())
                if audio_b64:
                    play_now(audio_b64) # JS will play this while Python prints next sentence
                current_sentence = ""
        else:
            full_text += chunk
            current_sentence += chunk
            ui_box.markdown(f"<div style='background:#1e1e1e; padding:20px; border-radius:10px; border-left:5px solid #00fbff;'>{full_text}▒</div>", unsafe_allow_html=True)
            time.sleep(0.04) # Natural reading speed match

    # Save History
    if "messages" not in st.session_state: st.session_state.messages = []
    st.session_state.messages.append({"role": "user", "content": query_voice})
    st.session_state.messages.append({"role": "assistant", "content": full_text})
