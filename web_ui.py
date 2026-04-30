import streamlit as st
from streamlit_mic_recorder import speech_to_text
from ai_engine import aura
import base64
import json


if "messages" not in st.session_state:
    st.session_state.messages = []


st.set_page_config(
    page_title="Gyan Setu AI - Global Academic Mentor",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# --- UI Style (same cosmic orbitron look) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    
    .stApp { background: radial-gradient(circle at center, #0f172a 0%, #020617 100%) !important; }

    h1 { 
        color: #00fbff !important; 
        font-family: 'Orbitron', sans-serif !important; 
        text-align: center !important; 
        font-size: 65px !important; 
        text-shadow: 0 0 40px #00fbff, 0 0 15px rgba(0, 251, 255, 0.5);
        margin-top: -85px;
        letter-spacing: 12px;
        text-transform: uppercase;
        font-weight: 900;
    }

    button[data-testid="stBaseButton-secondary"] {
        background-color: #00fbff !important;
        color: #0b0e14 !important;
        border-radius: 50% !important;
        width: 175px !important;
        height: 175px !important;
        border: 15px solid #1e293b !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900 !important;
        margin: 45px auto !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        box-shadow: 0 0 70px rgba(0, 251, 255, 0.35) !important;
        transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        cursor: pointer;
    }

    button[data-testid="stBaseButton-secondary"]:hover {
        transform: scale(1.1) rotate(-2deg);
        box-shadow: 0 0 100px rgba(0, 251, 255, 0.8) !important;
        border-color: #ffffff !important;
    }

    .chat-container {
        background: rgba(15, 23, 42, 0.95);
        padding: 50px;
        border-radius: 35px;
        border-left: 20px solid #00fbff;
        color: #f1f5f9;
        margin-top: 40px;
        font-family: 'Rajdhani', sans-serif;
        line-height: 2.1;
        font-size: 28px;
        box-shadow: 30px 30px 80px rgba(0,0,0,0.85);
        border-right: 2px solid rgba(0, 251, 255, 0.1);
        backdrop-filter: blur(25px);
    }

    .user-box { 
        border-left: 20px solid #ffffff; 
        background: rgba(30, 41, 59, 0.95); 
        box-shadow: 15px 15px 50px rgba(0,0,0,0.6);
    }

    #MainMenu, header, footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display:none;}

    ::-webkit-scrollbar { width: 12px; }
    ::-webkit-scrollbar-track { background: #020617; }
    ::-webkit-scrollbar-thumb { 
        background: linear-gradient(#00fbff, #005f61); 
        border-radius: 10px; 
    }
    </style>
""", unsafe_allow_html=True)

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)


# --- Hidden JS TTS + SYNC ENGINE (client side, word-by-word) ---
def inject_tts_engine_js():
    st.markdown(
        """
        <script>
        // ---- TTS ENGINE (Web‑based, Edge‑TTS–style) ----
        const GyanSetu_TTS = {
            // Cache: text → audio URL mapping
            cache: new Map(),
            // Current stream state
            currentText: "",
            currentWords: [],
            wordIndex: 0,
            audioCtx: null,
            buffers: [],
            isPlaying: false,

            async init() {
                this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            },

            // Assign voice based on Hindi/English content
            getVoice(text) {
                const hasHindi = /[\u0900-\u097F]/.test(text);
                return hasHindi ? "hi-IN-MadhurNeural" : "en-IN-PrabhatNeural";
            },

            // Mock TTS API (Streamlit‑side we just send text, assume MP3 URL)
            async fetchTTSChunk(text) {
                // In real production, you'd call a server‑side TTS API
                // For now, this is like a placeholder that returns an audio URL
                const voice = this.getVoice(text);
                // Example: external TTS endpoint
                const resp = await fetch("/api/tts", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text, voice }),
                });

                if (!resp.ok) throw new Error("TTS failed");
                const data = await resp.json();
                return data.url; // e.g., "/tts/123.mp3"
            },

            async loadBuffers(text) {
                const words = text.split("\\s+");
                this.currentText = text;
                this.currentWords = words;
                this.buffers = [];

                // Edge‑TTS‑style streaming: split text into chunks, fetch audio chunks
                for (const word of words) {
                    if (!word.trim()) continue;

                    try {
                        const chunkText = word.trim() + " "; // each word
                        const audioUrl = await this.fetchTTSChunk(chunkText);
                        const bufferResp = await fetch(audioUrl);
                        const bufferData = await bufferResp.arrayBuffer();
                        const buffer = await this.audioCtx.decodeAudioData(bufferData);
                        this.buffers.push({ buffer, word });
                    } catch (e) {
                        console.warn("TTS chunk failed:", word, e);
                        // Create silent fallback buffer
                        const fallback = this.audioCtx.createBuffer(1, 441, 44100);
                        this.buffers.push({ buffer: fallback, word });
                    }
                }
            },

            async playFromOffset(offset) {
                if (this.isPlaying) return;
                if (this.buffers.length === 0) return;

                this.isPlaying = true;
                const source = this.audioCtx.createBufferSource();
                const idx = Math.max(0, Math.min(this.buffers.length - 1, offset));
                const { buffer, word } = this.buffers[idx];

                const startTime = this.audioCtx.currentTime;
                source.buffer = buffer;
                source.connect(this.audioCtx.destination);
                source.start(startTime);

                // Close only after playback ends
                source.onended = () => {
                    this.isPlaying = false;
                };
            },

            async playWordByWord(text) {
                // Initialize audio context
                if (!this.audioCtx) await this.init();

                // Load buffers for this text
                await this.loadBuffers(text);

                let wordIndex = 0;
                // Each 200ms, highlight next word + play audio if aligned
                const interval = setInterval(() => {
                    if (wordIndex >= this.buffers.length) {
                        clearInterval(interval);
                        return;
                    }
                    const word = this.buffers[wordIndex].word;

                    // Highlight text in DOM (sync with typing)
                    const target = document.querySelector("#mentor-typing");
                    if (target) {
                        const fullText = target.textContent;
                        const regex = new RegExp("\\b" + escapeRegExp(word) + "\\b", "g");
                        target.innerHTML = fullText.replace(
                            regex,
                            `<span style="text-shadow: 0 0 8px rgba(0,251,255,0.7);">${word}</span>`
                        );
                    }

                    wordIndex++;
                }, 200);
            }
        };

        // Helper
        function escapeRegExp(s) {
            return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
        }

        // Message pump: Streamlit se aa raha streaming text
        // Ye example: text chunks stream kar raha
        let GyanSetuStream = "";
        function streamText(textChunk) {
            GyanSetuStream += textChunk;
            const target = document.querySelector("#mentor-typing");
            if (target) {
                target.textContent = GyanSetuStream + "▌";
            }
        }

        // Called from Streamlit Python side (when done writing)
        function finishTextAndPlay() {
            const target = document.querySelector("#mentor-typing");
            if (target) {
                target.textContent = GyanSetuStream;
            }
            GyanSetu_TTS.playWordByWord(GyanSetuStream);
        }

        // Triggered from Streamlit -> JS
        window.startTypingAndTTS = (stream, finalText) => {
            GyanSetuStream = "";
            const target = document.querySelector("#mentor-typing");
            if (!target) return;

            // Simulate typing animation (can be removed later, this is visual)
            let i = 0;
            const interval = setInterval(() => {
                if (i >= finalText.length) {
                    clearInterval(interval);
                    finishTextAndPlay();
                    return;
                }
                streamText(finalText.slice(0, i + 1));
                i++;
            }, 30); // 30ms between characters
        };
        </script>
        """,
        unsafe_allow_html=True,
    )


# --- JS call helper (send text to browser JS) ---
def call_js_tts(text):
    code = f"""
    <script>
    if (typeof startTypingAndTTS === "function") {{
        startTypingAndTTS([], `{json.dumps(text).replace("`", "\\`")}`);
    }}
    </script>
    """
    st.markdown(code, unsafe_allow_html=True)


# --- Voice input + answer logic (server side) ---
query_voice = speech_to_text(
    start_prompt="TAP TO SPEAK",
    stop_prompt="GYAN SETU IS PROCESSING...",
    language='en-IN',
    use_container_width=True,
    just_once=True,
    key='core_engine_v12_final'
)

if query_voice:
    st.markdown(f'<div class="chat-container user-box"><b>Student:</b> {query_voice}</div>', unsafe_allow_html=True)

    with st.spinner("Synthesizing solution..."):
        full_text = ""
        ui_anchor = st.empty()

        # 1. Text‑streaming (UI side)
        for text_fragment in aura.ask_stream(query_voice, st.session_state.messages):
            if text_fragment == "||SYNC_SIGNAL||":
                continue
            full_text += text_fragment
            ui_anchor.markdown(
                f'<div class="chat-container" id="mentor-typing">{full_text}▒</div>',
                unsafe_allow_html=True,
            )

        ui_anchor.markdown(
            f'<div class="chat-container" id="mentor-typing">{full_text}</div>',
            unsafe_allow_html=True,
        )

        # 2. Send final text to client‑side JS TTS engine
        inject_tts_engine_js()
        call_js_tts(full_text)

        st.session_state.messages.append({"role": "user", "content": query_voice})
        st.session_state.messages.append({"role": "assistant", "content": full_text})

else:
    st.markdown("""
        <div style="text-align:center; padding:60px;">
            <div style="color:#00fbff; font-family:Orbitron; letter-spacing:5px; font-weight:900; font-size:22px; text-shadow: 0 0 15px rgba(0, 251, 255, 0.4);">
                SYSTEM ONLINE: GYAN SETU
            </div>
        </div>
    """, unsafe_allow_html=True)
