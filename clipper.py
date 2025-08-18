import os
import json
import subprocess
from utils import fileSafe

def generate_video_clips(filename, parsed_content, output_dir="generated_clips"):
    """
    Generates video/audio clips from a source video based on segment details.
    Video (no audio) clips are saved to <output_dir>/video/
    Audio-only clips are saved to <output_dir>/audio/
    Segment label file is also generated.
    """
    # Create main and sub output directories
    video_dir = os.path.join(output_dir, "video")
    audio_dir = os.path.join(output_dir, "audio")
    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)

    segment_labels = []

    # Save segments to JSON
    json_path = os.path.join("transcripts/segments.json")
    with open(json_path, 'w') as f:
        json.dump(parsed_content, f, indent=4)

    # Process each segment
    for i, segment in enumerate(parsed_content):
        start_time = segment['start_time']
        end_time = segment['end_time']
        yt_title  = fileSafe(segment['yt_title'])
        description = segment['description']
        duration = segment['duration']

        # Build file paths
        video_output = os.path.join(video_dir, f"{yt_title}.mp4")
        audio_output = os.path.join(audio_dir, f"{yt_title}.aac")

        # --- Create video only (no audio) ---
        video_cmd = (
            f'ffmpeg -i "{filename}" -ss {start_time} -to {end_time} '
            f'-an -c:v libx264 "{video_output}"'
        )

        # --- Create audio only ---
        audio_cmd = (
            f'ffmpeg -i "{filename}" -ss {start_time} -to {end_time} '
            f'-vn -acodec copy "{audio_output}"'
        )

        subprocess.call(video_cmd, shell=True)
        subprocess.call(audio_cmd, shell=True)

        label = (
            f"Sub-Topic {i+1}: {yt_title}, Duration: {duration}s\n"
            f"Description: {description}\n"
        )
        segment_labels.append(label)

    # Save segment labels
    labels_path = os.path.join(output_dir, "segment_labels.txt")
    with open(labels_path, 'w') as f:
        for label in segment_labels:
            f.write(label + "\n")

    print(f"Finished. Video and audio saved in {output_dir}/video and {output_dir}/audio.")

# Example usage
if __name__ == "__main__":
    with open("transcripts/segments.json", 'r') as f:
        parsed_content = json.load(f)
    generate_video_clips('downloaded_videos/video.mp4', parsed_content)


