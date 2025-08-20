import os
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from typing import List
import json

import transcript
import clipper
import utils
import track_n_merge
import video_downloader


load_dotenv(find_dotenv())


llm = ChatOpenAI(model='openai/gpt-4o-mini',
                 temperature=0.7, 
                 max_tokens=None,
                 timeout=None,
                 max_retries=2
                 )


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

    # # create generated structure
    utils.create_generated_structure()
    
    # vid_id = 'XeN6eGO6FVQ'
    vid_id = input("Enter Video ID : ")

    isVideoDownloaded = video_downloader.download_youtube_video(vid_id,
                                                      output_path="generated/downloaded_videos",
                                                      output_filename="videoplayback.mp4")

    if not isVideoDownloaded:
        print("Video Download Failed")
        exit()
    
    # # main video
    filename = "generated/downloaded_videos/videoplayback.mp4"

    # # download transcript
    # # transcript
    
    print("Downloading transcript...")
    manager = transcript.TranscriptManager(vid_id)
    manager.get_transcript()


    print("Generating segments...")
    # prompts and message
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
    
    print("invoke LLM...")
    structured_llm = llm.with_structured_output(VideoTranscript)
    ai_msg = structured_llm.invoke(messages)

    parsed_content = ai_msg.dict()['segments']
    utils.save_segment_to_json(parsed_content)

    # with open("generated/transcripts/segments.json", 'r') as f:
    #     parsed_content = json.load(f)
    
    
    clipper.generate_video_clips(filename, parsed_content)
    # manager.save_transcript()
    manager.load_segments("generated/transcripts/segments.json")
    manager.merge_segments_with_subtitles()
    manager.export_all_srts()

    names = utils.return_files_in_directory("generated/video")

    cropper = track_n_merge.FaceTrackingCropper(smoothing_factor=0.8)
        
    for name in names:
        success = cropper.process_video(f"generated/video/{name}.mp4",
                                        f"generated/merged/{name}.mp4",
                                        f"generated/subtitles/{name}.srt")

