import os
import json

def fileSafe(text):
    safe_text = "".join(c if c.isalnum() or c in " _-" else "_" for c in text)
    return safe_text


def return_files_in_directory(directory):
    lst = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            lst.append(file[:-4])
    return lst


def create_generated_structure():
    # Create main directory
    main_dir = 'generated'
    os.makedirs(main_dir, exist_ok=True)
    
    # Create 4 subfolders
    subfolders = ['video', 'merged', 'subtitles', 'transcripts','downloaded_videos','lable']
    
    for folder in subfolders:
        os.makedirs(os.path.join(main_dir, folder), exist_ok=True)
    
    print(f"✅ Created '{main_dir}' directory with folders: {', '.join(subfolders)}")


def save_segment_to_json(segment):
    json_path = os.path.join("generated/transcripts/segments.json")
    with open(json_path, 'w') as f:
        json.dump(segment, f, indent=4)