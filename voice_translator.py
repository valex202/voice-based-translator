import streamlit as st
import speech_recognition as sr
from googletrans import Translator

# --- Page Configuration ---
st.set_page_config(
    page_title="VoxBridge | AI Translator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

translator = Translator()

if 'history' not in st.session_state:
    st.session_state.history = []

# --- PREMIUM UI CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    /* ===================== RESET & BASE ===================== */
    * { box-sizing: border-box; }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* ---- FORCE SIDEBAR ALWAYS OPEN ---- */
    [data-testid="stSidebar"] {
        transform: translateX(0) !important;
        display: block !important;
        visibility: visible !important;
        width: 21rem !important;
        min-width: 21rem !important;
        position: relative !important;
    }
    /* Hide the collapse arrow button — sidebar is always open */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    button[data-testid="baseButton-headerNoPadding"] {
        display: none !important;
    }

    :root {
        --bg-base:      #04060d;
        --bg-card:      rgba(255,255,255,0.035);
        --bg-card-hov:  rgba(255,255,255,0.065);
        --border:       rgba(255,255,255,0.08);
        --border-glow:  rgba(0,212,180,0.5);
        --accent:       #00d4b4;
        --accent2:      #ff6b6b;
        --accent3:      #ffd166;
        --text-primary: #eef2f7;
        --text-muted:   #6b7fa3;
        --text-dim:     #3d4f6b;
        --font-display: 'Syne', sans-serif;
        --font-mono:    'Space Mono', monospace;
        --font-body:    'DM Sans', sans-serif;
    }

    /* ===================== BODY ===================== */
    .stApp {
        background-color: var(--bg-base);
        background-image:
            radial-gradient(ellipse 80% 50% at 20% -10%, rgba(0, 212, 180, 0.12) 0%, transparent 60%),
            radial-gradient(ellipse 60% 40% at 80% 100%, rgba(255, 107, 107, 0.08) 0%, transparent 55%),
            url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.015'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        color: var(--text-primary);
        font-family: var(--font-body);
        min-height: 100vh;
    }

    /* ===================== SIDEBAR ===================== */
    [data-testid="stSidebar"] {
        background: rgba(4, 6, 13, 0.95) !important;
        border-right: 1px solid var(--border) !important;
        backdrop-filter: blur(20px);
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    .sidebar-logo-wrap {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 10px 0 20px;
        border-bottom: 1px solid var(--border);
        margin-bottom: 20px;
    }
    .sidebar-brand {
        font-family: var(--font-display);
        font-size: 22px;
        font-weight: 800;
        color: var(--accent);
        letter-spacing: -0.5px;
        margin-top: 10px;
    }
    .sidebar-sub {
        font-family: var(--font-mono);
        font-size: 10px;
        color: var(--text-muted);
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 3px;
    }

    .student-card {
        background: linear-gradient(135deg, rgba(0,212,180,0.06), rgba(255,107,107,0.04));
        border: 1px solid rgba(0,212,180,0.15);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
    }
    .student-tag {
        font-family: var(--font-mono);
        font-size: 9px;
        color: var(--accent);
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .student-name {
        font-family: var(--font-display);
        font-size: 13px;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.3;
    }
    .student-reg {
        font-family: var(--font-mono);
        font-size: 11px;
        color: var(--accent3);
        margin-top: 5px;
    }

    .sidebar-section-label {
        font-family: var(--font-mono);
        font-size: 9px;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: var(--text-dim);
        margin-bottom: 8px;
        margin-top: 20px;
        padding-left: 2px;
    }

    /* Sidebar selectbox & radio */
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        font-family: var(--font-body) !important;
    }
    [data-testid="stSidebar"] .stRadio > div {
        gap: 8px;
    }
    [data-testid="stSidebar"] .stRadio label {
        background: rgba(255,255,255,0.03);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 10px 14px;
        font-family: var(--font-body);
        font-size: 13px;
        color: var(--text-muted) !important;
        transition: all 0.2s;
        cursor: pointer;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(0,212,180,0.08);
        border-color: rgba(0,212,180,0.3);
        color: var(--text-primary) !important;
    }

    /* ===================== MAIN AREA ===================== */
    .main .block-container {
        padding: 2rem 2rem 4rem;
        max-width: 900px;
        margin: 0 auto;
    }

    /* ---- Hero Header ---- */
    .hero-wrap {
        text-align: center;
        padding: 2rem 0 1.5rem;
        position: relative;
    }
    .hero-eyebrow {
        font-family: var(--font-mono);
        font-size: 10px;
        letter-spacing: 5px;
        text-transform: uppercase;
        color: var(--accent);
        margin-bottom: 14px;
        opacity: 0.85;
    }
    .hero-title {
        font-family: var(--font-display);
        font-size: clamp(32px, 6vw, 62px);
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -2px;
        line-height: 1.05;
        margin: 0 0 10px;
    }
    .hero-title span {
        color: var(--accent);
        position: relative;
    }
    .hero-subtitle {
        font-family: var(--font-body);
        font-size: clamp(13px, 2vw, 15px);
        color: var(--text-muted);
        font-weight: 300;
        max-width: 500px;
        margin: 0 auto 6px;
        line-height: 1.6;
    }

    /* ---- Mode Badge ---- */
    .mode-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(0,212,180,0.08);
        border: 1px solid rgba(0,212,180,0.2);
        border-radius: 50px;
        padding: 6px 16px;
        font-family: var(--font-mono);
        font-size: 11px;
        color: var(--accent);
        letter-spacing: 1px;
        margin: 16px auto 0;
    }
    .mode-dot {
        width: 6px; height: 6px;
        border-radius: 50%;
        background: var(--accent);
        animation: pulse-dot 2s infinite;
    }
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.7); }
    }

    /* ---- Tip Box ---- */
    .tip-wrap {
        background: rgba(255,209,102,0.05);
        border: 1px solid rgba(255,209,102,0.15);
        border-radius: 12px;
        padding: 12px 20px;
        text-align: center;
        font-family: var(--font-body);
        font-size: 12px;
        color: var(--text-muted);
        margin: 20px 0;
        letter-spacing: 0.3px;
    }
    .tip-wrap b { color: var(--accent3); }

    /* ---- Speak Button ---- */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent) 0%, #00b89a 100%) !important;
        color: #04060d !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 18px 32px !important;
        font-family: var(--font-display) !important;
        font-size: 16px !important;
        font-weight: 800 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 0 30px rgba(0,212,180,0.25), 0 4px 20px rgba(0,0,0,0.4) !important;
        width: 100% !important;
        position: relative;
        overflow: hidden;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 0 55px rgba(0,212,180,0.45), 0 8px 30px rgba(0,0,0,0.5) !important;
    }
    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* Clear button in sidebar */
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255,107,107,0.1) !important;
        color: var(--accent2) !important;
        border: 1px solid rgba(255,107,107,0.25) !important;
        box-shadow: none !important;
        font-size: 13px !important;
        padding: 12px 20px !important;
        border-radius: 10px !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,107,107,0.2) !important;
        box-shadow: none !important;
    }

    /* ---- Status Container ---- */
    .status-wrap {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 14px;
        padding: 18px 30px;
        background: rgba(255,255,255,0.03);
        border: 1px solid var(--border);
        border-radius: 14px;
        margin: 14px 0;
    }
    .status-text {
        font-family: var(--font-mono);
        font-size: 13px;
        letter-spacing: 1px;
    }
    .status-bars {
        display: flex;
        align-items: center;
        gap: 3px;
        height: 30px;
    }
    .bar {
        width: 4px;
        border-radius: 3px;
        background: var(--accent);
        animation: eq 0.9s infinite ease-in-out;
    }
    .bar:nth-child(1) { height: 10px; animation-delay: 0.0s; }
    .bar:nth-child(2) { height: 16px; animation-delay: 0.1s; }
    .bar:nth-child(3) { height: 24px; animation-delay: 0.2s; background: var(--accent2); }
    .bar:nth-child(4) { height: 16px; animation-delay: 0.3s; }
    .bar:nth-child(5) { height: 10px; animation-delay: 0.4s; }
    .bar:nth-child(6) { height: 18px; animation-delay: 0.15s; }
    .bar:nth-child(7) { height: 12px; animation-delay: 0.25s; }
    @keyframes eq {
        0%, 100% { transform: scaleY(1); }
        50% { transform: scaleY(2.2); }
    }
    .spinner {
        width: 22px; height: 22px;
        border: 2px solid rgba(255,209,102,0.15);
        border-top: 2px solid var(--accent3);
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* ---- Transcript Section ---- */
    .transcript-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 32px 0 16px;
    }
    .transcript-line {
        flex: 1;
        height: 1px;
        background: linear-gradient(to right, var(--border), transparent);
    }
    .transcript-label {
        font-family: var(--font-mono);
        font-size: 9px;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: var(--text-dim);
        white-space: nowrap;
    }

    /* ---- Translation Cards ---- */
    .t-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 16px;
        position: relative;
        overflow: hidden;
        transition: all 0.25s ease;
    }
    .t-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 3px; height: 100%;
        background: linear-gradient(to bottom, var(--accent), transparent);
        border-radius: 3px 0 0 3px;
    }
    .t-card:hover {
        background: var(--bg-card-hov);
        border-color: rgba(255,255,255,0.13);
        transform: translateY(-2px);
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }
    .t-card-num {
        font-family: var(--font-mono);
        font-size: 9px;
        color: var(--text-dim);
        letter-spacing: 2px;
        position: absolute;
        top: 16px; right: 20px;
    }
    .t-label {
        font-family: var(--font-mono);
        font-size: 9px;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: var(--text-dim);
        margin-bottom: 6px;
    }
    .t-original {
        font-family: var(--font-body);
        font-size: clamp(14px, 2.5vw, 16px);
        color: #8da0bb;
        margin-bottom: 18px;
        line-height: 1.5;
        font-style: italic;
    }
    .t-label-out {
        font-family: var(--font-mono);
        font-size: 9px;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: var(--accent);
        margin-bottom: 6px;
        opacity: 0.8;
    }
    .t-translated {
        font-family: var(--font-display);
        font-size: clamp(18px, 4vw, 26px);
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.25;
        letter-spacing: -0.5px;
    }
    .t-divider {
        border: none;
        border-top: 1px solid var(--border);
        margin: 16px 0;
    }

    /* ---- Empty State ---- */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: var(--text-dim);
    }
    .empty-icon {
        font-size: 48px;
        margin-bottom: 16px;
        opacity: 0.4;
    }
    .empty-text {
        font-family: var(--font-mono);
        font-size: 11px;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: var(--text-dim);
    }

    /* ---- Info / Warning / Error Overrides ---- */
    .stAlert {
        border-radius: 12px !important;
        font-family: var(--font-body) !important;
        font-size: 13px !important;
        border: 1px solid var(--border) !important;
    }

    /* ---- Expander ---- */
    .stExpander {
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        background: var(--bg-card) !important;
    }
    .stExpander summary {
        font-family: var(--font-body) !important;
        font-size: 13px !important;
        color: var(--text-muted) !important;
    }

    /* ===================== MOBILE RESPONSIVE ===================== */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 1rem 4rem !important;
        }
        .hero-title {
            font-size: 28px !important;
            letter-spacing: -1px !important;
        }
        .hero-subtitle {
            font-size: 13px !important;
        }
        .t-card {
            padding: 18px 18px !important;
        }
        .t-translated {
            font-size: 20px !important;
        }
        .status-wrap {
            padding: 14px 16px !important;
            gap: 10px !important;
        }
        .status-text {
            font-size: 11px !important;
        }
        .tip-wrap {
            font-size: 11px !important;
            padding: 10px 14px !important;
        }
        [data-testid="stSidebar"] {
            width: 280px !important;
        }
        .stButton > button {
            padding: 15px 20px !important;
            font-size: 14px !important;
        }
    }

    @media (max-width: 480px) {
        .hero-title {
            font-size: 24px !important;
            letter-spacing: -0.5px !important;
        }
        .main .block-container {
            padding: 0.75rem 0.75rem 3rem !important;
        }
        .t-card {
            padding: 14px 14px !important;
        }
        .bar { width: 3px !important; }
    }
</style>
""", unsafe_allow_html=True)

# --- Language Dictionary ---
languages = {
    'Igbo':    {'mt': 'ig',    'stt': 'ig-NG'},
    'Hausa':   {'mt': 'ha',    'stt': 'ha-NG'},
    'Yoruba':  {'mt': 'yo',    'stt': 'yo-NG'},
    'French':  {'mt': 'fr',    'stt': 'fr-FR'},
    'Spanish': {'mt': 'es',    'stt': 'es-ES'},
    'German':  {'mt': 'de',    'stt': 'de-DE'},
    'Chinese': {'mt': 'zh-cn', 'stt': 'zh-CN'},
    'Arabic':  {'mt': 'ar',    'stt': 'ar-SA'},
    'Swahili': {'mt': 'sw',    'stt': 'sw-KE'},
    'Portuguese': {'mt': 'pt', 'stt': 'pt-PT'},
}

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
    <div class='sidebar-logo-wrap'>
        <div style='width:52px;height:52px;border-radius:14px;background:linear-gradient(135deg,#00d4b4,#00856f);
                    display:flex;align-items:center;justify-content:center;font-size:26px;box-shadow:0 0 20px rgba(0,212,180,0.3);'>
            🌐
        </div>
        <div class='sidebar-brand'>VoxBridge</div>
        <div class='sidebar-sub'>AI Neural Translator</div>
    </div>

    <div class='student-card'>
        <div class='student-tag'>◈ Task 8 — FUTO CSC 309</div>
        <div class='student-name'>Okoye Chukwuemeka <br>Paul</div>
        <div class='student-reg'>REG: 20231390632</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section-label'>🌍 Target Language</div>", unsafe_allow_html=True)
    selected_lang = st.selectbox("Language", list(languages.keys()), label_visibility="collapsed")

    st.markdown("<div class='sidebar-section-label'>🔄 Direction</div>", unsafe_allow_html=True)
    mode = st.radio(
        "Mode",
        [f"English  →  {selected_lang}", f"{selected_lang}  →  English"],
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️  Clear History"):
        st.session_state.history = []
        st.rerun()

    st.markdown(f"""
    <br>
    <div style='font-family:var(--font-mono);font-size:9px;letter-spacing:2px;color:#2a3a54;text-align:center;text-transform:uppercase;'>
        {len(st.session_state.history)} translation(s) logged
    </div>
    """, unsafe_allow_html=True)

# --- Direction Logic ---
if mode.startswith("English"):
    stt_lang_code = "en-US"
    mt_target_code = languages[selected_lang]['mt']
    input_label  = "English"
    output_label = selected_lang
else:
    stt_lang_code = languages[selected_lang]['stt']
    mt_target_code = "en"
    input_label  = selected_lang
    output_label = "English"

# --- HERO HEADER ---
st.markdown(f"""
<div class='hero-wrap'>
    <div class='hero-eyebrow'>◈ Bi-Directional Neural Translation</div>
    <h1 class='hero-title'>Vox<span>Bridge</span></h1>
    <p class='hero-subtitle'>Speak naturally. Translate instantly. Powered by Google Speech & Neural MT.</p>
    <div style='display:flex;justify-content:center;'>
        <div class='mode-badge'>
            <span class='mode-dot'></span>
            {input_label.upper()} &nbsp;→&nbsp; {output_label.upper()}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- TIP BOX ---
st.markdown("""
<div class='tip-wrap'>
    💡 <b>PRO TIP:</b> Speak clearly — the AI waits <b>2.5s of silence</b> before processing. Ensure your mic is enabled.
</div>
""", unsafe_allow_html=True)

# --- SPEAK BUTTON ---
col_l, col_c, col_r = st.columns([1, 2, 1])
with col_c:
    start_recording = st.button("🎙  TAP TO SPEAK")
    status_placeholder = st.empty()

st.markdown("<br>", unsafe_allow_html=True)

# --- RECORDING + TRANSLATION LOGIC ---
if start_recording:
    r = sr.Recognizer()
    r.pause_threshold = 2.5
    r.dynamic_energy_threshold = True

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)

        status_placeholder.markdown(f"""
<div class='status-wrap'>
    <div class='status-bars'>
        <div class='bar'></div><div class='bar'></div><div class='bar'></div>
        <div class='bar'></div><div class='bar'></div><div class='bar'></div><div class='bar'></div>
    </div>
    <span class='status-text' style='color:#00d4b4;'>LISTENING — {input_label.upper()}</span>
</div>
        """, unsafe_allow_html=True)

        try:
            audio = r.listen(source, timeout=10)

            status_placeholder.markdown("""
<div class='status-wrap'>
    <div class='spinner'></div>
    <span class='status-text' style='color:#ffd166;'>PROCESSING TRANSLATION...</span>
</div>
            """, unsafe_allow_html=True)

            spoken_text  = r.recognize_google(audio, language=stt_lang_code)
            translation  = translator.translate(spoken_text, dest=mt_target_code)

            st.session_state.history.insert(0, {
                "input_label":    input_label,
                "output_label":   output_label,
                "original_text":  spoken_text,
                "translated_text": translation.text
            })

            status_placeholder.markdown("""
<div class='status-wrap'>
    <span class='status-text' style='color:#00d4b4;'>✓ &nbsp;TRANSLATION COMPLETE</span>
</div>
            """, unsafe_allow_html=True)

        except sr.WaitTimeoutError:
            status_placeholder.empty()
            st.error("⏱ Listening timed out. No speech detected within 10 seconds.")
        except sr.UnknownValueError:
            status_placeholder.empty()
            st.warning(f"🎤 Could not transcribe audio in {input_label}. Please speak clearly and try again.")
        except Exception as e:
            status_placeholder.empty()
            st.error(f"⚠ Pipeline Error: {e}")

# --- TRANSCRIPT ---
if st.session_state.history:
    st.markdown("""
    <div class='transcript-header'>
        <div class='transcript-line'></div>
        <div class='transcript-label'>◈ Translation Transcript</div>
        <div class='transcript-line' style='background:linear-gradient(to left, var(--border), transparent);'></div>
    </div>
    """, unsafe_allow_html=True)

    for i, item in enumerate(st.session_state.history):
        n = len(st.session_state.history) - i
        st.markdown(f"""
<div class='t-card'>
    <div class='t-card-num'>#{n:02d}</div>
    <div class='t-label'>Detected {item['input_label']} Speech</div>
    <div class='t-original'>"{item['original_text']}"</div>
    <hr class='t-divider'>
    <div class='t-label-out'>→ {item['output_label']} Translation</div>
    <div class='t-translated'>{item['translated_text']}</div>
</div>
        """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div class='empty-state'>
        <div class='empty-icon'>🎙</div>
        <div class='empty-text'>No translations yet — tap the button above</div>
    </div>
    """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("<br><hr style='border:none;border-top:1px solid rgba(255,255,255,0.05);margin:10px 0;'>", unsafe_allow_html=True)
with st.expander("📊 Architectural Note (Lecturer)"):
    st.markdown("""
    **Pre-Trained Foundation Models via API Pipelines**

    This project uses no local training dataset. Instead, it integrates two cloud-based pre-trained systems:
    - **Google Web Speech API** — Speech-to-Text (STT), trained on millions of hours of audio
    - **Google Translate Neural MT** — Machine Translation, trained on billions of sentence pairs

    The 'dataset' in this context is the model weights residing on remote servers. This is an exercise in **AI Pipeline Integration** — a core skill in modern AI engineering.
    """)