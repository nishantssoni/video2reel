import os
import json
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from utils import fileSafe

class TranscriptManager:
    def __init__(self, video_id, folder="transcripts"):
        self.video_id = video_id
        self.folder = folder
        self.transcript = None          # Loaded transcript
        self.segments = None           # Loaded segments

    def get_transcript(self):
        """Download transcript from YouTube"""
        try:
            yt_api = YouTubeTranscriptApi()
            transcript_list = yt_api.list(self.video_id)
            self.transcript = transcript_list.find_transcript(["en"]).fetch().to_raw_data()
            return self.transcript
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def save_transcript(self):
        """Save transcript to JSON"""
        try:
            os.makedirs(self.folder, exist_ok=True)
            filename = os.path.join(self.folder, f"{self.video_id}_transcript.json")
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.transcript, f, ensure_ascii=False, indent=4)
            print(f"Transcript saved to: {filename}")
            return filename
        except Exception as e:
            print(f"Error saving transcript: {e}")
            return None

    def load_transcript(self):
        """Load transcript from JSON"""
        try:
            return self.transcript
        except Exception as e:
            print(f"Error loading transcript: {e}")
            return None

    def get_text_by_timestamp(self, timestamp):
        """Return text at a specific timestamp."""
        for entry in self.transcript:
            start = entry["start"]
            end = start + entry["duration"]
            if start <= timestamp < end:
                return entry["text"]
        return f"No text found at {timestamp} seconds"

    def get_text_in_range(self, start_time, end_time):
        """Return transcript entries within a time range."""
        result = []
        for entry in self.transcript:
            entry_start = entry["start"]
            entry_end = entry_start + entry["duration"]
            if entry_start < end_time and entry_end > start_time:
                result.append(entry)
        return result

    def search_text(self, search_term, case_sensitive=False):
        """Search transcript for a term."""
        results = []
        term = search_term if case_sensitive else search_term.lower()
        for entry in self.transcript:
            text = entry["text"] if case_sensitive else entry["text"].lower()
            if term in text:
                results.append(entry)
        return results

    def load_segments(self, segments_path):
        with open(segments_path, "r", encoding="utf-8") as f:
            self.segments = json.load(f)
        return self.segments

    def merge_segments_with_subtitles(self):
        """Merge loaded segments with currently loaded transcript."""
        if self.segments is None or self.transcript is None:
            raise Exception("Segments or transcript not loaded")

        merged_segments = []
        for seg in self.segments:
            subs = self.get_text_in_range(seg["start_time"], seg["end_time"])
            seg["subtitles"] = [
                    {
                        "start": entry["start"] - seg["start_time"],
                        "text": entry["text"]
                    }
                    for entry in subs
                ]

            merged_segments.append(seg)

        self.segments = merged_segments
        return merged_segments

    def merge_segments_with_subtitles_files(self, segments_path, transcript_path, output_path):
        """Load files, merge subtitles, and save output."""
        with open(segments_path, "r", encoding="utf-8") as f:
            self.segments = json.load(f)
        with open(transcript_path, "r", encoding="utf-8") as f:
            self.transcript = json.load(f)

        merged_segments = []
        for seg in self.segments:
            subs = []
            for entry in self.transcript:
                entry_start = entry["start"]
                entry_end = entry_start + entry["duration"]
                if entry_start < seg["end_time"] and entry_end > seg["start_time"]:
                    relative_start = entry_start - seg["start_time"]
                    subs.append({"start": relative_start, "text": entry["text"]})
            seg["subtitles"] = subs
            merged_segments.append(seg)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(merged_segments, f, ensure_ascii=False, indent=4)

        self.segments = merged_segments
        return merged_segments

    def json_to_srt(self, segment_index, output_srt_path):
        """Convert subtitles for one segment (by index) into an SRT file."""
        def seconds_to_srt_time(seconds):
            hours, remainder = divmod(int(seconds), 3600)
            minutes, remainder = divmod(remainder, 60)
            secs = int(seconds % 60)
            millis = int((seconds - int(seconds)) * 1000)
            return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

        if self.segments is None:
            raise Exception("Segments not loaded or merged")

        segment = self.segments[segment_index]
        subtitles = segment["subtitles"]
        srt_lines = []

        for idx, sub in enumerate(subtitles, 1):
            abs_start = max(sub["start"], 0)
            if idx < len(subtitles):
                abs_end = max(subtitles[idx]["start"], 0)
            else:
                abs_end = segment["duration"]

            srt_lines.append(
                f"{idx}\n"
                f"{seconds_to_srt_time(abs_start)} --> {seconds_to_srt_time(abs_end)}\n"
                f"{sub['text']}\n"
            )

        with open(output_srt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(srt_lines))
    
    def export_all_srts(self, output_folder="generated/subtitles"):
        """
        Export an SRT file for every segment using json_to_srt().
        File name is based on the segment's own 'yt_title'.
        """
        if self.segments is None:
            raise Exception("Segments not loaded or merged")

        os.makedirs(output_folder, exist_ok=True)

        for idx, segment in enumerate(self.segments):
            # get per-segment title
            title = segment.get("yt_title", f"segment_{idx + 1}")
            # make the title safe for a file name
            safe_title = fileSafe(title)
            filename = os.path.join(output_folder, f"{safe_title}.srt")

            self.json_to_srt(idx, filename)
            print(f"Saved: {filename}")


if __name__ == "__main__":
    manager = TranscriptManager("XeN6eGO6FVQ")
    manager.get_transcript()
    print(manager.load_transcript())
    # manager.save_transcript()
    # manager.load_segments("transcripts/segments.json")
    # manager.merge_segments_with_subtitles()
    # # manager.json_to_srt(0, "segment0.srt")
    # manager.export_all_srts()