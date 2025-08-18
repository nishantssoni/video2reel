import os

def fileSafe(text):
    safe_text = "".join(c if c.isalnum() or c in " _-" else "_" for c in text)
    return safe_text


def return_files_in_directory(directory):
    lst = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            lst.append(file[:-4])
    return lst

print(return_files_in_directory("generated_clips/video"))