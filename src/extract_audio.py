import sys
import subprocess
import argparse
from pydub import AudioSegment
import io
import numpy as np

def rip_to_memory(input_filename: str) -> AudioSegment:
    # Extract audio using ffmpeg and store in memory
    args = ["ffmpeg", "-i", input_filename, "-f", "wav", "-"]
    result = subprocess.run(args, stdout=subprocess.PIPE)
    result.check_returncode()

    # Use io.BytesIO to create a file-like object from the result
    audio_in_memory = io.BytesIO(result.stdout)

    # Load this audio into pydub
    audio_segment = AudioSegment.from_file(audio_in_memory, format="wav")
    return process_audio(audio_segment)

def process_audio(audio_segment: AudioSegment) -> AudioSegment:
    # Convert to mono and set frame rate
    return audio_segment.set_frame_rate(16000).set_channels(1)

def audio_segment_to_numpy(audio_segment):
    # Directly access the frame rate and number of channels from the audio_segment
    sample_rate = audio_segment.frame_rate
    channels = audio_segment.channels

    # Convert audio_segment to numpy array
    samples = np.array(audio_segment.get_array_of_samples())

    # If stereo, reshape the array
    if channels == 2:
        samples = samples.reshape((-1, 2))

    return samples, sample_rate

def main() -> int:
    parser = argparse.ArgumentParser(description="Rips audio from an mp4 file into a single 16khz mono wav file")
    parser.add_argument("video_file")
    args = parser.parse_args()

    audio_segment = rip_to_memory(args.video_file)

    return 0

if __name__ == "__main__":
    sys.exit(main())