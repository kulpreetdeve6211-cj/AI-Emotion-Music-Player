import os
import cv2
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("🚂 QUICK MODEL TRAINING")
print("=" * 70)

# ==================== LOAD DATA ====================
DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "FER2013")
TRAIN_PATH = os.path.join(DATASET_PATH, "train")
TEST_PATH = os.path.join(DATASET_PATH, "test")

EMOTIONS = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]
IMG_SIZE = 48

print(f"\nLoading from: {TRAIN_PATH}")

X_train = []
y_train = []

for emotion_idx, emotion in enumerate(EMOTIONS):
    emotion_path = os.path.join(TRAIN_PATH, emotion)
    if not os.path.exists(emotion_path):
        print(f"⚠️  {emotion} not found, skipping...")
        continue
    
    images = os.listdir(emotion_path)
    print(f"Loading {emotion}... ({len(images)} images)")
    
    count = 0
    for img_file in images[:500]:  # Limit to 500 per emotion for speed
        try:
            img_path = os.path.join(emotion_path, img_file)
            img = Image.open(img_path).convert('L')
            img = img.resize((IMG_SIZE, IMG_SIZE))
            img_array = np.array(img)
            
            X_train.append(img_array)
            y_train.append(emotion_idx)
            count += 1
        except:
            continue
    
    print(f"  ✅ Loaded {count} images")

X_train = np.array(X_train)
y_train = np.array(y_train)

print(f"\n✅ Total training data: {X_train.shape}")

# Normalize
X_train = X_train.astype('float32') / 255.0
X_train = np.expand_dims(X_train, axis=-1)

# ==================== BUILD & TRAIN ====================
print("\n🧠 Building and training model...")

model = keras.Sequential([
    layers.Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=(IMG_SIZE, IMG_SIZE, 1)),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2, 2)),
    layers.Dropout(0.25),
    
    layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2, 2)),
    layers.Dropout(0.25),
    
    layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2, 2)),
    layers.Dropout(0.25),
    
    layers.Flatten(),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(7, activation='softmax')
])

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print("Training...")
history = model.fit(
    X_train, y_train,
    batch_size=32,
    epochs=10,
    validation_split=0.2,
    verbose=1
)

# ==================== SAVE ====================
model_path = os.path.join(os.path.dirname(__file__), "fer2013_model_trained.h5")
model.save(model_path)

print(f"\n✅ Model saved: {model_path}")
print(f"✅ File size: {os.path.getsize(model_path) / 1024 / 1024:.2f} MB")
