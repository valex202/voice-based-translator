import streamlit as st
import speech_recognition as sr
from deep_translator import GoogleTranslator

st.set_page_config(
    page_title="VoxBridge | AI Translator",
    page_icon="🌐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

for k, v in [('history',[]),('sel_lang','Igbo'),('to_eng',False)]:
    if k not in st.session_state:
        st.session_state[k] = v

languages = {
    'Igbo':{'mt':'ig','stt':'ig-NG'},'Hausa':{'mt':'ha','stt':'ha-NG'},
    'Yoruba':{'mt':'yo','stt':'yo-NG'},'French':{'mt':'fr','stt':'fr-FR'},
    'Spanish':{'mt':'es','stt':'es-ES'},'German':{'mt':'de','stt':'de-DE'},
    'Chinese':{'mt':'zh-cn','stt':'zh-CN'},'Arabic':{'mt':'ar','stt':'ar-SA'},
    'Swahili':{'mt':'sw','stt':'sw-KE'},'Portuguese':{'mt':'pt','stt':'pt-PT'},
}

lang     = st.session_state.sel_lang
to_eng   = st.session_state.to_eng
in_lbl   = lang if to_eng else "English"
out_lbl  = "English" if to_eng else lang
stt_code = languages[lang]['stt'] if to_eng else "en-US"
mt_code  = "en" if to_eng else languages[lang]['mt']

# ─── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');
*{box-sizing:border-box;margin:0;padding:0;}
#MainMenu,footer,header{visibility:hidden;}

/* Note: The CSS rules hiding the sidebar toggler have been completely removed! */

:root{
  --bg:#04060d;--card:rgba(255,255,255,.04);--border:rgba(255,255,255,.08);
  --accent:#00d4b4;--red:#ff6b6b;--gold:#ffd166;--fg:#eef2f7;--muted:#6b7fa3;--dim:#2e3d55;
  --F:'Syne',sans-serif;--M:'Space Mono',monospace;--B:'DM Sans',sans-serif;
}
.stApp{
  background:var(--bg);
  background-image:radial-gradient(ellipse 90% 50% at 15% 0%,rgba(0,212,180,.1) 0%,transparent 60%),
                   radial-gradient(ellipse 60% 40% at 85% 100%,rgba(255,107,107,.07) 0%,transparent 55%);
  font-family:var(--B);color:var(--fg);min-height:100vh;
}
.block-container{padding:1rem 1rem 5rem!important;max-width:680px!important;margin:0 auto!important;}
.hero{text-align:center;padding:4rem 0 1rem;}
.hero-eye{font-family:var(--M);font-size:9px;letter-spacing:5px;text-transform:uppercase;color:var(--accent);margin-bottom:12px;opacity:.8;}
.hero-title{font-family:var(--F);font-size:clamp(28px,8vw,52px);font-weight:800;letter-spacing:-2px;line-height:1.05;}
.hero-title span{color:var(--accent);}
.hero-sub{font-size:13px;color:var(--muted);margin:8px auto 0;max-width:400px;line-height:1.6;}
.pill{display:inline-flex;align-items:center;gap:8px;background:rgba(0,212,180,.08);border:1px solid rgba(0,212,180,.2);border-radius:50px;padding:5px 14px;font-family:var(--M);font-size:10px;color:var(--accent);letter-spacing:1px;margin-top:14px;}
.dot{width:6px;height:6px;border-radius:50%;background:var(--accent);animation:pd 2s infinite;}
@keyframes pd{0%,100%{opacity:1;transform:scale(1);}50%{opacity:.4;transform:scale(.6);}}
.tip{background:rgba(255,209,102,.05);border:1px solid rgba(255,209,102,.15);border-radius:12px;padding:11px 18px;font-size:12px;color:var(--muted);text-align:center;margin:14px 0;}
.tip b{color:var(--gold);}
.tr-head{display:flex;align-items:center;gap:10px;margin:28px 0 14px;}
.tr-line{flex:1;height:1px;background:linear-gradient(to right,var(--border),transparent);}
.tr-lbl{font-family:var(--M);font-size:9px;letter-spacing:4px;text-transform:uppercase;color:var(--dim);white-space:nowrap;}
.card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px 22px;margin-bottom:14px;position:relative;overflow:hidden;transition:all .2s;}
.card::before{content:'';position:absolute;top:0;left:0;width:3px;height:100%;background:linear-gradient(to bottom,var(--accent),transparent);}
.card:hover{transform:translateY(-2px);box-shadow:0 10px 30px rgba(0,0,0,.3);}
.c-num{font-family:var(--M);font-size:9px;color:var(--dim);position:absolute;top:14px;right:16px;}
.c-lbl{font-family:var(--M);font-size:9px;letter-spacing:3px;text-transform:uppercase;color:var(--dim);margin-bottom:5px;}
.c-orig{font-size:14px;color:#8da0bb;font-style:italic;margin-bottom:14px;line-height:1.5;}
.c-lbl2{font-family:var(--M);font-size:9px;letter-spacing:3px;text-transform:uppercase;color:var(--accent);margin-bottom:5px;opacity:.8;}
.c-trans{font-family:var(--F);font-size:clamp(18px,5vw,24px);font-weight:700;color:var(--fg);line-height:1.2;letter-spacing:-.5px;}
.c-div{border:none;border-top:1px solid var(--border);margin:12px 0;}
.empty{text-align:center;padding:50px 20px;font-family:var(--M);font-size:10px;letter-spacing:3px;text-transform:uppercase;color:var(--dim);}
.stAlert{border-radius:12px!important;}
.stExpander{border:1px solid var(--border)!important;border-radius:12px!important;}

/* settings panel styling */
.settings-wrap{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:20px;margin-bottom:20px;}
.settings-title{font-family:var(--M);font-size:9px;letter-spacing:4px;text-transform:uppercase;color:var(--dim);margin-bottom:16px;}
</style>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────
st.markdown(f"""
<div class='hero'>
  <div class='hero-eye'>◈ Bi-Directional Neural Translation</div>
  <div class='hero-title'>Vox<span>Bridge</span></div>
  <div class='hero-sub'>Speak naturally. Translate instantly.</div>
  <div style='display:flex;justify-content:center;'>
    <div class='pill'><span class='dot'></span>{in_lbl.upper()} → {out_lbl.upper()}</div>
  </div>
</div>
<div class='tip'>
  💡 <b>HOW TO USE:</b> Choose language & direction below, then tap the mic icon to record.
</div>
""", unsafe_allow_html=True)

# ── SETTINGS (inline, always visible, no sidebar) ─────────────
st.markdown("<div class='settings-wrap'><div class='settings-title'>◈ Settings</div>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    new_lang = st.selectbox("🌍 Language", list(languages.keys()),
                             index=list(languages.keys()).index(st.session_state.sel_lang))
with c2:
    dir_choice = st.radio("🔄 Direction",
                           [f"EN → {new_lang}", f"{new_lang} → EN"],
                           horizontal=False)
st.markdown("</div>", unsafe_allow_html=True)

new_to_eng = dir_choice.endswith("→ EN")
if new_lang != st.session_state.sel_lang or new_to_eng != st.session_state.to_eng:
    st.session_state.sel_lang = new_lang
    st.session_state.to_eng   = new_to_eng
    st.rerun()

# ── NATIVE MIC RECORDER ──────────────────────────────────────
audio_file = st.audio_input("🎙 TAP TO RECORD")

# ── PROCESS RECEIVED AUDIO ────────────────────────────────────
if audio_file is not None and audio_file != st.session_state.get('_last_audio', None):
    st.session_state._last_audio = audio_file
    
    with st.spinner("Transcribing & translating..."):
        try:
            r = sr.Recognizer()
            with sr.AudioFile(audio_file) as src:
                audio_rec = r.record(src)
                
            spoken = r.recognize_google(audio_rec, language=stt_code)
            translated = GoogleTranslator(source='auto', target=mt_code).translate(spoken)
            
            st.session_state.history.insert(0,{
                "input_label":in_lbl,
                "output_label":out_lbl,
                "original_text":spoken,
                "translated_text":translated
            })
            st.success(f"✓ **{out_lbl}:** {translated}")
            
        except sr.UnknownValueError:
            st.warning("🎤 Could not understand. Speak clearly and try again.")
        except Exception as e:
            st.error(f"⚠ Error: {e}")

# ── CLEAR ──────────────────────────────────────────────────────
col_a, col_b = st.columns([3,1])
with col_b:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# ── TRANSCRIPT ─────────────────────────────────────────────────
if st.session_state.history:
    st.markdown("""<div class='tr-head'>
      <div class='tr-line'></div><div class='tr-lbl'>◈ Transcript</div>
      <div class='tr-line' style='background:linear-gradient(to left,var(--border),transparent)'></div>
    </div>""", unsafe_allow_html=True)
    for i,item in enumerate(st.session_state.history):
        n=len(st.session_state.history)-i
        st.markdown(f"""<div class='card'>
  <div class='c-num'>#{n:02d}</div>
  <div class='c-lbl'>Detected {item['input_label']} Speech</div>
  <div class='c-orig'>"{item['original_text']}"</div>
  <hr class='c-div'>
  <div class='c-lbl2'>→ {item['output_label']}</div>
  <div class='c-trans'>{item['translated_text']}</div>
</div>""", unsafe_allow_html=True)
else:
    st.markdown("<div class='empty'>🎙<br><br>No translations yet</div>", unsafe_allow_html=True)

with st.expander("📊 Architectural Note (Lecturer)"):
    st.markdown("""
**Pre-Trained Foundation Models via API Pipelines**
- **Streamlit Native Audio** — captures mic audio directly natively on the browser
- **Google Web Speech API** — Speech-to-Text, trained on millions of audio hours
- **Google Translate Neural MT** — trained on billions of sentence pairs

No local dataset. This is an exercise in **AI Pipeline Integration**.
    """)
