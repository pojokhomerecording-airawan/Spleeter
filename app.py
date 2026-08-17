import streamlit as st
import crepe
import soundfile as sf
import librosa
import numpy as np
import pandas as pd
import tempfile

st.title("Pendeteksi Nada Vokal & Not Musik")

uploaded_file = st.file_uploader("Unggah stem vokal (.wav atau .mp3)", type=["wav", "mp3"])

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/wav")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(uploaded_file.read())
        audio_path = tmp_file.name

    if st.button("Analisis Nada Vokal"):
        with st.spinner("Menganalisis frekuensi dan notasi musik..."):
            audio, sr = sf.read(audio_path)
            
            # Deteksi frekuensi menggunakan CREPE
            time, frequency, confidence, _ = crepe.predict(
                audio, sr, viterbi=True, step_size=20, model_capacity='tiny'
            )

            # Filter data berdasarkan batas confidence (> 0.5)
            valid_mask = (confidence > 0.5) & (frequency > 50)  # Abaikan frekuensi di bawah 50 Hz
            
            times_valid = time[valid_mask]
            freqs_valid = frequency[valid_mask]

            # 1. Konversi Frekuensi (Hz) ke Not Musik (misal: C4, F#3)
            notes_valid = librosa.hz_to_note(freqs_valid)

            # 2. Buat DataFrame ringkasan hasil
            df_results = pd.DataFrame({
                "Waktu (detik)": np.round(times_valid, 2),
                "Frekuensi (Hz)": np.round(freqs_valid, 1),
                "Not Musik": notes_valid
            })

            # Tampilkan statistik & ringkasan di Streamlit
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Sampel Nada", len(df_results))
            with col2:
                # Menemukan not yang paling sering dinyanyikan (Dominan)
                top_note = df_results["Not Musik"].mode()[0] if not df_results.empty else "-"
                st.metric("Not Paling Dominan", top_note)

            # Tampilkan Tabel Data
            st.subheader("Data Detail Nada Per Detik")
            st.dataframe(df_results, use_container_width=True)

            # Tampilkan Grafik Distribusi Not
            st.subheader("Distribusi Not yang Dinyanyikan")
            note_counts = df_results["Not Musik"].value_counts()
            st.bar_chart(note_counts)
