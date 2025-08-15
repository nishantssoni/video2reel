
prompt = f"""Provided to you is a transcript of a video. 
Please identify all segments that can be extracted as 
subtopics from the video based on the transcript.
Make sure each segment is between 30-500 seconds in duration.
Make sure you provide extremely accruate timestamps
and respond only in the format provided. 
\n Here is the transcription : \n  {transcript}"""

messages = [
    {"role": "system", "content": "You are a viral content producer. You are master at reading youtube transcripts and identifying the most intriguing content. You have extraordinary skills to extract subtopic from content. Your subtopics can be repurposed as a separate video."},
    {"role": "user", "content": prompt}
]


