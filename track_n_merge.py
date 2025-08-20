import cv2
import mediapipe as mp
import numpy as np
from typing import Tuple, Optional
import os
import subprocess
import tempfile


class FaceTrackingCropper:
    def __init__(self, smoothing_factor: float = 0.8):
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,
            min_detection_confidence=0.5
        )
        self.smoothing_factor = smoothing_factor
        self.last_center_x = None
        self.last_center_y = None

    def get_face_center(self, frame: np.ndarray) -> Tuple[int, int]:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb_frame)

        if results.detections:
            detection = results.detections[0]
            bbox = detection.location_data.relative_bounding_box
            h, w = frame.shape[:2]
            cx = int((bbox.xmin + bbox.width / 2) * w)
            cy = int((bbox.ymin + bbox.height / 2) * h)

            if self.last_center_x is not None and self.last_center_y is not None:
                cx = int(self.smoothing_factor * self.last_center_x + (1 - self.smoothing_factor) * cx)
                cy = int(self.smoothing_factor * self.last_center_y + (1 - self.smoothing_factor) * cy)

            self.last_center_x = cx
            self.last_center_y = cy
            return cx, cy

        if self.last_center_x is not None and self.last_center_y is not None:
            return self.last_center_x, self.last_center_y

        h, w = frame.shape[:2]
        return w // 2, h // 2

    def calculate_crop_region(self, frame: np.ndarray, face_center: Tuple[int, int]) -> Tuple[int, int, int, int]:
        h, w = frame.shape[:2]
        cx, cy = face_center
        aspect = 9 / 16

        if w / h < aspect:
            cw = w
            ch = int(w / aspect)
        else:
            ch = h
            cw = int(h * aspect)

        x1 = max(0, min(w - cw, cx - cw // 2))
        y1 = max(0, min(h - ch, cy - ch // 2))
        return x1, y1, x1 + cw, y1 + ch

    def process_video(self, input_path: str, output_path: str, subtitle_path: str) -> bool:
        """
        Process video with face tracking crop and preserve audio.
        """
        if not os.path.exists(input_path):
            print(f"Input file not found: {input_path}")
            return False

        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            print(f"Cannot open video: {input_path}")
            return False

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"Processing {total_frames} frames ({fps:.2f} FPS)")

        # Create temporary file for video without audio
        temp_video = tempfile.mktemp(suffix='.mp4')
        
        # Get first frame to determine output dimensions
        ret, first_frame = cap.read()
        if not ret:
            cap.release()
            return False
        
        center = self.get_face_center(first_frame)
        x1, y1, x2, y2 = self.calculate_crop_region(first_frame, center)
        out_width = x2 - x1
        out_height = y2 - y1
        
        print(f"Output dimensions: {out_width}x{out_height}")
        
        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_video, fourcc, fps, (out_width, out_height))
        
        # Reset to beginning
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            center = self.get_face_center(frame)
            x1, y1, x2, y2 = self.calculate_crop_region(frame, center)
            
            # Crop the frame
            cropped = frame[y1:y2, x1:x2]
            
            # Resize if dimensions don't match (edge case)
            if cropped.shape[:2] != (out_height, out_width):
                cropped = cv2.resize(cropped, (out_width, out_height))
            
            out.write(cropped)
            
            frame_idx += 1
            if frame_idx % 50 == 0:
                print(f"  -> {frame_idx}/{total_frames} frames processed")
        
        cap.release()
        out.release()
        
        print("✔ Video processing complete, adding audio...")
        # Combine cropped video with original audio using FFmpeg
        ffmpeg_cmd = [
            'ffmpeg', '-y',  # -y to overwrite output file
            '-i', temp_video,  # cropped video
            '-i', input_path,  # original video (for audio)
            '-vf', f'subtitles={subtitle_path}',  # add subtitles filter
            '-c:v', 'libx264',  # video codec
            '-c:a', 'aac',      # audio codec
            '-map', '0:v:0',    # video from first input
            '-map', '1:a:0',    # audio from second input
            '-shortest',        # match shortest stream
            output_path
        ]
        
        try:
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)
            print("✔ Audio merged successfully")
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e}")
            print(f"stderr: {e.stderr}")
            return False
        finally:
            # Clean up temporary file
            if os.path.exists(temp_video):
                os.remove(temp_video)
        
        print(f"✔ Final output: {output_path}")
        return True


if __name__ == "__main__":
    cropper = FaceTrackingCropper(smoothing_factor=0.8)
    
    input_video = 'generated_clips/video/Cultivating a Growth Mindset: Dopamine and Effort.mp4'
    subtitle_path = 'generated_clips/subtitles/Cultivating a Growth Mindset_ Dopamine and Effort.srt'
    output_video = 'dynamic_cropped_output.mp4'
    
    success = cropper.process_video(input_video, output_video, subtitle_path)
    
    if success:
        print("Video cropping completed successfully!")
    else:
        print("Video processing failed!")