import os
from pytube import YouTube
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from pydantic import BaseModel, Field
# from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_ollama import ChatOllama
import json
import subprocess
from typing import List

load_dotenv()

# youtube URL
vid_id = os.getenv("YOUTUBE_VIDEO_ID")

# create a directory to store the transcript
os.makedirs("downloaded_videos", exist_ok=True)


try:
    # download the video
    yt = YouTube("https://www.youtube.com/watch?v=" + vid_id)

    video = yt.streams.filter(file_extension="mp4").first()

    title = yt.title.replace(" ", "_")
    filename = f"downloaded_videos/{title}.mp4"
    video.download(filename=filename)
except Exception as e:
    print(f"An error occurred: {e}")


def get_transcript(video_id):
    try:
        transcript_yt = YouTubeTranscriptApi()
        transcript_list = YouTubeTranscriptApi.list(transcript_yt, video_id)
        # print(transcript_list)
        return transcript_list.find_transcript(["en"]).fetch()
    except Exception as e:
        print(f"An error occurred: {e}")

trascript = get_transcript(vid_id)
print(trascript)

