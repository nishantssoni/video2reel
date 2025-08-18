import os
import json
import subprocess
from utils import fileSafe

def generate_video_clips(filename, parsed_content, output_dir="generated_clips"):
    """
    Generates video clips from a source video based on segment details.
    Saves labels and segments to files in output_dir.
    
    Arguments:
        filename (str): Path to the source video file.
        parsed_content (list): List of dictionaries with segment info.
        video_title (str): Title for output files.
        output_dir (str): Output directory to store segments and files.
    """
    os.makedirs(output_dir, exist_ok=True)
    segment_labels = []

    # Save segments to JSON
    json_path = os.path.join("transcripts/segments.json")
    with open(json_path, 'w') as f:
        json.dump(parsed_content, f, indent=4)
    
    # Load segments back (optional, remove if not needed)
    with open("transcripts/segments.json", 'r') as f:
        parsed_content = json.load(f)


    # Process each segment
    for i, segment in enumerate(parsed_content):
        start_time = segment['start_time']
        end_time = segment['end_time']
        yt_title = fileSafe(segment['yt_title'])
        description = segment['description']
        duration = segment['duration']

        output_file = f"{output_dir}/{yt_title}.mp4"
        command = f'ffmpeg -i "{filename}" -ss {start_time} -to {end_time} -c:v libx264 -c:a aac -strict experimental -b:a 192k "{output_file}"'
        subprocess.call(command, shell=True)
        label = f"Sub-Topic {i+1}: {yt_title}, Duration: {duration}s\nDescription: {description}\n"
        segment_labels.append(label)

    # Save segment labels
    labels_path = os.path.join(output_dir, "segment_labels.txt")
    with open(labels_path, 'w') as f:
        for label in segment_labels:
            f.write(label + "\n")


if __name__ == "__main__":
    # Example usage
    generate_video_clips('downloaded_videos/video.mp4')
