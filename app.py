import gc  # 1. TAMBAHAN: Import Garbage Collector untuk bersihkan RAM
import os
import streamlit as st
from pydub import AudioSegment
from spleeter.separator import Separator

st.set_page_config(page_title="Spleeter 4-Stem Separator", layout="centered")
st.title("🎵 Audio 4-Stem Separator")

# Upload file audio
uploaded_file = st.file_uploader(
    "Upload file audio (.mp3 / .wav)", type=["mp3", "wav"]
)

# Batas maksimal 5 menit (300 detik)
MAX_DURATION_SECONDS = 300

if uploaded_file is not None:
    # 1. Simpan file unggahan sementara
    temp_input_path = f"temp_{uploaded_file.name}"
    with open(temp_input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # 2. Cek durasi audio dengan pydub
    audio = AudioSegment.from_file(temp_input_path)
    duration_seconds = len(audio) / 1000.0  # pydub menghitung dalam milidetik

    minutes = int(duration_seconds // 60)
    seconds = int(duration_seconds % 60)

    # 2. TAMBAHAN: Hapus objek 'audio' dari RAM SEGERA setelah durasi dihitung
    del audio
    gc.collect()

    # 3. Validasi durasi
    if duration_seconds > MAX_DURATION_SECONDS:
        st.error(
            f"❌ **Durasi Terlalu Panjang!**\n\n"
            f"Durasi lagu kamu adalah **{minutes}m {seconds}s**. "
            f"Batas maksimal yang diizinkan adalah **5 menit (300 detik)** untuk mencegah server kehabisan RAM."
        )
        # Hapus file temp jika lagu terlalu panjang
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)
    else:
        st.success(
            f"⏱️ Durasi lagu: **{minutes}m {seconds}s** (Sesuai batas kuota)"
        )

        if st.button("Proses Pemisahan Stem"):
            with st.spinner(
                "Memproses audio... Membutuhkan waktu sekitar 30-60 detik."
            ):
                output_dir = "output"

                # Inisialisasi Spleeter 4 stems
                separator = Separator("spleeter:4stems")
                separator.separate_to_file(temp_input_path, output_dir)

                # Path direktori output
                folder_name = f"temp_{os.path.splitext(uploaded_file.name)[0]}"
                stem_dir = os.path.join(output_dir, folder_name)

                st.balloons()
                st.subheader("Hasil Pemisahan Track:")

                # Render player audio untuk 4 stem
                stems = ["vocals", "drums", "bass", "other"]
                for stem in stems:
                    audio_path = os.path.join(stem_dir, f"{stem}.wav")
                    if os.path.exists(audio_path):
                        st.write(f"**{stem.capitalize()}**")
                        st.audio(audio_path, format="audio/wav")

            # 3. PERBAIKAN: Pindahkan penghapusan file temp ke dalam blok tombol ini
            if os.path.exists(temp_input_path):
                os.remove(temp_input_path)
