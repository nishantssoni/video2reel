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

transcript = get_transcript(vid_id)
print(transcript)
# save the transcript to a txt file
with open("transcript.txt", "w") as f:
    f.write(str(transcript))

prompt = f"""Provided to you is a transcript of a video. 
Please identify all segments that can be extracted as 
subtopics from the video based on the transcript.
Make sure each segment is between 30-500 seconds in duration.
Make sure you provide extremely accruate timestamps
and respond only in the format provided. 
\n Here is the transcription : \n {transcript}"""

messages = [
    {"role": "system", "content": "You are a viral content producer. You are master at reading youtube transcripts and identifying the most intriguing content. You have extraordinary skills to extract subtopic from content. Your subtopics can be repurposed as a separate video."},
    {"role": "user", "content": prompt}
]

# # 9. Use ChatOllama model from langchain_ollama
# llm = ChatOllama(model="deepseek-r1:latest")
# result = llm.invoke(messages)
# print(result.content)