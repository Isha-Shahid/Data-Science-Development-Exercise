import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os
import sys

# ✅ Define dataset path
train_dir = os.path.abspath("dataset/train")

# ✅ Check if dataset exists
if not os.path.exists(train_dir):
    print(f"❌ ERROR: Dataset folder not found at: {train_dir}")
    sys.exit(1)

print(f"📂 Training Directory Found: {train_dir}")

# ✅ Define CNN Model (Improved with Dropout)
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(150, 150, 1)),
    MaxPooling2D(2, 2),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),  # Prevent Overfitting
    Dense(1, activation='sigmoid')  # Binary classification
])

# ✅ Compile Model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# ✅ Data Augmentation for Better Generalization
train_datagen = ImageDataGenerator(
    rescale=1.0 / 255.0,
    rotation_range=15,
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.1,
    zoom_range=0.1,
    horizontal_flip=True,
    validation_split=0.2
)

# ✅ Load training data with a larger batch size (to handle large dataset)
batch_size = 64  # Increase to 64 or 128 for large dataset

try:
    train_generator = train_datagen.flow_from_directory(
        train_dir, target_size=(150, 150),
        batch_size=batch_size, color_mode='grayscale', class_mode='binary', subset='training'
    )

    val_generator = train_datagen.flow_from_directory(
        train_dir, target_size=(150, 150),
        batch_size=batch_size, color_mode='grayscale', class_mode='binary', subset='validation'
    )
except Exception as e:
    print(f"❌ ERROR: Unable to load images. Details: {str(e)}")
    sys.exit(1)

# ✅ Train Model with Early Stopping & Reduced Epochs
from tensorflow.keras.callbacks import EarlyStopping

early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

try:
    model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=10,  # Reduce number of epochs for efficiency
        callbacks=[early_stopping]
    )
except Exception as e:
    print(f"❌ ERROR: Model training failed. Details: {str(e)}")
    sys.exit(1)

# ✅ Save Model
try:
    model.save("pneumonia_model.keras")
    print("🎉 Model saved successfully as `pneumonia_model.keras`")
except Exception as e:
    print(f"❌ ERROR: Model saving failed. Details: {str(e)}")
