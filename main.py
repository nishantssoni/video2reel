import os
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from typing import List
import json

import transcript
import clipper


load_dotenv(find_dotenv())

# youtube URL
vid_id = os.getenv("YOUTUBE_VIDEO_ID")

# transcript
manager = transcript.TranscriptManager(vid_id)

# create a directory to store the transcript
os.makedirs("downloaded_videos", exist_ok=True)
filename = f"downloaded_videos/video.mp4"

llm = ChatOpenAI(model='openai/gpt-4o-mini',
                 temperature=0.7, 
                 max_tokens=None,
                 timeout=None,
                 max_retries=2
                 )

prompt = f"""Provided to you is a transcript of a video. 
Please identify all segments that can be extracted as 
subtopics from the video based on the transcript.
Make sure each segment is between 60-300 seconds in duration.
Make sure you provide extremely accruate timestamps
and respond only in the format provided. 
\n Here is the transcription : \n {manager.load_transcript()}"""

messages = [
    {"role": "system", "content": "You are a viral content producer. You are master at reading youtube transcripts and identifying the most intriguing content. You have extraordinary skills to extract subtopic from content. Your subtopics can be repurposed as a separate video."},
    {"role": "user", "content": prompt}
]

class Segment(BaseModel):
    """ Represents a segment of a video"""
    start_time: float = Field(..., description="The start time of the segment in seconds")
    end_time: float = Field(..., description="The end time of the segment in seconds")
    yt_title: str = Field(..., description="The youtube title to make this segment as a viral sub-topic")
    description: str = Field(..., description="The detailed youtube description to make this segment viral ")
    duration : int = Field(..., description="The duration of the segment in seconds")

class VideoTranscript(BaseModel):
    """ Represents the transcript of a video with identified viral segments"""
    segments: List[Segment] = Field(..., description="List of viral segments in the video")



if __name__ == "__main__":
    # structured_llm = llm.with_structured_output(VideoTranscript)
    # ai_msg = structured_llm.invoke(messages)

    # parsed_content = ai_msg.dict()['segments']

    # clipper.generate_video_clips(filename, parsed_content)

    with open("transcripts/segments.json", 'r') as f:
        parsed_content = json.load(f)
    
    clipper.generate_video_clips(filename, parsed_content)
    manager.get_transcript()
    manager.save_transcript()
    print(manager.load_transcript())
    manager.load_segments("transcripts/segments.json")
    manager.merge_segments_with_subtitles()
    manager.export_all_srts()

