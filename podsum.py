import yt_dlp
import os
from openai import OpenAI

client = OpenAI(
  api_key=os.environ['OPENAI_API_KEY'], 
)

def download_podcast(url):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "%(title)s.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "prefer_ffmpeg": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        audio_file = ydl.prepare_filename(info).replace(info["ext"], "mp3")
    return audio_file

def transcribe_audio(audio_file):
    with open(audio_file, "rb") as audio:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio,
            response_format="text"
        )
    return transcript

def summarize_transcription(transcription):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that creates concise bullet-point summaries of transcripts."
            },
            {
                "role": "user",
                "content": f"Please create a detailed bullet-point summary of the following transcript:\n{transcription}"
            }
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

def main():
    podcast_url = input("Please enter the podcast URL: ")
    audio_file = download_podcast(podcast_url)
    print(f"Downloaded audio file: {audio_file}")
    
    title = os.path.splitext(os.path.basename(audio_file))[0]  # Get the title without extension

    transcription = transcribe_audio(audio_file)
    print("Transcription completed.")

    summary = summarize_transcription(transcription)
    print("Summary generated.")

    output_file = f"summary_{title}.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Full Transcript\n")
        f.write(transcription)
        f.write("\n# Summary\n")
        f.write(summary)

    print(f"Transcription and summary saved to: {output_file}")

if __name__ == "__main__":
    main()