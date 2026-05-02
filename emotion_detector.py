import numpy as np
import cv2
import os
from PIL import Image
import tensorflow as tf
from tensorflow import keras
import warnings
warnings.filterwarnings('ignore')

class EmotionDetector:
    """CNN Emotion Detector with Trained Model"""
    
    def __init__(self):
        self.emotions = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]
        self.emotion_map = {
            "angry": "angry",
            "disgust": "angry",
            "fear": "sad",
            "happy": "happy",
            "neutral": "neutral",
            "sad": "sad",
            "surprise": "surprise"
        }
        
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        self.model = self._load_model()
        
    def _load_model(self):
        try:
            model_path = os.path.join(os.path.dirname(__file__), "fer2013_model.h5")
            if os.path.exists(model_path):
                print(f"Loading CNN model...")
                model = keras.models.load_model(model_path)
                print("✅ CNN Model loaded!")
                return model
            else:
                print(f"Model not found: {model_path}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def predict(self, image_array):
        try:
            if self.model is None:
                return "neutral", 0.5
            
            if len(image_array.shape) == 3:
                gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
            else:
                gray = image_array
            
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5, minSize=(30, 30))
            
            if len(faces) == 0:
                return "neutral", 0.5
            
            face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = face
            
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (48, 48))
            face_roi = face_roi.astype('float32') / 255.0
            face_roi = np.expand_dims(face_roi, axis=0)
            face_roi = np.expand_dims(face_roi, axis=-1)
            
            predictions = self.model.predict(face_roi, verbose=0)
            emotion_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][emotion_idx])
            
            raw_emotion = self.emotions[emotion_idx]
            mapped_emotion = self.emotion_map.get(raw_emotion, "neutral")
            
            print(f"[CNN] {raw_emotion} ({confidence:.2f}) → {mapped_emotion}")
            
            return mapped_emotion, confidence
            
        except Exception as e:
            print(f"Error: {e}")
            return "neutral", 0.5
