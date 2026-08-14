import streamlit as st
import requests
import librosa
import numpy as np
import matplotlib.pyplot as plt
import os
import re

st.set_page_config(page_title="YouTube Music BPM Finder", page_icon="🎵")

st.title("🎵 YouTube & YT Music BPM Detector")
st.write("Tempel link lagu dari **YouTube Music** atau **YouTube** untuk mendeteksi BPM secara instan.")

raw_url = st.text_input(
    "🔗 URL YouTube / YouTube Music:", 
    placeholder="https://music.youtube.com/watch?v=... atau https://youtu.be/..."
)

duration_option = st.selectbox(
    "⏱️ Durasi sampel analisis:",
    options=[30, 60, 90, "Penuh (Full Track)"],
    index=0
)

def clean_youtube_url(url):
    """Mengekstrak ID video dan mengonversi ke URL YouTube standar"""
    pattern = r"(?:v=|\/([0-9A-Za-z_-]{11})|youtu\.be\/|\/embed\/|\/v\/|watch\?v=|\&v=)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, url)
    if match:
        video_id = match.group(1) or match.group(2)
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"
    return url

if st.button("🚀 Analisis BPM", type="primary"):
    if not raw_url:
        st.warning("⚠️ Masukkan URL lagu terlebih dahulu.")
    else:
        # OTOMATIS BERSIHKAN URL (Buang &si=... dan ubah domain ke youtube.com)
        clean_url = clean_youtube_url(raw_url)
        
        temp_file = "temp_audio.mp3"
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass

        try:
            # 1. Ambil Audio via Public API Proxy
            with st.spinner("📥 Mengunduh audio trek..."):
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
                payload = {
                    "url": clean_url,
                    "downloadMode": "audio",
                    "audioFormat": "mp3"
                }
                
                api_res = requests.post("https://api.cobalt.tools/", json=payload, headers=headers, timeout=20)
                data = api_res.json()

                if "url" in data:
                    audio_data = requests.get(data["url"]).content
                    with open(temp_file, "wb") as f:
                        f.write(audio_data)
                else:
                    st.error("❌ Gagal mengambil audio. Coba gunakan tautan lain atau pastikan video tidak di-private.")
                    st.stop()

            # 2. Analisis BPM dengan Librosa
            with st.spinner("🎼 Menganalisis tempo (BPM)..."):
                load_duration = None if duration_option == "Penuh (Full Track)" else float(duration_option)
                y, sr = librosa.load(temp_file, duration=load_duration)
                
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
                bpm = float(tempo[0]) if hasattr(tempo, "__len__") else float(tempo)

            # 3. Hasil & Visualisasi Waveform
            st.success("✅ Selesai!")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric(label="🥁 Estimasi Tempo", value=f"{round(bpm)} BPM")
            with col2:
                st.audio(temp_file, format="audio/mp3")

            # Plot Waveform
            fig, ax = plt.subplots(figsize=(8, 2.5), facecolor='none')
            times = librosa.times_like(y, sr=sr)
            ax.plot(times, y, color='#FF0000', alpha=0.7, linewidth=0.7)
            ax.set_axis_off()
            st.pyplot(fig)

        except Exception as e:
            st.error(f"❌ Terjadi kesalahan: {e}")
            
        finally:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass
