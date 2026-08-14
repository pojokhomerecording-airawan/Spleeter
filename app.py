import streamlit as st
from pytubefix import YouTube
import librosa
import numpy as np
import matplotlib.pyplot as plt
import os

st.set_page_config(
    page_title="YouTube BPM Detector",
    page_icon="🎵",
    layout="centered"
)

# Custom Styling
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🎵 YouTube BPM Detector</h1>", unsafe_allow_html=True)
st.write("Masukkan URL video/musik YouTube di bawah ini untuk mengunduh audio, menganalisis tempo (BPM), serta menampilkan visualisasi gelombang audionya.")

url = st.text_input("🔗 URL YouTube:", placeholder="https://www.youtube.com/watch?v=...")

duration_option = st.selectbox(
    "⏱️ Durasi sampel analisis (semakin pendek semakin cepat):",
    options=[30, 60, 90, 120, "Penuh (Full Track)"],
    index=0
)

if st.button("🚀 Analisis BPM & Waveform", type="primary"):
    if not url:
        st.warning("⚠️ Silakan masukkan URL YouTube terlebih dahulu.")
    else:
        audio_file = "temp_audio.m4a"
        
        # Hapus file sisa jika ada
        if os.path.exists(audio_file):
            try:
                os.remove(audio_file)
            except Exception:
                pass

        try:
            # 1. Unduh Audio via PyTubeFix (Bypass HTTP 403 Cloud Block)
            with st.spinner("📥 1/3 Mengunduh audio dari YouTube (via PyTubeFix)..."):
                yt = YouTube(url, client='MWEB')
                ys = yt.streams.get_audio_only()
                ys.download(filename=audio_file)

            if not os.path.exists(audio_file):
                st.error("❌ Gagal mengunduh audio. Pastikan link YouTube valid.")
            else:
                # 2. Analisis BPM Menggunakan Librosa
                with st.spinner("🎼 2/3 Menganalisis tempo (BPM) audio..."):
                    load_duration = None if duration_option == "Penuh (Full Track)" else float(duration_option)
                    y, sr = librosa.load(audio_file, duration=load_duration)
                    
                    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
                    bpm = float(tempo[0]) if hasattr(tempo, "__len__") else float(tempo)

                # 3. Visualisasi Grafik Waveform
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

                # Tampilkan Hasil ke UI Streamlit
                st.success("✅ Analisis Selesai!")
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric(label="🥁 Estimated BPM", value=f"{bpm:.1f} BPM")
                with col2:
                    st.audio(audio_file, format="audio/mp4")

                st.write("---")
                st.subheader("📈 Visualisasi Bentuk Gelombang (Waveform)")
                st.pyplot(fig)

        except Exception as e:
            st.error(f"❌ Terjadi kesalahan saat memproses: {str(e)}")
            
        finally:
            if os.path.exists(audio_file):
                try:
                    os.remove(audio_file)
                except Exception:
                    pass
