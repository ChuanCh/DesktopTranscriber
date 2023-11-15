# def main():
#     app = QApplication(sys.argv)
#     mainWindow = SimpleApp()
#     mainWindow.show()
#     sys.exit(app.exec_())

# if __name__ == '__main__':
#     main()


import os
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
import subprocess
from pydub import AudioSegment
from google.cloud import translate_v2 as translate
from faster_whisper import WhisperModel
import tkinter as tk
from tkinter import filedialog

MODEL_SIZE = "large-v2"
DEVICE = "cuda"
COMPUTE_TYPE = "float16"
LANGUAGE = "ja"
TARGET_LANGUAGE = "zh"

# test cuda
import torch
print(torch.cuda.is_available())

def extract_audio(video_file):
    audio_file = "temp_audio.wav"
    video_file_str = str(video_file)    
    subprocess.run(["ffmpeg", "-i", video_file_str, "-f", "wav", "-ar", "16000", "-ac", "1", audio_file], check=True)
    return audio_file

def split_audio(audio_file_path):
    segment_length = 60000  # 60 seconds
    try:
        audio = AudioSegment.from_wav(audio_file_path)
        segments = [audio[i:i + segment_length] for i in range(0, len(audio), segment_length)]
        return segments
    except Exception as e:
        print(f"Error processing audio file: {e}")
        return []

def transcribe_audio(audio_segment, language_code="ja-JP"):
    whisper = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
    segments, info = whisper.transcribe(audio_segment, language=LANGUAGE, vad_filter=True)
    subtitles = []
    for segment in segments:
        # format it into SRT format
        text = translate_text(segment.text)
        subtitle = [(segment.start, segment.end, text)]
        subtitles.extend(subtitle)
    srts = generate_srt(subtitles)
    return srts


def translate_text(text):
    translate_client = translate.Client()
    result = translate_client.translate(text, target_language=TARGET_LANGUAGE)
    return result['translatedText']

def format_time(seconds):
    """Convert time in seconds to the SRT time format."""
    millisec = int((seconds - int(seconds)) * 1000)
    hours, seconds = divmod(int(seconds), 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{millisec:03}"

def generate_srt(subtitles):
    """Generate an SRT formatted string from a list of subtitles."""
    srt_format = []
    for index, (start, end, text) in enumerate(subtitles, start=1):
        start_time = format_time(start)
        end_time = format_time(end)
        srt_format.append(f"{index}\n{start_time} --> {end_time}\n{text}\n")
    
    return "\n".join(srt_format)

def save_subtitle(text, video_file):
    subtitle_file = os.path.splitext(video_file)[0] + ".srt"
    with open(subtitle_file, "w") as file:
        # write the srt by line
        for line in text:
            file.write(line)
    return subtitle_file

def main():
    try:
        # Set up a root window for the file dialog (hidden from view)
        root = tk.Tk()
        root.withdraw()

        # Open a file dialog and get the video file path
        video_file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv"), ("All Files", "*.*")]
        )

        if not video_file_path:
            print("No file selected.")
            return

        print("Extracting audio from video...")
        audio_file = extract_audio(video_file_path)

        print("Transcribing audio segments...")
        transcriptions = transcribe_audio(audio_file)

        print("Saving subtitle...")
        subtitle_file = save_subtitle(transcriptions, video_file_path)
        print(f"Subtitle saved to {subtitle_file}")

        # Clean up temporary audio file
        os.remove(audio_file)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
