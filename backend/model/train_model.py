import os
import cv2
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("🚀 EMOTION DETECTION MODEL TRAINING")
print("=" * 70)

# ==================== DATASET CONFIGURATION ====================
DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "FER2013")
TRAIN_PATH = os.path.join(DATASET_PATH, "train")
TEST_PATH = os.path.join(DATASET_PATH, "test")

EMOTIONS = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]
IMG_SIZE = 48
BATCH_SIZE = 32
EPOCHS = 20

print(f"Dataset path: {DATASET_PATH}")
print(f"Train path: {TRAIN_PATH}")
print(f"Test path: {TEST_PATH}")

# ==================== CHECK DATASET ====================
print("\n📊 Checking dataset structure...")

if not os.path.exists(TRAIN_PATH):
    print(f"❌ ERROR: Train path not found: {TRAIN_PATH}")
    exit(1)

train_counts = {}
for emotion in os.listdir(TRAIN_PATH):
    emotion_path = os.path.join(TRAIN_PATH, emotion)
    if os.path.isdir(emotion_path):
        count = len(os.listdir(emotion_path))
        train_counts[emotion] = count
        print(f"  ✅ {emotion}: {count} images")

print(f"\nTotal training images: {sum(train_counts.values())}")

# ==================== LOAD DATASET ====================
print("\n📂 Loading dataset...")

def load_images(path, emotion_labels):
    X = []
    y = []
    
    for emotion_idx, emotion in enumerate(emotion_labels):
        emotion_path = os.path.join(path, emotion)
        if not os.path.exists(emotion_path):
            print(f"  ⚠️  Skipping {emotion} (folder not found)")
            continue
        
        images = os.listdir(emotion_path)
        print(f"  Loading {emotion}... ({len(images)} images)")
        
        for idx, img_file in enumerate(images):
            try:
                img_path = os.path.join(emotion_path, img_file)
                img = Image.open(img_path).convert('L')  # Convert to grayscale
                img = img.resize((IMG_SIZE, IMG_SIZE))
                img_array = np.array(img)
                
                X.append(img_array)
                y.append(emotion_idx)
                
                if (idx + 1) % 1000 == 0:
                    print(f"    → {idx + 1}/{len(images)}")
                    
            except Exception as e:
                print(f"    ❌ Error loading {img_file}: {e}")
                continue
    
    return np.array(X), np.array(y)

X_train, y_train = load_images(TRAIN_PATH, EMOTIONS)
X_test, y_test = load_images(TEST_PATH, EMOTIONS)

print(f"✅ Training data: {X_train.shape}")
print(f"✅ Testing data: {X_test.shape}")

# ==================== NORMALIZE ====================
print("\n🔧 Normalizing data...")

X_train = X_train.astype('float32') / 255.0
X_test = X_test.astype('float32') / 255.0

# Add channel dimension
X_train = np.expand_dims(X_train, axis=-1)
X_test = np.expand_dims(X_test, axis=-1)

print(f"✅ Train shape: {X_train.shape}")
print(f"✅ Test shape: {X_test.shape}")

# ==================== BUILD MODEL ====================
print("\n🧠 Building CNN model...")

model = keras.Sequential([
    # Block 1
    layers.Conv2D(64, (3, 3), activation='relu', padding='same', input_shape=(IMG_SIZE, IMG_SIZE, 1)),
    layers.BatchNormalization(),
    layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2, 2)),
    layers.Dropout(0.25),
    
    # Block 2
    layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
    layers.BatchNormalization(),
    layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2, 2)),
    layers.Dropout(0.25),
    
    # Block 3
    layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
    layers.BatchNormalization(),
    layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2, 2)),
    layers.Dropout(0.25),
    
    # Flatten and Dense
    layers.Flatten(),
    layers.Dense(512, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(len(EMOTIONS), activation='softmax')
])

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print("✅ Model built successfully!")
print(f"\nModel Summary:")
model.summary()

# ==================== TRAIN MODEL ====================
print("\n" + "=" * 70)
print("🚂 TRAINING MODEL")
print("=" * 70)

history = model.fit(
    X_train, y_train,
    batch_size=BATCH_SIZE,
    epochs=EPOCHS,
    validation_split=0.1,
    verbose=1
)

# ==================== EVALUATE ====================
print("\n" + "=" * 70)
print("📈 EVALUATING MODEL")
print("=" * 70)

test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f"Test Loss: {test_loss:.4f}")
print(f"Test Accuracy: {test_accuracy:.4f}")

# ==================== SAVE MODEL ====================
print("\n💾 Saving model...")

model_path = os.path.join(os.path.dirname(__file__), "fer2013_model.h5")
model.save(model_path)

print(f"✅ Model saved: {model_path}")
print(f"✅ File size: {os.path.getsize(model_path) / 1024 / 1024:.2f} MB")

print("\n" + "=" * 70)
print("✅ TRAINING COMPLETE!")
print("=" * 70)
