import sys, os, signal
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QLabel, QTextEdit, QHBoxLayout
from PyQt5.QtCore import QProcess


class MeetingSummarizer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Meeting Summarizer")
        self.setFixedSize(700, 450)  # Set fixed window size to 800x450 pixels

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.button_layout = QHBoxLayout()
        layout.addLayout(self.button_layout)

        self.start_button = QPushButton("Start Recording")
        self.start_button.clicked.connect(self.start_recording)
        self.button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Recording")
        self.stop_button.clicked.connect(self.stop_recording)
        self.button_layout.addWidget(self.stop_button)

        self.summarize_button = QPushButton("Summarize")
        self.summarize_button.clicked.connect(self.summarize_recording)
        layout.addWidget(self.summarize_button)

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
        if not output_filename.endswith(".mp3"):
            output_filename += ".mp3"
        self.output_filename = output_filename
        self.process.start("python", ["cli.py", "record", self.output_filename])

    def stop_recording(self):
        os.kill(self.process.processId(), signal.SIGINT)
        self.process.waitForFinished(-1)  # Wait indefinitely for the process to finish

    def summarize_recording(self):
        audio_filename, _ = QFileDialog.getOpenFileName(self, "Select Audio File", filter="MP3 Files (*.mp3)")
        if not audio_filename:
            return
        self.process.start("python", ["cli.py", "summarize", audio_filename])

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        lines = data.strip().splitlines()

        summary_flag = False
        summary_lines = []

        for line in lines:
            print(line)  # Print stdout to console

            if line.startswith("TRANSCRIPT:"):
                transcript = line[len("TRANSCRIPT:"):].strip()
                current_transcript = self.transcript_edit.toPlainText()
                self.transcript_edit.setPlainText(current_transcript + transcript)
            elif line.startswith("SUMMARY_START"):
                summary_flag = True
            elif line.startswith("SUMMARY_END"):
                summary_flag = False
                summary = "\n".join(summary_lines)
                current_summary = self.summary_edit.toPlainText()
                self.summary_edit.setPlainText(current_summary + summary)
                summary_lines = []  # Clear summary_lines for next summary
            elif summary_flag:
                summary_lines.append(line)

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode()
        print(f"StdErr: {data.strip()}")  # Print stderr to console

    def process_finished(self):
        print("Process finished")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MeetingSummarizer()
    window.show()
    sys.exit(app.exec_())
