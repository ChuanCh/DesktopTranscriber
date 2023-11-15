import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit, QFileDialog, QCheckBox, QDesktopWidget, QGraphicsView, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
import os
import numpy as np
import pyqtgraph as pg
import threading
from src.extract_audio import rip_to_memory, audio_segment_to_numpy
from src.transcribe import TranscriptionThread

class SimpleApp(QWidget):

    waveformReady = pyqtSignal(np.ndarray, float)
    transcriptionDone = pyqtSignal(str)


    def __init__(self):
        super().__init__()
        self.initUI()
        self.selectedFile = None
        self.waveformReady.connect(self.display_waveform)
        self.transcriptionDone.connect(self.onTranscriptionDone)

    def initUI(self):
        # Initialize rows and layouts
        self.setupRowsAndLayouts()

        # Set window properties
        self.setWindowTitle('Subtitle Generator App')
        self.setGeometry(900, 900, 1500, 900)
        self.center()

    def setupRowsAndLayouts(self):
        # Row 1: Buttons for file operations
        self.setupRow1()

        # Row 2: Area for audio waveform display
        self.setupRow2()

        # Row 3: Text edit for subtitles and settings
        self.setupRow3()

        # Main Layout
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(self.row1Layout)
        mainLayout.addLayout(self.row2Layout)
        mainLayout.addLayout(self.row3Layout)
        self.setLayout(mainLayout)

    def setupRow1(self):
        self.openButton = QPushButton('Open', self)
        self.runButton = QPushButton('Run', self)
        self.saveButton = QPushButton('Save Subtitle', self)

        self.openButton.clicked.connect(self.openFileDialog)
        self.runButton.clicked.connect(self.runSubtitle)
        self.saveButton.clicked.connect(self.saveSubtitle)

        self.row1Layout = QHBoxLayout()
        self.row1Layout.addWidget(self.openButton)
        self.row1Layout.addWidget(self.runButton)
        self.row1Layout.addWidget(self.saveButton)

    def setupRow2(self):
        self.videoLabel = QLabel('Video/Audio Display', self)
        self.audioWaveDisplay = QGraphicsView(self)

        self.row2Layout = QVBoxLayout()
        self.row2Layout.addWidget(self.videoLabel)
        self.row2Layout.addWidget(self.audioWaveDisplay)

    def setupRow3(self):
        self.subtitleTextEdit = QTextEdit(self)
        self.settingCheckbox = QCheckBox('Setting 1', self)

        self.row3Layout = QVBoxLayout()
        self.row3Layout.addWidget(self.subtitleTextEdit)
        self.row3Layout.addWidget(self.settingCheckbox)

    def display_waveform(self, audio_data, sample_rate):
        # Convert audio data to waveform for display
        time_array = np.arange(len(audio_data)) / sample_rate
        waveform_plot = pg.PlotWidget()
        waveform_plot.plot(time_array, audio_data)
        waveform_plot.getAxis('bottom').setLabel('Time', units='s')

        waveform_plot.setMinimumSize(1400, 200)

        # Check if the second widget in row2Layout is the waveform plot and replace it
        if self.row2Layout.count() > 1:
            # Remove the old waveform plot
            old_waveform_widget = self.row2Layout.itemAt(1).widget()
            if old_waveform_widget is not None:
                self.row2Layout.removeWidget(old_waveform_widget)
                old_waveform_widget.deleteLater()

        # Add the new waveform plot as the second widget in row2Layout
        self.row2Layout.addWidget(waveform_plot)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def openFileDialog(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Open Video Files", "", "Video Files (*.mp4 *.avi *.mkv)")
        if files:
            self.selectedFile = files[0]
            self.fileProcessorThread = FileProcessor(files)  # Keep a reference to the thread
            self.fileProcessorThread.update_waveform_signal.connect(self.display_waveform)  # Connect signal
            self.fileProcessorThread.start()

    def processFiles(self, files):
        for file in files:
            print(f"Processing {file}")
            audio_segment = rip_to_memory(file)
            print(f"Finished processing {file}")
            samples, sample_rate = audio_segment_to_numpy(audio_segment)
            print(f"Finished converting {file} to numpy array")
            # Emit the signal instead of directly calling display_waveform
            self.waveformReady.emit(samples, sample_rate)

    def saveSubtitle(self):
        # Logic to save subtitle
        pass

    def runSubtitle(self):
        # Check if a file is selected
        if not self.selectedFile:
            QMessageBox.warning(self, "Warning", "No file selected!")
            return

         # Create and start the transcription thread
        self.transcriptionThread = TranscriptionThread(self.selectedFile)
        print("Starting transcription thread")
        self.transcriptionThread.transcriptionDone.connect(self.onTranscriptionDone)
        print("Connected transcriptionDone signal")
        self.transcriptionThread.start()

    def onTranscriptionDone(self, result):
        print("Transcription Done signal received")
        if result.startswith("Error"):
            QMessageBox.critical(self, "Transcription Error", result)
        else:
            self.subtitleTextEdit.setPlainText(result)

class FileProcessor(QThread):
    update_waveform_signal = pyqtSignal(np.ndarray, float)

    def __init__(self, files, parent=None):
        super(FileProcessor, self).__init__(parent)
        self.files = files

    def run(self):
        for file in self.files:
            audio_segment = rip_to_memory(file)
            samples, sample_rate = audio_segment_to_numpy(audio_segment)
            self.update_waveform_signal.emit(samples, sample_rate)  # Emit signal with data

