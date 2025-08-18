import os
import json
from dotenv import load_dotenv, find_dotenv
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi


def get_transcript(video_id):
    try:
        transcript_yt = YouTubeTranscriptApi()
        transcript_list = YouTubeTranscriptApi.list(transcript_yt, video_id)
        # print(transcript_list)
        return transcript_list.find_transcript(["en"]).fetch()
    except Exception as e:
        print(f"An error occurred: {e}")

def save_transcript_to_json(transcript_data, video_id, folder="transcripts"):
    """
    Save transcript data to JSON file
    
    Args:
        transcript_data: List of dicts with 'text', 'start', 'duration' keys
        video_id: YouTube video ID for filename
        folder: Folder to save transcripts (default: 'transcripts')
    
    Returns:
        str: Path to saved file
    """
    try:
        # Create folder if it doesn't exist
        os.makedirs(folder, exist_ok=True)
        
        # Create filename
        filename = os.path.join(folder, f"{video_id}_transcript.json")
        
        # Save to JSON
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f, ensure_ascii=False, indent=4)
        
        print(f"Transcript saved to: {filename}")
        return filename
        
    except Exception as e:
        print(f"Error saving transcript: {e}")
        return None


def load_transcript_from_json(video_id, folder="transcripts"):
    """
    Load transcript data from JSON file
    
    Args:
        video_id: YouTube video ID
        folder: Folder where transcripts are saved
    
    Returns:
        list: Transcript data or empty list if not found
    """
    try:
        filename = os.path.join(folder, f"{video_id}_transcript.json")
        
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                transcript_data = json.load(f)
            print(f"Transcript loaded from: {filename}")
            return transcript_data
        else:
            print(f"Transcript file not found: {filename}")
            return []
            
    except Exception as e:
        print(f"Error loading transcript: {e}")
        return []


def get_text_by_timestamp(transcript, timestamp):
    """
    Get text at specific timestamp
    
    Args:
        transcript: List of transcript entries
        timestamp: Time in seconds (float)
    
    Returns:
        str: Text at that timestamp or error message
    """
    for entry in transcript:
        start = entry["start"]
        end = start + entry["duration"]
        if start <= timestamp < end:
            return entry["text"]
    return f"No text found at {timestamp} seconds"


def get_text_in_range(transcript, start_time, end_time):
    """
    Get all text entries within a time range
    
    Args:
        transcript: List of transcript entries  
        start_time: Start time in seconds
        end_time: End time in seconds
    
    Returns:
        list: List of entries within the time range
    """
    result = []
    for entry in transcript:
        entry_start = entry["start"]
        entry_end = entry_start + entry["duration"]
        
        # Check if entry overlaps with requested range
        if entry_start < end_time and entry_end > start_time:
            result.append(entry)
    
    return result


def search_text_in_transcript(transcript, search_term, case_sensitive=False):
    """
    Search for text in transcript
    
    Args:
        transcript: List of transcript entries
        search_term: Text to search for
        case_sensitive: Whether search is case sensitive
    
    Returns:
        list: List of entries containing the search term
    """
    results = []
    search_term = search_term if case_sensitive else search_term.lower()
    
    for entry in transcript:
        text = entry["text"] if case_sensitive else entry["text"].lower()
        if search_term in text:
            results.append(entry)
    
    return results


def merge_segments_with_subtitles(segments, transcript):
    """
    Merge segment dicts with transcript subtitles belonging to each segment's time range.

    Args:
        segments (list): List of segment dicts, each with 'start_time' and 'end_time'.
        transcript (list): List of transcript entries with 'start', 'duration', 'text'.

    Returns:
        list: Segments updated with a 'subtitles' key (list of subtitle texts per segment).
    """
    merged_segments = []
    for seg in segments:
        subs = get_text_in_range(transcript, seg["start_time"], seg["end_time"])
        seg["subtitles"] = [entry["text"] for entry in subs]
        merged_segments.append(seg)
    return merged_segments


import json

def merge_segments_with_subtitles_files(segments_path, transcript_path, output_path):
    """
    Load segments and transcript files, merge subtitles with timestamps by segment time ranges,
    and save the merged segments to an output JSON file.

    Args:
        segments_path (str): Path to segments JSON file.
        transcript_path (str): Path to transcript JSON file.
        output_path (str): Path to save the merged segments JSON.

    Returns:
        None
    """
    def get_text_and_time_in_range(transcript, start_time, end_time):
        result = []
        for entry in transcript:
            entry_start = entry["start"]
            entry_end = entry_start + entry["duration"]
            if entry_start < end_time and entry_end > start_time:
                # Include start relative to segment start_time
                relative_start = entry_start - start_time
                result.append({"start": relative_start, "text": entry["text"]})
        return result

    # Load segments
    with open(segments_path, "r", encoding="utf-8") as f:
        segments = json.load(f)
    
    # Load transcript
    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = json.load(f)
    
    # Merge segments with subtitles including timestamps
    merged_segments = []
    for seg in segments:
        subs = get_text_and_time_in_range(transcript, seg["start_time"], seg["end_time"])
        seg["subtitles"] = subs
        merged_segments.append(seg)
    
    # Save merged results
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged_segments, f, ensure_ascii=False, indent=4)


def json_to_srt(segment, output_srt_path):
    """
    Convert segment's 'subtitles' into an SRT file using subtitle start times relative to 0,
    suitable for a clipped video starting at 0 seconds.
    """
    def seconds_to_srt_time(seconds):
        hours, remainder = divmod(int(seconds), 3600)
        minutes, remainder = divmod(remainder, 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

    srt_lines = []
    subtitles = segment["subtitles"]
    for idx, sub in enumerate(subtitles, 1):
        abs_start = max(sub["start"], 0)  # Clip any negative start times to 0
        if idx < len(subtitles):
            abs_end = max(subtitles[idx]["start"], 0)
        else:
            abs_end = segment["duration"]  # Use segment duration for last subtitle end

        srt_lines.append(
            f"{idx}\n"
            f"{seconds_to_srt_time(abs_start)} --> {seconds_to_srt_time(abs_end)}\n"
            f"{sub['text']}\n"
        )
    with open(output_srt_path, "w", encoding="utf-8") as f:
        f.write('\n'.join(srt_lines))

# # Example usage
# if __name__ == "__main__":
#     merge_segments_with_subtitles_files(
#     "video_title/segments.json",
#     "transcripts/XeN6eGO6FVQ_transcript.json",
#     "merged_segments.json"
# )

    # # Your transcript data
    # video_id = "XeN6eGO6FVQ"
    # transcript = get_transcript(video_id).to_raw_data()
    
    # # Save transcript
    # saved_file = save_transcript_to_json(transcript, video_id)
    
    # # Load transcript
    # loaded_transcript = load_transcript_from_json(video_id)
    # print(f"Loaded {len(loaded_transcript)} entries")
    
    # # Get text at specific timestamp
    # text_at_2_seconds = get_text_by_timestamp(loaded_transcript, 2.0)
    # print(f"Text at 2 seconds: {text_at_2_seconds}")
    
    # # Get text in time range
    # text_range = get_text_in_range(loaded_transcript, 1.0, 4.3)
    # print(f"Text between 1-6 seconds: {[entry['text'] for entry in text_range]}")
    
    # # Search for text
    # search_results = search_text_in_transcript(loaded_transcript, "welcome")
    # print(f"Search results for 'welcome': {[entry['text'] for entry in search_results]}")