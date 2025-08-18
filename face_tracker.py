import cv2
import mediapipe as mp
import numpy as np
from typing import Tuple, Optional
import os

class FaceTrackingCropper:
    def __init__(self, smoothing_factor: float = 0.8):
        """
        Initialize the face tracking cropper.
        
        Args:
            smoothing_factor: Controls smoothness of tracking (0.0 = no smoothing, 1.0 = maximum smoothing)
        """
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,  # Use model 1 for better long-range detection
            min_detection_confidence=0.5
        )
        
        self.smoothing_factor = smoothing_factor
        self.last_center_x = None
        self.last_center_y = None
        
    def get_face_center(self, frame: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Detect face and return the center coordinates.
        
        Args:
            frame: Input frame
            
        Returns:
            Tuple of (center_x, center_y) or None if no face detected
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb_frame)
        
        if results.detections:
            # Get the first detected face
            detection = results.detections[0]
            bbox = detection.location_data.relative_bounding_box
            
            h, w = frame.shape[:2]
            
            # Calculate face center
            face_center_x = int((bbox.xmin + bbox.width / 2) * w)
            face_center_y = int((bbox.ymin + bbox.height / 2) * h)
            
            # Apply smoothing
            if self.last_center_x is not None and self.last_center_y is not None:
                face_center_x = int(self.smoothing_factor * self.last_center_x + 
                                  (1 - self.smoothing_factor) * face_center_x)
                face_center_y = int(self.smoothing_factor * self.last_center_y + 
                                  (1 - self.smoothing_factor) * face_center_y)
            
            self.last_center_x = face_center_x
            self.last_center_y = face_center_y
            
            return face_center_x, face_center_y
        
        # If no face detected, use last known position or center of frame
        if self.last_center_x is not None and self.last_center_y is not None:
            return self.last_center_x, self.last_center_y
        else:
            h, w = frame.shape[:2]
            return w // 2, h // 2
    
    def calculate_crop_region(self, frame: np.ndarray, face_center: Tuple[int, int]) -> Tuple[int, int, int, int]:
        """
        Calculate the optimal crop region for 9:16 aspect ratio without squeezing.
        
        Args:
            frame: Input frame
            face_center: Center coordinates of the detected face
            
        Returns:
            Tuple of (x1, y1, x2, y2) crop coordinates
        """
        h, w = frame.shape[:2]
        face_x, face_y = face_center
        
        # Calculate the largest possible 9:16 crop from the original frame
        # This ensures no stretching/squeezing occurs
        target_aspect_ratio = 9 / 16  # width / height for 9:16 format
        
        # Determine crop dimensions based on which dimension is limiting
        if w / h < target_aspect_ratio:
            # Width is limiting factor - use full width
            crop_width = w
            crop_height = int(w / target_aspect_ratio)
        else:
            # Height is limiting factor - use full height  
            crop_height = h
            crop_width = int(h * target_aspect_ratio)
        
        # Center the crop on the face, but keep within frame bounds
        crop_x1 = max(0, min(w - crop_width, face_x - crop_width // 2))
        crop_x2 = crop_x1 + crop_width
        
        crop_y1 = max(0, min(h - crop_height, face_y - crop_height // 2))
        crop_y2 = crop_y1 + crop_height
        
        return crop_x1, crop_y1, crop_x2, crop_y2
    
    def process_video(self, input_path: str, output_path: str, show_preview: bool = False) -> bool:
        """
        Process the video with face tracking and cropping to 9:16 without squeezing.
        
        Args:
            input_path: Path to input video
            output_path: Path to output video
            show_preview: Whether to show preview window during processing
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(input_path):
            print(f"Error: Input file '{input_path}' not found.")
            return False
        
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            print(f"Error: Cannot open video file '{input_path}'")
            return False
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"Processing video: {total_frames} frames at {fps} FPS")
        
        # Read first frame to determine crop dimensions
        ret, first_frame = cap.read()
        if not ret:
            print("Error: Cannot read first frame")
            cap.release()
            return False
        
        # Calculate crop region from first frame
        face_center = self.get_face_center(first_frame)
        crop_x1, crop_y1, crop_x2, crop_y2 = self.calculate_crop_region(first_frame, face_center)
        
        # Get final output dimensions (no resizing, just cropping)
        output_width = crop_x2 - crop_x1
        output_height = crop_y2 - crop_y1
        
        print(f"Output dimensions: {output_width}x{output_height} (9:16 aspect ratio)")
        
        # Reset video capture to beginning
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (output_width, output_height))
        
        frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Get face center
                face_center = self.get_face_center(frame)
                
                # Calculate crop region
                crop_x1, crop_y1, crop_x2, crop_y2 = self.calculate_crop_region(frame, face_center)
                
                # Crop the frame (no resizing to avoid squeezing)
                cropped_frame = frame[crop_y1:crop_y2, crop_x1:crop_x2]
                
                # Write frame directly without resizing
                out.write(cropped_frame)
                
                frame_count += 1
                
                # Show progress
                if frame_count % 30 == 0:  # Update every 30 frames
                    progress = (frame_count / total_frames) * 100
                    print(f"Progress: {progress:.1f}% ({frame_count}/{total_frames} frames)")
                
                # Show preview if requested
                if show_preview:
                    # Draw face center and crop region on original frame for preview
                    preview_frame = frame.copy()
                    cv2.circle(preview_frame, face_center, 10, (0, 255, 0), -1)
                    cv2.rectangle(preview_frame, (crop_x1, crop_y1), (crop_x2, crop_y2), (255, 0, 0), 2)
                    
                    # Resize for preview (maintain aspect ratio)
                    preview_height = 480
                    preview_width = int(preview_frame.shape[1] * preview_height / preview_frame.shape[0])
                    preview_frame = cv2.resize(preview_frame, (preview_width, preview_height))
                    
                    # Show output preview (maintain aspect ratio)
                    output_preview_height = 480
                    output_preview_width = int(cropped_frame.shape[1] * output_preview_height / cropped_frame.shape[0])
                    output_preview = cv2.resize(cropped_frame, (output_preview_width, output_preview_height))
                    
                    cv2.imshow('Original (Green dot: face center, Blue box: crop region)', preview_frame)
                    cv2.imshow('Cropped Output', output_preview)
                    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("Processing interrupted by user")
                        break
            
            print(f"\nProcessing complete! Output saved to: {output_path}")
            return True
            
        except KeyboardInterrupt:
            print("\nProcessing interrupted by user")
            return False
        except Exception as e:
            print(f"Error during processing: {str(e)}")
            return False
        finally:
            cap.release()
            out.release()
            if show_preview:
                cv2.destroyAllWindows()


# Example usage when importing as a module:
"""
from face_tracking_cropper import FaceTrackingCropper

cropper = FaceTrackingCropper(smoothing_factor=0.8)
success = cropper.process_video('input.mp4', 'output.mp4', show_preview=True)
"""

if __name__ == "__main__":
    # Example usage when running as a script:
    cropper = FaceTrackingCropper(smoothing_factor=0.8)
    success = cropper.process_video('downloaded_videos/videoplayback (1).mp4', 'output.mp4', show_preview=True)