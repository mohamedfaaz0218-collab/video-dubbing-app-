import os
import tempfile
from pathlib import Path
import streamlit as st

from dubbing_pipeline import process_video_for_dubbing

st.set_page_config(
    page_title="Video Auto-Dubbing Studio",
    page_icon="🎙️",
    layout="wide",
)

SUPPORTED_LANGUAGES = [
    "English",
    "Spanish",
    "French",
    "German",
    "Hindi",
    "Japanese",
    "Portuguese",
]

TARGET_LANGUAGE_MAP = {
    "English": "English",
    "Spanish": "Spanish",
    "French": "French",
    "German": "German",
    "Hindi": "Hindi",
    "Japanese": "Japanese",
    "Portuguese": "Portuguese",
}

def save_uploaded_video(uploaded_file) -> str:
    temp_dir = tempfile.mkdtemp(prefix="video_dub_")
    file_name = uploaded_file.name
    safe_name = os.path.basename(file_name)
    file_path = os.path.join(temp_dir, safe_name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path


def run_pipeline_with_streamlit(video_path: str, target_language: str):
    work_dir = str(Path(video_path).parent)
    progress = st.progress(0)
    status = st.empty()

    def update_progress(value: float, message: str):
        progress.progress(min(max(value, 0.0), 1.0))
        status.info(message)

    output_path = process_video_for_dubbing(
        video_path=video_path,
        target_language=target_language,
        work_dir=work_dir,
        progress_callback=update_progress,
    )
    return output_path


def main():
    st.title("🎙️ Video Auto-Dubbing Studio")
    st.caption("Upload a video, choose a target language, and generate a dubbed version with music preserved.")

    uploaded_file = st.file_uploader(
        "Upload video",
        type=["mp4", "mov", "mkv"],
        help="Supported formats: MP4, MOV, MKV"
    )

    target_language = st.selectbox(
        "Target language",
        options=SUPPORTED_LANGUAGES,
        index=1,  # Spanish by default
    )

    if uploaded_file is not None:
        st.write(f"Selected file: {uploaded_file.name}")
        st.write(f"Target language: {target_language}")

    col1, col2 = st.columns([1, 1])
    with col1:
        process_button = st.button("Generate Dubbed Video", type="primary", use_container_width=True)

    if process_button:
        if uploaded_file is None:
            st.error("Please upload a video before processing.")
            return

        try:
            video_path = save_uploaded_video(uploaded_file)
            with st.spinner("Processing your video..."):
                output_video = run_pipeline_with_streamlit(video_path, target_language)

            st.success("Video dubbing complete!")

            if os.path.exists(output_video):
                st.video(output_video)

                with open(output_video, "rb") as f:
                    st.download_button(
                        label="Download dubbed video",
                        data=f.read(),
                        file_name=os.path.basename(output_video),
                        mime="video/mp4",
                        use_container_width=True,
                    )
            else:
                st.warning("The final video file was not generated successfully.")

        except Exception as exc:
            st.error(f"Dubbing failed: {exc}")
            st.exception(exc)

    st.markdown("---")

    with st.expander("How it works", expanded=False):
        st.markdown(
            """
            - Extracts the audio track from the uploaded video
            - Separates vocal and background stems using Demucs
            - Preserves the background audio without modification
            - Transcribes vocals and assigns approximate speaker IDs
            - Detects speaker gender via pitch analysis
            - Translates text to the selected language
            - Synthesizes translated text with Edge TTS using gender-matched voices
            - Aligns each clip to the original timing using FFmpeg `atempo`
            - Merges dialogue and background audio
            - Muxes the final mixed audio back into the original video
            - Placeholder lip-sync hook included for future Wav2Lip / Sync.so integration
            """
        )


if __name__ == "__main__":
    main()
