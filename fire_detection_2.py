# -*- coding: utf-8 -*-
"""fire detection 2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/11k0yEgmVG6XcsimH7KOsxN5QC6of3POY
"""

from google.colab import drive
drive.mount('/content/drive')

!unzip /content/drive/MyDrive/archive.zip

import os
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, Input

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import PIL.Image

train_dir='/content/the_wildfire_dataset_2n_version/train'
test_dir='/content/the_wildfire_dataset_2n_version/test'
val_dir='/content/the_wildfire_dataset_2n_version/val'

img_height, img_width = 224, 224
batch_size = 32

train_datagen = ImageDataGenerator(rescale=1./255,
                                   rotation_range=20,
                                   zoom_range=0.2,
                                   horizontal_flip=True)

val_datagen = ImageDataGenerator(rescale=1./255)
test_datagen = ImageDataGenerator(rescale=1./255)

train_data = train_datagen.flow_from_directory(train_dir, target_size=(img_height, img_width),
                                               batch_size=batch_size, class_mode='categorical')

val_data = val_datagen.flow_from_directory(val_dir, target_size=(img_height, img_width),
                                           batch_size=batch_size, class_mode='categorical')

test_data = test_datagen.flow_from_directory(test_dir, target_size=(img_height, img_width),
                                             batch_size=batch_size, class_mode='categorical')

# List all the classes
classes = os.listdir(train_dir)
num_classes = len(classes)

# Display the class names
print(f'Number of Classes: {num_classes}')
print(f'Classes: {classes}')

model = Sequential([
    Input(shape=(img_height, img_width, 3)),
    Conv2D(32, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    Conv2D(128, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(num_classes, activation='softmax')
])

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

history = model.fit(train_data,
                    validation_data=val_data,
                    epochs=10)

loss, acc = model.evaluate(test_data)
print(f'Test Accuracy: {acc*100:.2f}%')

model.save('forest_fire_detector.h5')

!pip install streamlit
import streamlit as st

#Load your trained model
model = load_model('forest_fire_detector.h5')

# Define your class labels (same as in training)
class_names = ['fire', 'no_fire']  # Update if you have different labels

# Streamlit app UI
st.set_page_config(page_title="Forest Fire Detector", layout="centered")
st.title("🔥 Forest Fire Detection App 🌲")
st.write("Upload an image to check if it shows signs of a forest fire.")

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    img = Image.open(uploaded_file).convert('RGB')
    st.image(img, caption='Uploaded Image', use_column_width=True)

    # Preprocess the image
    img = img.resize((224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Predict
    prediction = model.predict(img_array)
    class_index = np.argmax(prediction)
    predicted_label = class_names[class_index]
    confidence = prediction[0][class_index] * 100

    # Show result
    st.write(f"### Prediction: `{predicted_label.upper()}`")
    st.write(f"Confidence: `{confidence:.2f}%`")

    if predicted_label == 'fire':
        st.error("⚠️ Fire Detected! Take action immediately!")
    else:
        st.success("✅ No Fire Detected. Environment seems safe.")