import cv2
import numpy as np
import base64
try:
    try:
        from fer import FER
    except ImportError:
        from fer.fer import FER
    FER_AVAILABLE = True
except ImportError:
    print("Warning: FER library or dependencies (tensorflow/opencv) not found. Face emotion detection will be disabled.")
    FER_AVAILABLE = False
import time

class FaceEmotionDetector:
    def __init__(self):
        if FER_AVAILABLE:
            self.detector = FER(mtcnn=False) # Use default detector for speed
        else:
            self.detector = None

    def detect_emotion(self, capture_duration=3):
        """Captures video for a few seconds and returns the average emotion."""
        if not FER_AVAILABLE:
            return None
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Warning: Could not open webcam for face emotion detection.")
            return None

        emotions_list = []
        start_time = time.time()

        print(f"Capturing face emotions for {capture_duration} seconds...")
        
        while time.time() - start_time < capture_duration:
            ret, frame = cap.read()
            if not ret:
                break

            # Analyze the frame
            result = self.detector.detect_emotions(frame)
            if result:
                # result is a list of dicts: [{'box': [], 'emotions': {'happy': 0.1, ...}}]
                res = result[0]
                emotions_list.append(res['emotions'])
                
                # Draw box and emotion on frame for visual feedback
                x, y, w, h = res['box']
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                dominant = max(res['emotions'], key=res['emotions'].get)
                score = res['emotions'][dominant]
                label = f"{dominant}: {score:.2f}"
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # Display the frame so user can see analysis
            cv2.imshow('Face Emotion Analysis - Logging...', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        if not emotions_list:
            return None

        # Average the emotions
        avg_emotions = {}
        for emotion in emotions_list[0].keys():
            avg_emotions[emotion] = sum(e[emotion] for e in emotions_list) / len(emotions_list)

        return avg_emotions

    def detect_emotion_from_base64(self, base64_image):
        """Analyzes emotion from a base64 encoded image (for web integration)"""
        if not FER_AVAILABLE or not self.detector:
            return None
        
        try:
            # Remove data URL prefix if present
            if ',' in base64_image:
                base64_image = base64_image.split(',')[1]
            
            # Decode base64 to image
            img_data = base64.b64decode(base64_image)
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return None
            
            # Analyze the frame
            result = self.detector.detect_emotions(frame)
            
            if result and len(result) > 0:
                emotions = result[0]['emotions']
                return emotions
            
            return None
            
        except Exception as e:
            print(f"Error detecting emotion from base64: {e}")
            return None

if __name__ == "__main__":
    detector = FaceEmotionDetector()
    print(detector.detect_emotion())
