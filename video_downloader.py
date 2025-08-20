import os
import yt_dlp

def download_youtube_video(
    video_id,
    output_path="downloads",
    quality="best",
    show_progress=True,
    output_filename=None  # NEW: custom filename parameter
):
    """
    Download YouTube video with audio merged using video ID.

    Args:
        video_id (str): YouTube video ID (e.g., 'XeN6eGO6FVQ')
        output_path (str): Directory to save the merged video (default: 'downloads')
        quality (str): Quality option - 'best', 'worst', or specific height like '720p', '1080p'
        show_progress (bool): Whether to show download progress (default: True)
        output_filename (str or None): Specify a custom output filename (e.g., 'my_video.mp4')
    Returns:
        bool: True if download successful, False otherwise
    """

    url = f"https://www.youtube.com/watch?v={video_id}"
    output_path = os.path.abspath(output_path)
    os.makedirs(output_path, exist_ok=True)

    def progress_hook(d):
        if show_progress:
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', 'N/A')
                speed = d.get('_speed_str', 'N/A')
                eta = d.get('_eta_str', 'N/A')
                print(f"\rDownloading... {percent} (Speed: {speed}, ETA: {eta})", end='', flush=True)
            elif d['status'] == 'finished':
                print("\nDownload finished. Processing...")

    try:
        if quality == "best":
            format_selector = 'bestvideo+bestaudio/best'
        elif quality == "worst":
            format_selector = 'worst'
        elif quality.endswith('p'):
            height = quality[:-1]
            format_selector = f'bestvideo[height<={height}]+bestaudio/best[height<={height}]'
        else:
            format_selector = 'best'

        # NEW: If output_filename is provided, use it directly for outtmpl
        if output_filename:
            # Sanitize filename and join with output path
            safe_filename = "".join(c for c in output_filename if c.isalnum() or c in (' .-_')).rstrip()
            outtmpl = os.path.join(output_path, safe_filename)
        else:
            outtmpl = os.path.join(output_path, '%(title)s.%(ext)s')

        ydl_opts = {
            'format': format_selector,
            'outtmpl': outtmpl,
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_hook] if show_progress else [],
            'quiet': not show_progress,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                if show_progress:
                    print("Could not retrieve video information.")
                return False

            if show_progress:
                print(f"Video Title: {info.get('title', 'Unknown')}")
                print("Downloading and merging video...")

            ydl.download([url])

            if show_progress:
                print("Download and merge complete!")

            return True

    except Exception as e:
        if show_progress:
            print(f"An error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    # Example usage:
    # https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ&start_radio=1
    success = download_youtube_video(
        'dQw4w9WgXcQ',
        output_path="downloads_main",
        output_filename="downloaded.mp4"
    )
    print(f"Video download: {'Successful' if success else 'Failed'}")
