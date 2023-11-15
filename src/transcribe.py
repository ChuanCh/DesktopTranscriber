# -*- coding: UTF-8 -*-
""" This file is responsible for producing and translating a transcript of a video file """

from google.cloud import speech, translate_v2 as translate
from PyQt5.QtCore import QThread, pyqtSignal
import time

LANGUAGE_CODE = "ja-JP"  # Japanese

class TranscriptionThread(QThread):
    transcriptionDone = pyqtSignal(str)
    transcriptionStatus = pyqtSignal(str)

    def __init__(self, input_filename, parent=None):
        super().__init__(parent)
        self.input_filename = input_filename

    def run(self):
        try:
            transcription_text = self.transcribe(self.input_filename)
            self.transcriptionStatus.emit("Transcription done!")
            translated_text = self.translate_to_english(transcription_text)
            self.transcriptionDone.emit(translated_text)
        except Exception as e:
            self.transcriptionDone.emit(f"Error: {str(e)}")

    def transcribe(self, file_path):
        client = speech.SpeechClient()
        with open(file_path, 'rb') as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)
        print("Starting transcription")
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=LANGUAGE_CODE,
        )

        operation = client.long_running_recognize(config=config, audio=audio)
        print("Waiting for transcription to finish")
        while not operation.done():
            self.transcriptionStatus.emit("Transcription in progress...")
            time.sleep(5)

        response = operation.result()
        print("Transcription done!")
        return ' '.join([result.alternatives[0].transcript for result in response.results])

    def translate_to_english(self, text):
        translate_client = translate.Client()
        print("Translating to English")
        result = translate_client.translate(text, target_language='en')
        print("Translation done!")
        return result['translatedText']
