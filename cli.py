import os
import platform
import subprocess
import sys
import time

import openai
import tiktoken
import torch
import whisper
from dotenv import load_dotenv
import tqdm

whisper_model = "base"


class _CustomProgressBar(tqdm.tqdm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current = self.n

    def update(self, n):
        super().update(n)
        self._current += n

        print("Audio Transcribe Progress: " + str(round(self._current / self.total * 100)) + "%")


transcribe_module = sys.modules['whisper.transcribe']
transcribe_module.tqdm.tqdm = _CustomProgressBar


def record_meeting(filename):
    input_format = "dshow" if platform.system() == "Windows" else "avfoundation"
    input_device = "audio=Microphone" if platform.system() == "Windows" else ":0"

    command = ["ffmpeg", "-f", input_format, "-i", input_device, "-vn", "-acodec", "libmp3lame", filename]
    try:
        process = subprocess.Popen(command)
        process.communicate()
    except KeyboardInterrupt:
        process.terminate()
        print("\nRecording stopped by user.")
        sys.exit(0)


def transcribe_audio(filename):

    # load model
    devices = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = whisper.load_model(whisper_model, device=devices)

    # load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio(filename)

    print("Beginning Transcribing Process...")

    result = model.transcribe(audio, verbose=False, fp16=False)

    return result['text']


def summarize_transcript(transcript):

    def generate_summary(prompt):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text."},
                {"role": "user", "content": f"Please summarize the following text: {prompt}"}
            ],
            temperature=0.5,
        )
        return response.choices[0].message['content'].strip()

    chunks = []
    prompt = "Please summarize the following text:\n\n"
    text = prompt + transcript
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    while tokens:
        chunk_tokens = tokens[:1000]
        chunk_text = tokenizer.decode(chunk_tokens)
        chunks.append(chunk_text)
        tokens = tokens[1000:]

    summary = "\n\n".join([generate_summary(chunk) for chunk in chunks])
    return summary


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} [record|summarize] output.mp3")
        sys.exit(1)

    load_dotenv()
    api_key = os.getenv('OPEN_API_KEY')
    if api_key is None:
        print("Environment variable OPEN_API_KEY not found. Exiting...")
        sys.exit(1)

    openai.api_key = api_key

    action = sys.argv[1]
    output_filename = sys.argv[2]

    if action == "record":
        record_meeting(output_filename)
    elif action == "summarize":
        transcript = transcribe_audio(output_filename)
        summary = summarize_transcript(transcript)
        print("TRANSCRIPT:\n" + transcript)
        print("SUMMARY:\n" + summary)
    else:
        print(f"Invalid action. Usage: python {sys.argv[0]} [record|summarize] output.mp3")
        sys.exit(1)
