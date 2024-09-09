import os
import subprocess
import logging
from openai import OpenAI
import yt_dlp
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# OpenAI client
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def download_video_audio(url: str) -> str:
    # yt-dlp options to download audio and convert to mp3
    ydl_opts = {
        'format': 'bestaudio/best',  # Get the best audio quality available
        'quiet': False,              # Show the download progress
        'extract_audio': True,       # Extract audio only
        'audio_format': 'mp3',       # Convert to mp3
        'outtmpl': './%(title)s.%(ext)s',  # Use video title as the filename
    }

    # Download the audio using yt-dlp
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)  # Download the video and extract info
        video_title = info_dict.get('title', None)  # Get the video title
        file_path = f"./{video_title}.mp3"  # Construct the path to the downloaded file

        # Ensure title is valid for a filename by replacing problematic characters
        if video_title:
            valid_title = ''.join(c if c.isalnum() or c in (' ', '.', '_', '-') else '_' for c in video_title)
            file_path = f"./{valid_title}.mp3"
        else:
            raise Exception("Failed to extract video title")

    return file_path


def transcribe_mp3_file(filename: str) -> str:
    with open(filename, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
        )
    return transcription.text


def ask_gpt_for_summary(transcript: str, url: str) -> str:
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. You are helping me summarize and write actionable insights from transcriptions of youtube videos."},
            {"role": "user", "content": f"Hello! Can you help me summarize and write a detailed, yet concise document from this transcript? \n {transcript}, also at the bottom of the summary can you put this url: {url} underneath a h2 md heading like this ![](<insert-url-here>) "}
        ]
    )
    return completion.choices[0].message.content


async def process_youtube_summary(url: str, detail: str):

    # TODO:  add 'detail' as a summary argument
    try:
        print(detail)
        logging.info(f"Downloading audio for {url}")
        audio_file_path = download_video_audio(url)

        logging.info(f"Transcribing audio for {audio_file_path}")
        transcription = transcribe_mp3_file(audio_file_path)
        # TODO: save transcript to "database"

        logging.info(f"Generating summary for {audio_file_path}")
        summary = ask_gpt_for_summary(transcription, url)

        # Clean up the audio file
        os.remove(audio_file_path)

        return {
                "status": "success",
                "summary": summary
        }
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return {"status": "failed", "error": str(e)}
