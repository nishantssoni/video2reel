# YouTube Video Segmentation & Processing Tool (Video2reel)
![Diagram](samples/logo_.png)

### An automated tool that downloads YouTube videos, analyzes their transcripts using AI, extracts viral segments, and creates face-tracked cropped videos with embedded subtitles.

## Features

- 📹 **YouTube Video Download**: Download videos in various qualities with audio
- 📝 **Transcript Extraction**: Automatically fetch YouTube transcripts
- 🤖 **AI-Powered Segmentation**: Use OpenAI Compatible models to identify viral segments (60-300 seconds)
- ✂️ **Video Clipping**: Extract segments based on AI analysis
- 👤 **Face Tracking**: Dynamic face-centered cropping with smooth transitions
- 📺 **Subtitle Integration**: Embed subtitles into processed videos
- 🎥 **Batch Processing**: Process multiple segments automatically

## Project Structure

```
project/
├── main.py                 # Main orchestration script
├── video_downloader.py     # YouTube video downloading
├── transcript.py          # Transcript management and SRT generation
├── clipper.py             # Video segment extraction
├── track_n_merge.py       # Face tracking and cropping
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
└── generated/            # Auto-created output directory
    ├── downloaded_videos/ # Your youtube Downloaded video
    ├── video/            # Raw video segments
    ├── merged/           # Final processed videos
    ├── subtitles/        # SRT subtitle files
    ├── transcripts/      # JSON transcript data
    └── lable/           # Segment labels
```

## Prerequisites

- Python 3.8+
- FFmpeg (for video processing)
- OpenAI API key
- MediaPipe for face detection
- OpenCV for video processing

## Installation

### 1. Clone the Repository
```
git clone <your-repo-url>
cd youtube-video-processor
```

### 2. Install System Dependencies

**Ubuntu/Debian:**
```
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```
brew install ffmpeg
```

**Windows:**
Download FFmpeg from https://ffmpeg.org/download.html and add to PATH

### 3. Install Python Dependencies
```
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

### Basic Usage
```
python main.py
```

When prompted, enter a YouTube video ID (e.g., `XeN6eGO6FVQ` from `https://www.youtube.com/watch?v=XeN6eGO6FVQ`)

### Manual Component Usage

#### 1. Download YouTube Video
```
from video_downloader import download_youtube_video

success = download_youtube_video(
    'video_id_here',
    output_path="downloads",
    quality="best",  # or "720p", "1080p", "worst"
    output_filename="my_video.mp4"
)
```

#### 2. Extract and Process Transcript
```
from transcript import TranscriptManager

manager = TranscriptManager('video_id_here')
transcript = manager.get_transcript()
manager.save_transcript()
```

#### 3. Generate Video Clips
```
from clipper import generate_video_clips

# segments should be a list of dictionaries with start_time, end_time, etc.
generate_video_clips('input_video.mp4', segments)
```

#### 4. Face-Tracked Cropping
```
from track_n_merge import FaceTrackingCropper

cropper = FaceTrackingCropper(smoothing_factor=0.8)
success = cropper.process_video(
    input_path='input.mp4',
    output_path='output.mp4',
    subtitle_path='subtitles.srt'
)
```

## Configuration

### Video Quality Options
- `"best"` - Highest available quality
- `"worst"` - Lowest available quality  
- `"720p"`, `"1080p"` - Specific resolution

### Face Tracking Parameters
- `smoothing_factor` (0.0-1.0): Higher values = smoother but slower response to face movement

### AI Segmentation
The system prompts identify viral segments with these criteria:
- Duration: 60-300 seconds
- Accurate timestamps
- Engaging subtopics suitable for standalone videos

## Output Files

After processing, you'll find:

- **`generated/merged/`**: Final face-tracked videos with embedded subtitles
- **`generated/video/`**: Raw extracted video segments
- **`generated/subtitles/`**: SRT subtitle files for each segment
- **`generated/transcripts/segments.json`**: AI-analyzed segment data
- **`generated/lable/segment_labels.txt`**: Human-readable segment descriptions

## Data Models

### Segment Structure
```
{
    "start_time": 120.5,           # Start time in seconds
    "end_time": 245.3,             # End time in seconds
    "yt_title": "Viral Topic Title", # Suggested YouTube title
    "description": "Detailed description...", # Video description
    "duration": 124                # Duration in seconds
}
```

## Troubleshooting

### Common Issues

**FFmpeg not found:**
```
# Add FFmpeg to your system PATH
export PATH=$PATH:/path/to/ffmpeg/bin
```

**OpenAI API errors:**
- Verify your API key in `.env` file
- Check API quota and billing

**Video download fails:**
- Ensure the YouTube video is publicly accessible
- Check your internet connection
- Some videos may have download restrictions

**Face detection issues:**
- Works best with videos containing clear face shots
- May fall back to center cropping if no face detected
- Adjust `smoothing_factor` for different tracking behaviors

### Error Messages

**"Input file not found"**: Check file paths and ensure video downloaded successfully

**"Cannot open video"**: Video file may be corrupted or in unsupported format

**"FFmpeg error"**: Check FFmpeg installation and subtitle file format

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI API (I use GPT-4o-mini)
- MediaPipe for face detection
- yt-dlp for YouTube video downloading
- FFmpeg for video processing

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Search existing issues in the repository
3. Create a new issue with detailed information about your problem

---
## 🤝 Contribution
Contributions are welcome! Feel free to open issues or submit pull requests for suggestions, improvements, or bug fixes.

---

## 📜 License
This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

---

## 📬 Contact
For any questions or feedback, please contact [iamnishantsoni4@gmail.com](mailto:iamnishantsoni4@gmail.com).
### hit me on <a href="https://twitter.com/nishantssoni">Twitter</a>

---
**Note**: This tool is for educational and personal use. Ensure you comply with YouTube's Terms of Service and respect copyright laws when downloading and processing videos.
