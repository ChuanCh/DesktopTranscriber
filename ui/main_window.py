import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit, QFileDialog, QCheckBox, QDesktopWidget, QGraphicsView
import os

script_dir = os.path.dirname(__file__)  # Path to the directory where this script is located
parent_dir = os.path.dirname(script_dir)  # Path to the parent directory
sys.path.append(parent_dir)

from src.extract_audio import rip_to_memory


class SimpleApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Row 1
        self.openButton = QPushButton('Open', self)
        self.runButton = QPushButton('Run', self)
        self.saveButton = QPushButton('Save Subtitle', self)
        self.openButton.clicked.connect(self.openFileDialog)
        self.runButton.clicked.connect(self.runSubtitle)
        self.saveButton.clicked.connect(self.saveSubtitle)
        

        row1Layout = QHBoxLayout()
        row1Layout.addWidget(self.openButton)
        row1Layout.addWidget(self.runButton)
        row1Layout.addWidget(self.saveButton)

        # Row 2
        self.videoLabel = QLabel('Video/Audio Display', self)
        self.audioWaveDisplay = QGraphicsView(self)
        row2Layout = QVBoxLayout()
        row2Layout.addWidget(self.videoLabel)
        row2Layout.addWidget(self.audioWaveDisplay)

        # Row 3
        self.subtitleTextEdit = QTextEdit(self)
        self.settingCheckbox = QCheckBox('Setting 1', self)

        row3Layout = QVBoxLayout()
        row3Layout.addWidget(self.subtitleTextEdit)
        row3Layout.addWidget(self.settingCheckbox)

        # Main Layout
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(row1Layout)
        mainLayout.addLayout(row2Layout)
        mainLayout.addLayout(row3Layout)

        self.setLayout(mainLayout)
        self.setWindowTitle('Subtitle Generator App')
        self.setGeometry(900, 900, 1500, 900)
        self.center()

    def display_waveform(self, audio_data):
        # Assuming audio_data is a NumPy array of audio samples
        waveform_plot = pg.PlotWidget()
        waveform_plot.plot(audio_data)
        # Add waveform_plot to your layout

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def openFileDialog(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Open Video Files", "", "Video Files (*.mp4 *.avi *.mkv)")
        if files:
            for file in files:
                audio_path = rip_to_memory(file)

    def saveSubtitle(self):
        # Logic to save subtitle
        pass

    def runSubtitle(self):
        # Logic to run subtitle
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SimpleApp()
    ex.show()
    sys.exit(app.exec_())
