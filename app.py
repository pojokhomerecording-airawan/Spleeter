import streamlit as st
import requests
import librosa
import numpy as np
import matplotlib.pyplot as plt
import os

st.set_page_config(
    page_title="YouTube BPM Detector",
    page_icon="🎵",
    layout="centered"
)

st.markdown("<h1 style='text-align: center;'>🎵 YouTube BPM Detector</h1>", unsafe_allow_html=True)
st.write("Masukkan URL YouTube **atau** upload file audio secara manual untuk menganalisis BPM dan melihat bentuk gelombang audionya.")

# Pilihan Input: Link YouTube atau Upload File
tab1, tab2 = st.tabs(["🔗 Tautan YouTube", "📁 Unggah File Audio"])

audio_path = None

with tab1:
    url = st.text_input("URL YouTube:", placeholder="https://www.youtube.com/watch?v=...")
    duration_option = st.selectbox(
        "⏱️ Durasi sampel analisis:",
        options=[30, 60, 90, 120, "Penuh (Full Track)"],
        index=0,
        key="yt_duration"
    )
    analyze_yt = st.button("🚀 Analisis Tautan YouTube", type="primary")

with tab2:
    uploaded_file = st.file_uploader("Pilih file audio (.mp3, .wav, .m4a):", type=["mp3", "wav", "m4a"])
    analyze_file = st.button("🚀 Analisis File Audio", type="primary")

# PROSES 1: Jika user menggunakan URL YouTube
if analyze_yt:
    if not url:
        st.warning("⚠️ Silakan masukkan URL YouTube terlebih dahulu.")
    else:
        temp_file = "temp_youtube.mp3"
        if os.path.exists(temp_file):
            os.remove(temp_file)

        try:
            with st.spinner("📥 1/3 Memproses dan mengambil audio via API Bypass..."):
                # Request ke API Cobalt untuk melewati blokir IP 403
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
                payload = {
                    "url": url,
                    "downloadMode": "audio",
                    "audioFormat": "mp3"
                }
                
                api_res = requests.post("https://api.cobalt.tools/", json=payload, headers=headers)
                data = api_res.json()

                if "url" in data:
                    # Unduh file audio dari link proxy yang diberikan
                    audio_data = requests.get(data["url"]).content
                    with open(temp_file, "wb") as f:
                        f.write(audio_data)
                    audio_path = temp_file
                else:
                    st.error("❌ Gagal mengambil audio dari YouTube. Coba tautan lain atau gunakan fitur upload file.")

        except Exception as e:
            st.error(f"❌ Terjadi kesalahan pengunduhan: {e}")

# PROSES 2: Jika user mengunggah file manual
if analyze_file:
    if uploaded_file is not None:
        temp_file = f"temp_upload_{uploaded_file.name}"
        with open(temp_file, "wb") as f:
            f.write(uploaded_file.getbuffer())
        audio_path = temp_file
        duration_option = "Penuh (Full Track)"
    else:
        st.warning("⚠️ Silakan pilih file audio terlebih dahulu.")

# PROSES ANALISIS BPM & WAVEFORM (Sama untuk kedua input)
if audio_path and os.path.exists(audio_path):
    try:
        with st.spinner("🎼 2/3 Menganalisis tempo (BPM)..."):
            load_duration = None if duration_option == "Penuh (Full Track)" else float(duration_option)
            y, sr = librosa.load(audio_path, duration=load_duration)
            
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            bpm = float(tempo[0]) if hasattr(tempo, "__len__") else float(tempo)

        with st.spinner("📊 3/3 Memproses visualisasi waveform..."):
            fig, ax = plt.subplots(figsize=(10, 3.5), facecolor='none')
            times = librosa.times_like(y, sr=sr)
            ax.plot(times, y, color='#1DB954', alpha=0.8, linewidth=0.8)
            ax.set_title("Audio Waveform", fontsize=12, color='gray', pad=10)
            ax.set_xlabel("Waktu (Detik)", fontsize=10)
            ax.set_ylabel("Amplitudo", fontsize=10)
            ax.grid(True, linestyle='--', alpha=0.3)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            plt.tight_layout()

        st.success("✅ Analisis Selesai!")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric(label="🥁 Estimated BPM", value=f"{bpm:.1f} BPM")
        with col2:
            st.audio(audio_path)

        st.write("---")
        st.subheader("📈 Visualisasi Bentuk Gelombang (Waveform)")
        st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ Gagal menganalisis audio: {e}")
        
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
