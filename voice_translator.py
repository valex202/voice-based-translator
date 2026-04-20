import streamlit as st
import streamlit.components.v1 as components
import speech_recognition as sr
from deep_translator import GoogleTranslator
import base64, tempfile, os

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
[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"],[data-testid="collapsedControl"]{display:none!important;}
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
  💡 <b>HOW TO USE:</b> Choose language & direction below, then tap <b>🎙 TAP TO SPEAK</b> and allow mic access.
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

# ── BROWSER MIC RECORDER ──────────────────────────────────────
recorder_html = f"""<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@800&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{background:transparent;padding:4px;}}
#btn{{
  width:100%;padding:17px;border:none;border-radius:14px;
  background:linear-gradient(135deg,#00d4b4,#00a08a);
  color:#04060d;font-size:15px;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;
  cursor:pointer;transition:all .25s;box-shadow:0 0 28px rgba(0,212,180,.3);
  font-family:'Syne',sans-serif;
}}
#btn:hover{{transform:translateY(-2px);box-shadow:0 0 50px rgba(0,212,180,.5);}}
#btn.recording{{background:linear-gradient(135deg,#ff6b6b,#cc4444);box-shadow:0 0 28px rgba(255,107,107,.4);}}
#status{{
  margin-top:10px;padding:12px 16px;background:rgba(255,255,255,.03);
  border:1px solid rgba(255,255,255,.08);border-radius:10px;text-align:center;
  font-family:'Space Mono',monospace;font-size:11px;color:#6b7fa3;display:none;
}}
.bars{{display:inline-flex;align-items:center;gap:3px;height:18px;vertical-align:middle;margin-right:8px;}}
.b{{width:3px;border-radius:2px;background:#00d4b4;animation:eq .9s infinite ease-in-out;}}
.b:nth-child(1){{height:5px;animation-delay:0s;}}
.b:nth-child(2){{height:10px;animation-delay:.1s;}}
.b:nth-child(3){{height:16px;animation-delay:.2s;background:#ff6b6b;}}
.b:nth-child(4){{height:10px;animation-delay:.3s;}}
.b:nth-child(5){{height:5px;animation-delay:.4s;}}
@keyframes eq{{0%,100%{{transform:scaleY(1)}}50%{{transform:scaleY(2.2)}}}}
.spin{{display:inline-block;width:14px;height:14px;border:2px solid rgba(255,209,102,.2);border-top:2px solid #ffd166;border-radius:50%;animation:sp .8s linear infinite;vertical-align:middle;margin-right:8px;}}
@keyframes sp{{to{{transform:rotate(360deg)}}}}
</style></head><body>
<button id="btn" onclick="toggle()">🎙&nbsp; TAP TO SPEAK</button>
<div id="status"></div>
<script>
let rec, chunks=[], going=false, silTimer=null;

async function toggle(){{
  if(going){{ stop(); return; }}
  start();
}}

async function start(){{
  const btn=document.getElementById('btn'), st=document.getElementById('status');
  try{{
    const stream=await navigator.mediaDevices.getUserMedia({{audio:true}});
    rec=new MediaRecorder(stream);
    chunks=[];
    rec.ondataavailable=e=>{{if(e.data.size>0)chunks.push(e.data);}};
    rec.onstop=()=>{{
      stream.getTracks().forEach(t=>t.stop());
      st.innerHTML='<span class="spin"></span><span style="color:#ffd166">PROCESSING...</span>';
      const blob=new Blob(chunks,{{type:'audio/webm'}});
      const fr=new FileReader();
      fr.onloadend=()=>{{
        Streamlit.setComponentValue(fr.result.split(',')[1]);
      }};
      fr.readAsDataURL(blob);
      btn.className=''; btn.innerHTML='🎙&nbsp; TAP TO SPEAK'; going=false;
    }};

    // Silence detection
    const ctx=new AudioContext(), src=ctx.createMediaStreamSource(stream);
    const ana=ctx.createAnalyser(); ana.fftSize=512; src.connect(ana);
    const dat=new Uint8Array(ana.frequencyBinCount);
    let silStart=null;
    function chk(){{
      if(!going)return;
      ana.getByteFrequencyData(dat);
      const vol=dat.reduce((a,b)=>a+b,0)/dat.length;
      if(vol<5){{ if(!silStart)silStart=Date.now(); else if(Date.now()-silStart>2500){{stop();return;}} }}
      else silStart=null;
      requestAnimationFrame(chk);
    }}

    rec.start(); going=true;
    btn.className='recording'; btn.innerHTML='⏹&nbsp; RECORDING — tap to stop';
    st.style.display='block';
    st.innerHTML='<span class="bars"><span class="b"></span><span class="b"></span><span class="b"></span><span class="b"></span><span class="b"></span></span><span style="color:#00d4b4">LISTENING — {in_lbl.upper()} (auto-stops on silence)</span>';
    chk();
  }}catch(e){{
    st.style.display='block';
    st.innerHTML='<span style="color:#ff6b6b">⚠ Mic access denied. Please allow microphone access in your browser settings.</span>';
  }}
}}

function stop(){{
  if(rec&&going){{ rec.stop(); going=false; }}
}}
</script>
</body></html>"""

audio_b64 = components.html(recorder_html, height=120)

# ── PROCESS RECEIVED AUDIO ────────────────────────────────────
if audio_b64 and audio_b64 != st.session_state.get('_last_audio',''):
    st.session_state._last_audio = audio_b64
    with st.spinner("Transcribing & translating..."):
        try:
            audio_bytes = base64.b64decode(audio_b64)
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
                f.write(audio_bytes); tmp_webm = f.name

            tmp_wav = tmp_webm.replace(".webm",".wav")
            ret = os.system(f"ffmpeg -y -i {tmp_webm} {tmp_wav} -loglevel quiet 2>/dev/null")

            if ret != 0 or not os.path.exists(tmp_wav):
                st.error("⚠ Audio conversion failed. ffmpeg may not be available.")
            else:
                r = sr.Recognizer()
                with sr.AudioFile(tmp_wav) as src:
                    audio_rec = r.record(src)
                spoken = r.recognize_google(audio_rec, language=stt_code)
                translated = GoogleTranslator(source='auto', target=mt_code).translate(spoken)
                st.session_state.history.insert(0,{
                    "input_label":in_lbl,"output_label":out_lbl,
                    "original_text":spoken,"translated_text":translated
                })
                st.success(f"✓ **{out_lbl}:** {translated}")
            for p in [tmp_webm, tmp_wav]:
                try: os.unlink(p)
                except: pass
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
- **Browser MediaRecorder API** — captures mic audio directly on the user's device (no server mic needed)
- **Google Web Speech API** — Speech-to-Text, trained on millions of audio hours
- **Google Translate Neural MT** — trained on billions of sentence pairs

No local dataset. This is an exercise in **AI Pipeline Integration**.
    """)
