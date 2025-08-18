import json






if __name__ == "__main__":
    with open("merged_segments.json", "r", encoding="utf-8") as f:
        segment = json.load(f)
    json_to_srt(segment[0], "output.srt")
