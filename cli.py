import os
import sys
import time
import threading
import signal
import subprocess

import ffmpeg
import openai
import tiktoken
import torch
import whisper
from dotenv import load_dotenv

whisper_model = "base"
command_prompt = "Create clear and concise unlabelled bullet points summarizing key information"

stop_ticker = False


def display_ticker():
    start_time = time.time()
    while not stop_ticker:
        elapsed_time = time.time() - start_time
        minutes, seconds = divmod(int(elapsed_time), 60)
        sys.stdout.write(f'\rRecording: {minutes:02d}:{seconds:02d}')
        sys.stdout.flush()
        time.sleep(1)


def record_meeting(output_filename):
    try:

        global stop_ticker

        # Start the moving ticker
        stop_ticker = False
        ticker_thread = threading.Thread(target=display_ticker)
        ticker_thread.start()

        # The command to record audio using FFmpeg on macOS
        stream = (
            ffmpeg
            .input(":0", f="avfoundation", video_size=None)  # Use 'default'
            .output(output_filename, acodec="libmp3lame", format="mp3")  # Specify the output format as 'mp3'
            .overwrite_output()
        )

        # Start the FFmpeg process
        process = ffmpeg.run_async(stream, pipe_stdin=True, pipe_stderr=True)

        # Wait for the process to finish or be interrupted
        while process.poll() is None:
            time.sleep(1)

    except KeyboardInterrupt:

        stop_ticker = True
        ticker_thread.join()

        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            process.wait()

        print("Recording stopped.")
    except Exception as e:
        print(e)


def transcribe_audio(filename):

    # load model
    devices = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = whisper.load_model(whisper_model, device=devices)

    # load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio(filename)

    print("Beginning Transcribing Process...")

    result = model.transcribe(audio, verbose=False, fp16=False, task="translate")

    return result['text']


def summarize_transcript(transcript):

    def generate_summary(prompt):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text to small paragraphs"},
                {"role": "user", "content": f"{command_prompt}: {prompt}"}
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
        chunk_tokens = tokens[:2000]
        chunk_text = tokenizer.decode(chunk_tokens)
        chunks.append(chunk_text)
        tokens = tokens[2000:]

    summary = "\n".join([generate_summary(chunk) for chunk in chunks])

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
        print(f"TRANSCRIPT:{transcript}\n")
        print(f"SUMMARY_START:\n{summary}\nSUMMARY_END\n")
    else:
        print(f"Invalid action. Usage: python {sys.argv[0]} [record|summarize] output.mp3")
        sys.exit(1)
