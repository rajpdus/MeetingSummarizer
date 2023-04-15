# MeetingSummarizer

Effortlessly record, transcribe, and summarize meetings with this user-friendly desktop utility powered by OpenAI's Whisper and GPT-3.5-turbo.
This has been tested to work well on Macbooks with Apple Silicon


## Prerequisites

- Python 3.10: Download and install the latest version of Python from the [official website](https://www.python.org/downloads/) or use your package manager.
- FFmpeg: Install FFmpeg using a package manager. For macOS, you can use [Homebrew](https://brew.sh/):
- PyQt5: Install PyQt5 using brew as above. Add the site-packages to your PYTHONPATH
## Whisper ASR

Whisper is an Automatic Speech Recognition (ASR) system developed by OpenAI. It converts spoken language into written text and is trained on a large amount of multilingual and multitask supervised data collected from the web.

## CLI Utility

The command-line interface (CLI) utility allows you to record meetings and transcribe and summarize the recordings using the following commands:

1. Record a meeting:

``` python
python cli.py record output.mp3
```


2. Transcribe and summarize a recorded meeting:

``` python
python cli.py summarize output.mp3
```

Replace `output.mp3` with your desired output file name.

## GUI Utility

The graphical user interface (GUI) utility provides a more intuitive way to use the MeetingSummarizer. To launch the GUI, run:

``` python
python gui.py
```

To record a meeting, click the "Start Recording" button and choose a file name for the output. To stop recording and generate a transcription and summary, click the "Stop Recording and Summarize" button.

## Requirements

Install the required Python packages using the following command:

``` python
pip install -r requirements.txt
```

## License

This project is licensed under the [Apache License](LICENSE).
