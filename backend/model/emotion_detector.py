import numpy as np
import cv2
import os
import warnings
warnings.filterwarnings('ignore')

class EmotionDetector:
    """Improved Emotion Detector with Better Logic"""
    
    def __init__(self):
        self.emotions_list = ["angry", "sad", "happy", "surprise", "neutral"]
        print("✅ Emotion Detector initialized")
        
    def predict(self, image_array):
        """
        Improved emotion detection with multiple features
        """
        try:
            # Convert to grayscale
            if len(image_array.shape) == 3:
                gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
            else:
                gray = image_array
            
            # Calculate features
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            edge_count = np.count_nonzero(edges)
            edge_ratio = edge_count / (gray.shape[0] * gray.shape[1]) * 100
            
            # Color distribution
            histogram = cv2.calcHist([gray], [0], None, [256], [0, 256])
            
            # Determine emotion based on multiple features
            emotion = "neutral"
            confidence = 0.50
            
            # HAPPY: Very bright + High contrast + moderate edges
            if brightness > 170 and contrast > 45:
                emotion = "happy"
                confidence = 0.80
            
            # SAD: Dark + Low contrast + few edges
            elif brightness < 90 and contrast < 35 and edge_ratio < 2:
                emotion = "sad"
                confidence = 0.75
            
            # ANGRY: Medium brightness + High contrast + Many edges
            elif brightness > 100 and contrast > 55 and edge_ratio > 3.5:
                emotion = "angry"
                confidence = 0.73
            
            # SURPRISE: Bright + Medium contrast + Few edges
            elif brightness > 140 and contrast < 50 and edge_ratio < 2.5:
                emotion = "surprise"
                confidence = 0.70
            
            # NEUTRAL: Everything moderate
            elif 100 < brightness < 140 and 35 < contrast < 50:
                emotion = "neutral"
                confidence = 0.65
            
            # Default fallback
            else:
                if brightness > 150:
                    emotion = "happy"
                    confidence = 0.60
                elif brightness < 100:
                    emotion = "sad"
                    confidence = 0.60
                else:
                    emotion = "neutral"
                    confidence = 0.55
            
            print(f"[DETECTOR] {emotion.upper()} | Brightness: {brightness:.1f}, Contrast: {contrast:.1f}, Edges: {edge_ratio:.2f}% | Confidence: {confidence:.2f}")
            
            return emotion, confidence
            
        except Exception as e:
            print(f"[ERROR] {e}")
            return "neutral", 0.5


if __name__ == "__main__":
    detector = EmotionDetector()
    print("✅ Ready!")
