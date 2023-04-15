import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QLabel, QTextEdit
from PyQt5.QtCore import QProcess


class MeetingSummarizer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Meeting Summarizer")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.start_button = QPushButton("Start Recording")
        self.start_button.clicked.connect(self.start_recording)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Recording and Summarize")
        self.stop_button.clicked.connect(self.stop_recording)
        layout.addWidget(self.stop_button)

        self.transcript_label = QLabel("Transcript:")
        layout.addWidget(self.transcript_label)

        self.transcript_edit = QTextEdit()
        layout.addWidget(self.transcript_edit)

        self.summary_label = QLabel("Summary:")
        layout.addWidget(self.summary_label)

        self.summary_edit = QTextEdit()
        layout.addWidget(self.summary_edit)

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)

    def start_recording(self):
        output_filename, _ = QFileDialog.getSaveFileName(self, "Save Meeting Recording", filter="MP3 Files (*.mp3)")
        if not output_filename:
            return
        self.output_filename = output_filename
        self.process.start("python", ["cli.py", "record", self.output_filename])

    def stop_recording(self):
        self.process.terminate()
        self.process.waitForFinished()
        self.process.start("python", ["cli.py", "summarize", self.output_filename])

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        if data.startswith("TRANSCRIPT:"):
            self.transcript_edit.setPlainText(data[len("TRANSCRIPT:"):].strip())
        elif data.startswith("SUMMARY:"):
            self.summary_edit.setPlainText(data[len("SUMMARY:"):].strip())

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode()
        print(f"Error: {data.strip()}")

    def process_finished(self):
        print("Process finished")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MeetingSummarizer()
    window.show()
    sys.exit(app.exec_())
