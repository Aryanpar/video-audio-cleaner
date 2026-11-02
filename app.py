import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import numpy as np
import soundfile as sf
import streamlit as st
import noisereduce as nr

st.set_page_config(
    page_title="Ethereal — Audio Studio",
    page_icon="✳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Visual system ----------
st.markdown(
    """
    <style>
    :root {
      --ink: #202238; --muted: #555b73; --subtle: #687087;
      --line: #dce1ee; --paper: #f7f8fc; --white: #ffffff;
      --violet: #5144b8; --violet-dark: #403494;
    }
    /* Remove Streamlit's translucent top chrome and Deploy controls. */
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
    #MainMenu, footer { display: none !important; visibility: hidden !important; height: 0 !important; }
    [data-testid="stAppViewContainer"], [data-testid="stMain"] {
      background: linear-gradient(180deg, #f7f8fc 0%, #ffffff 42%, #f8f9fd 100%);
      color: var(--ink);
    }
    html, body { color: var(--ink); }
    .block-container { max-width: 1120px; padding: 1.2rem 1.35rem 3rem; }
    /* Improve contrast across Streamlit's native labels and copy. */
    [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li, [data-testid="stCaptionContainer"],
    [data-testid="stWidgetLabel"] p, label, .stRadio label, .stCheckbox label {
      color: #343951 !important;
    }
    [data-testid="stCaptionContainer"] { color: #5f667d !important; }
    .appbar { display:flex; justify-content:space-between; align-items:center; gap:1rem;
      padding:.25rem .1rem 1.15rem; border-bottom:1px solid #e0e4ef; margin-bottom:1.35rem; }
    .brand { display:flex; align-items:center; gap:.7rem; font-weight:800; letter-spacing:-.025em; color:#22253d; font-size:1.05rem; }
    .brand-icon { width:2.45rem; height:2.45rem; border-radius:13px; display:flex; align-items:center; justify-content:center;
      color:#fff; font-size:1.3rem; background:#5144b8; box-shadow:0 4px 12px rgba(81,68,184,.18); }
    .app-status { color:#35405a; font-size:.8rem; border:1px solid #dce3ef; background:#fff; border-radius:999px; padding:.45rem .75rem; white-space:nowrap; }
    .hero { position:relative; overflow:hidden; border-radius:24px; padding:clamp(1.5rem,4vw,3rem);
      background:linear-gradient(115deg,#ffffff 0%,#f0efff 58%,#eaf5ff 100%);
      border:1px solid #e0e3f0; box-shadow:0 12px 32px rgba(36,43,83,.06); margin-bottom:1.5rem; }
    .hero:after { content:"✳"; position:absolute; right:5%; top:5%; font-size:clamp(5rem,11vw,9rem); color:rgba(81,68,184,.09); pointer-events:none; }
    .eyebrow { font-size:.75rem; font-weight:800; text-transform:uppercase; letter-spacing:.12em; color:#5144b8; margin-bottom:.85rem; }
    .hero h1 { max-width:680px; margin:0; color:#202238; font-size:clamp(2.2rem,5vw,3.8rem); line-height:1.06; letter-spacing:-.05em; font-weight:800; }
    .hero p { max-width:650px; margin:1rem 0 0; font-size:1.02rem; line-height:1.65; color:#454b64; }
    .hero-meta { display:flex; flex-wrap:wrap; gap:.55rem; margin-top:1.3rem; }
    .meta-chip { font-size:.78rem; color:#3e4560; border:1px solid #d9deef; background:#fff; padding:.42rem .7rem; border-radius:999px; }
    .section-head { display:flex; align-items:flex-start; gap:.8rem; margin:1.65rem 0 .8rem; }
    .step-no { flex:0 0 2.1rem; height:2.1rem; border-radius:11px; display:flex; align-items:center; justify-content:center; background:#e8e7ff; color:#403494; font-size:.85rem; font-weight:850; }
    .section-title { font-size:1.1rem; font-weight:800; letter-spacing:-.02em; color:#242840; line-height:1.35; margin:.05rem 0 .2rem; }
    .section-desc { color:#555c75; font-size:.9rem; line-height:1.55; }
    .upload-hint { color:#555c75; font-size:.86rem; line-height:1.6; margin-top:.4rem; }
    div[data-testid="stFileUploader"] { background:#fff; border:1.5px dashed #9c9acb; border-radius:16px; padding:.65rem; }
    div[data-testid="stFileUploader"] section { border:0; background:transparent; }
    /* Streamlit's upload button uses its own BaseButton styles; force readable contrast. */
    div[data-testid="stFileUploader"] button,
    div[data-testid="stFileUploader"] button * {
      color:#292e47 !important;
      opacity:1 !important;
    }
    div[data-testid="stFileUploader"] button {
      background:#f0efff !important;
      border:1px solid #8f88d4 !important;
      border-radius:10px !important;
      font-weight:750 !important;
      min-height:2.6rem;
    }
    div[data-testid="stFileUploader"] button:hover {
      background:#e4e1ff !important;
      border-color:#5144b8 !important;
    }
    div[data-testid="stRadio"] > div { gap:.6rem; }
    div[data-testid="stRadio"] label, div[data-testid="stSelectbox"] label,
    div[data-testid="stSlider"] label, div[data-testid="stSelectSlider"] label,
    div[data-testid="stFileUploader"] label { color:#292e47 !important; font-weight:700; font-size:.92rem; }
    /* Inputs should look like controls, not low-contrast decoration. */
    [data-baseweb="select"] > div, [data-baseweb="input"] > div,
    [data-testid="stTextInput"] input { background:#fff !important; border-color:#cbd2e3 !important; color:#252a42 !important; }
    [data-baseweb="select"] *, [data-baseweb="popover"] *, [role="radiogroup"] * { color:#252a42; }
    div[data-testid="stButton"] button, div[data-testid="stDownloadButton"] button,
    div[data-testid="stLinkButton"] a { min-height:3rem; border-radius:12px; font-weight:750;
      border:1px solid #cbd2e3; background:#fff; color:#292e47 !important; transition:background .15s ease,border-color .15s ease,transform .15s ease; }
    /* Support both newer and older Streamlit button DOM structures. */
    div[data-testid="stBaseButton-primary"],
    div[data-testid="stBaseButton-primary"] *,
    div[data-testid="stButton"] button[kind="primary"],
    div[data-testid="stDownloadButton"] button[kind="primary"],
    div[data-testid="stLinkButton"] a[kind="primary"] {
      background:#5144b8 !important; color:#fff !important; border-color:#5144b8 !important;
      opacity:1 !important;
    }
    div[data-testid="stBaseButton-primary"] *,
    div[data-testid="stButton"] button[kind="primary"] *,
    div[data-testid="stDownloadButton"] button[kind="primary"] *,
    div[data-testid="stLinkButton"] a[kind="primary"] * { color:#fff !important; opacity:1 !important; }
    div[data-testid="stBaseButton-primary"]:hover,
    div[data-testid="stButton"] button[kind="primary"]:hover,
    div[data-testid="stDownloadButton"] button[kind="primary"]:hover {
      background:#403494 !important; border-color:#403494 !important; transform:translateY(-1px); }
    div[data-testid="stButton"] button:not([kind="primary"]):hover,
    div[data-testid="stDownloadButton"] button:not([kind="primary"]):hover { background:#f0efff !important; border-color:#8b83d4 !important; }
    div[data-testid="stButton"] button:disabled,
    div[data-testid="stBaseButton-primary"]:disabled { background:#e7e9f1 !important; color:#747b90 !important; border-color:#d8dce7 !important; box-shadow:none; }
    div[data-testid="stButton"] button:disabled *, div[data-testid="stBaseButton-primary"]:disabled * { color:#747b90 !important; }
    div[data-testid="stAudio"] { border-radius:12px; overflow:hidden; margin:.4rem 0 .75rem; }
    div[data-testid="stAlert"] { border-radius:12px; }
    [data-testid="stProgressBar"] > div { background:#e5e3f7; }
    [data-testid="stProgressBar"] > div > div { background:#5144b8; }
    .file-summary { display:flex; align-items:center; gap:.8rem; background:#f0efff; border:1px solid #dcd9fa; padding:.85rem .9rem; border-radius:14px; margin-top:.75rem; }
    .file-symbol { width:2.5rem; height:2.5rem; flex:0 0 2.5rem; display:flex; align-items:center; justify-content:center; background:#dedbff; color:#403494; border-radius:11px; font-size:1.1rem; }
    .file-name { font-weight:750; font-size:.92rem; color:#272b45; overflow-wrap:anywhere; }
    .file-detail { color:#555c75; font-size:.8rem; margin-top:.18rem; }
    .result-card { background:#fff; border:1px solid #dfe3ee; border-radius:16px; padding:1rem; height:100%; }
    .result-label { color:#555c75; font-size:.75rem; text-transform:uppercase; letter-spacing:.08em; font-weight:800; margin-bottom:.35rem; }
    .result-name { color:#242840; font-size:1rem; font-weight:800; overflow-wrap:anywhere; }
    .result-desc { color:#555c75; font-size:.86rem; line-height:1.55; margin:.35rem 0 .6rem; }
    .success-banner { border:1px solid #a9dfc7; background:#effaf4; color:#205e45; border-radius:12px; padding:.85rem 1rem; font-size:.92rem; margin:.7rem 0 1rem; }
    .footnote { text-align:center; color:#71778b; font-size:.78rem; padding:2rem .5rem .2rem; }
    @media (max-width: 768px) {
      .block-container { padding:.75rem .75rem 2rem; }
      .appbar { margin-bottom:1rem; padding-bottom:.9rem; }
      .app-status { font-size:.7rem; padding:.35rem .55rem; }
      .hero { padding:1.4rem 1.1rem; border-radius:19px; margin-bottom:1.1rem; }
      .hero h1 { font-size:2.25rem; max-width:100%; }
      .hero p { font-size:.96rem; line-height:1.6; }
      .hero:after { right:0; top:1%; font-size:5rem; }
      .section-head { margin-top:1.3rem; }
      .meta-chip { font-size:.72rem; padding:.36rem .58rem; }
      div[data-testid="stButton"] button, div[data-testid="stDownloadButton"] button { width:100%; }
    }
    @media (max-width: 420px) {
      .brand { font-size:.88rem; gap:.5rem; }
      .brand-icon { width:2.1rem; height:2.1rem; border-radius:11px; }
      .app-status { max-width:115px; white-space:normal; text-align:center; }
      .hero h1 { font-size:1.95rem; }
      .block-container { padding-left:.55rem; padding-right:.55rem; }
      .section-title { font-size:1rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="appbar">
      <div class="brand"><span class="brand-icon">✳</span><span>Ethereal <span style="font-weight:500;color:#817c9d">/ Audio Studio</span></span></div>
      <div class="app-status">● &nbsp; Private local processing</div>
    </div>
    <section class="hero">
      <div class="eyebrow">VIDEO TO AUDIO · SIMPLE AND PRIVATE</div>
      <h1>Get clear audio<br>from your video.</h1>
      <p>Upload a video, choose whether to reduce background noise, preview the result, and download your audio. No editing experience needed.</p>
      <div class="hero-meta">
        <span class="meta-chip">No account needed</span>
        <span class="meta-chip">Processed locally on this computer</span>
        <span class="meta-chip">MP3 · WAV · AAC · FLAC</span>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

if shutil.which("ffmpeg") is None:
    st.error("FFmpeg was not found. Add the folder containing ffmpeg.exe to your Windows user Path, then restart the terminal.")
    st.link_button("FFmpeg Windows builds", "https://www.gyan.dev/ffmpeg/builds/")
    st.stop()

# Workflow step 1
st.markdown(
    '<div class="section-head"><div class="step-no">01</div><div><div class="section-title">Choose your source</div><div class="section-desc">Step 1: Upload a video from your device. Supported formats are listed below the upload control.</div></div></div>',
    unsafe_allow_html=True,
)
uploaded = st.file_uploader(
    "Upload video",
    type=["mp4", "mov", "mkv", "avi", "webm", "m4v", "mpeg", "mpg"],
    help="MP4, MOV, MKV, AVI, WebM and other common video formats.",
    label_visibility="collapsed",
)
if uploaded:
    st.markdown(
        f"""
        <div class="file-summary">
          <div class="file-symbol">▶</div>
          <div style="min-width:0">
            <div class="file-name">{uploaded.name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</div>
            <div class="file-detail">Video selected · {uploaded.size / (1024 * 1024):.1f} MB</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown('<div class="upload-hint">Tip: a short clip is best for your first test. Large videos may take longer to process.</div>', unsafe_allow_html=True)

# Workflow step 2
st.markdown(
    '<div class="section-head"><div class="step-no">02</div><div><div class="section-title">Set your preferences</div><div class="section-desc">Step 2: Choose an option. If you are unsure, keep the default settings and try a short clip first.</div></div></div>',
    unsafe_allow_html=True,
)
settings = st.container(border=True)
with settings:
    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        mode = st.radio(
            "Audio treatment",
            ["Extract only", "Reduce background noise"],
            help="Noise reduction is most effective on steady sounds such as fan hum and hiss.",
        )
        strength = st.slider(
            "Noise reduction amount",
            min_value=0.1, max_value=1.0, value=0.6, step=0.1,
            disabled=(mode == "Extract only"),
            help="Start around 0.5–0.7. Higher settings may make voices sound artificial.",
        )
    with col_b:
        output_format = st.selectbox("File format", ["MP3", "WAV", "M4A (AAC)", "FLAC", "AAC"])
        if output_format == "MP3":
            quality = st.select_slider("MP3 quality", options=["96 kbps", "128 kbps", "192 kbps", "256 kbps", "320 kbps"], value="192 kbps")
        elif output_format in ["M4A (AAC)", "AAC"]:
            quality = st.select_slider("AAC quality", options=["96 kbps", "128 kbps", "192 kbps", "256 kbps"], value="192 kbps")
        else:
            quality = "Lossless / format default"
            st.caption("WAV and FLAC preserve audio without lossy compression.")

process = st.button("Create my audio", type="primary", disabled=(uploaded is None), use_container_width=True)

if process and uploaded is not None:
    started = time.time()
    progress = st.progress(0, text="Preparing your file…")
    status = st.empty()

    with tempfile.TemporaryDirectory(prefix="ethereal_audio_") as tmp:
        work = Path(tmp)
        original_name = Path(uploaded.name).name
        video_path = work / original_name
        raw_wav = work / "original_audio.wav"
        cleaned_wav = work / "cleaned_audio.wav"
        output_ext = {"MP3": "mp3", "WAV": "wav", "M4A (AAC)": "m4a", "FLAC": "flac", "AAC": "aac"}[output_format]
        output_path = work / f"{Path(original_name).stem}_audio.{output_ext}"
        video_path.write_bytes(uploaded.getvalue())

        try:
            status.info("Step 1 of 3 · Extracting audio")
            result = subprocess.run(
                ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video_path),
                 "-vn", "-ac", "2", "-ar", "44100", "-c:a", "pcm_s16le", str(raw_wav)],
                capture_output=True, text=True,
            )
            if result.returncode != 0 or not raw_wav.exists():
                st.error("We couldn't extract audio from this video. It may not contain an audio track or may use an unsupported codec.")
                with st.expander("Technical details"):
                    st.code((result.stderr or "No additional details returned.")[-4000:])
                st.stop()

            progress.progress(30, text="Audio extracted")
            source_wav = raw_wav

            if mode == "Reduce background noise":
                status.info("Step 2 of 3 · Reducing background noise")
                audio, sample_rate = sf.read(str(raw_wav), dtype="float32", always_2d=True)
                cleaned_channels = []
                for channel_index in range(audio.shape[1]):
                    cleaned_channel = nr.reduce_noise(
                        y=audio[:, channel_index], sr=sample_rate,
                        prop_decrease=float(strength), stationary=False,
                    )
                    cleaned_channels.append(cleaned_channel)
                cleaned = np.clip(np.stack(cleaned_channels, axis=1), -1.0, 1.0)
                sf.write(str(cleaned_wav), cleaned, sample_rate, subtype="PCM_16")
                source_wav = cleaned_wav
            else:
                progress.progress(58, text="Audio ready")

            progress.progress(68, text="Preparing export")
            status.info(f"Step 3 of 3 · Creating {output_format}")
            if output_format == "WAV":
                shutil.copyfile(source_wav, output_path)
                result = None
            else:
                if output_format == "MP3":
                    codec_args = ["-c:a", "libmp3lame", "-b:a", quality.split()[0]]
                elif output_format in ["M4A (AAC)", "AAC"]:
                    codec_args = ["-c:a", "aac", "-b:a", quality.split()[0]]
                else:
                    codec_args = ["-c:a", "flac"]
                result = subprocess.run(
                    ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source_wav),
                     *codec_args, str(output_path)],
                    capture_output=True, text=True,
                )

            if result is not None and (result.returncode != 0 or not output_path.exists()):
                st.error("The selected audio format could not be created.")
                with st.expander("Technical details"):
                    st.code((result.stderr or "No additional details returned.")[-4000:])
                st.stop()

            output_bytes = output_path.read_bytes()
            progress.progress(100, text="Complete")
            status.success(f"Ready in {time.time() - started:.1f} seconds.")

            st.markdown(
                '<div class="section-head"><div class="step-no">03</div><div><div class="section-title">Listen before you save</div><div class="section-desc">Compare the source with your processed audio, then download your export.</div></div></div>',
                unsafe_allow_html=True,
            )
            left_preview, right_preview = st.columns(2, gap="large")
            with left_preview:
                st.markdown(
                    '<div class="result-card"><div class="result-label">Source</div><div class="result-name">Original audio</div><div class="result-desc">The soundtrack extracted from your video.</div></div>',
                    unsafe_allow_html=True,
                )
                st.audio(raw_wav.read_bytes(), format="audio/wav")
            with right_preview:
                if mode == "Reduce background noise":
                    st.markdown(
                        '<div class="result-card"><div class="result-label">Processed</div><div class="result-name">Noise-reduced audio</div><div class="result-desc">Check that the voice sounds natural and clear.</div></div>',
                        unsafe_allow_html=True,
                    )
                    st.audio(cleaned_wav.read_bytes(), format="audio/wav")
                else:
                    st.markdown(
                        '<div class="result-card"><div class="result-label">Processing option</div><div class="result-name">Noise reduction off</div><div class="result-desc">Select “Reduce background noise” to create a cleaned comparison.</div></div>',
                        unsafe_allow_html=True,
                    )

            mime_types = {"MP3": "audio/mpeg", "WAV": "audio/wav", "M4A (AAC)": "audio/mp4", "FLAC": "audio/flac", "AAC": "audio/aac"}
            st.markdown('<div class="success-banner">Your audio is ready. Preview it above, then save a copy to your device.</div>', unsafe_allow_html=True)
            st.audio(output_bytes, format=mime_types[output_format])
            st.download_button(
                f"Download {output_path.name}",
                data=output_bytes,
                file_name=output_path.name,
                mime=mime_types[output_format],
                type="primary",
                use_container_width=True,
            )
            st.caption(f"Export size: {len(output_bytes) / (1024 * 1024):.2f} MB. Temporary processing files are removed after this run.")
        except MemoryError:
            st.error("This video used more memory than available. Try a shorter clip or extract audio without noise reduction.")
        except Exception as exc:
            st.error(f"Processing failed: {exc}")
            st.info("Try a short MP4 first. If the issue continues, share the full terminal error.")

st.markdown(
    '<div class="footnote">ETHEREAL AUDIO STUDIO &nbsp;·&nbsp; Thoughtful tools for clearer sound</div>',
    unsafe_allow_html=True,
)
