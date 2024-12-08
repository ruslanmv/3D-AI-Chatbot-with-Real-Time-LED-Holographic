# **Building an Interactive 3D Chatbot with Real-Time Holographic LED Fan Integration: Step-by-Step Guide**

This tutorial demonstrates how to create an **interactive 3D chatbot** with real-time animations, powered by **ChatGPT** and displayed on **Missyou** or **GIWOX holographic LED fans**. We integrate a 3D model, customize animations, and synchronize lip sync with chatbot responses.

## Introduction
Interactive 3D chatbots combined with **LED holographic fans** bring a futuristic dimension to human-computer interaction. This tutorial extends the concept by integrating **ChatGPT** with **3D holographic fans** (Missyou and GIWOX), enabling real-time conversation and animated chatbot displays in 3D.

This project combines several Python packages to create an interactive 3D chatbot, integrating ChatGPT for conversational responses, real-time animations for a 3D model, and holographic LED fan technology for display. Each package contributes to a specific aspect of the pipeline, ensuring smooth interaction between the chatbot, 3D character, and holographic display.

## Example of prototype

![Example GIF](./assets/video.gif) 
From  3D holographic fan-Cindy

Below is a table summarizing the primary Python packages used in this project, their roles, and how they enable the chatbot and holographic integration.

---

### **Overview Table**

| **Package**       | **Description**                   | **File Types**       | **ChatGPT Integration**                                 | **3D Chatbot + LED Fan**                                 | **3D Chatbot AI Integration**                                                                                   |
|--------------------|-----------------------------------|-----------------------|---------------------------------------------------------|----------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| `matplotlib`      | A versatile plotting library for generating simple 3D animations. | Rendered Frames (PNG) | - Display chatbot responses as text or gestures in 3D   | - Real-time gesture animations for chatbot display       | - **3D Chatbot:** Create dynamic animations tied to ChatGPT responses.                                          |
| `openai`          | OpenAI's library for accessing ChatGPT and GPT models. | Text                  | - Generate intelligent chatbot responses                | - Drive animations and lip sync based on chatbot text    | - **AI-driven expressions:** Determine animations and expressions based on conversation context.                 |
| `Pillow`          | Python Imaging Library for image processing and format conversion. | PNG                   | - Enhance or modify chatbot-generated frames            | - Convert animations to fan-compatible formats           | - **Lip sync simulation:** Adjust animations to match speech phonemes dynamically.                              |
| `requests`        | A library for sending HTTP requests to APIs. | API (HTTP)            | - Automate chatbot-to-fan communication                 | - Stream chatbot animations and text to holographic fans | - **Seamless streaming:** Enable real-time frame uploads to holographic displays.                               |
| `pygame`          | A library for real-time graphics and game development. | Real-time Display     | - Simulate animations locally for debugging             | - Preview holographic animations before streaming        | - **Real-time rendering:** Test animations in a graphical window before finalizing for LED fans.                |
| `pygltflib`       | A library for working with glTF/GLB 3D model files. | glTF/GLB              | - Customize 3D character animations via API             | - Render and animate chatbot character models            | - **3D model integration:** Adjust animations and blend shapes based on chatbot emotions and phoneme analysis.  |
| `gtts`            | Google Text-to-Speech for speech synthesis. | MP3                   | - Convert chatbot responses into speech audio           | - Synchronize audio with 3D lip animations               | - **Text-to-Speech:** Generate spoken responses tied to chatbot text output.                                    |

---

### **How These Packages Work Together**
- **Core AI Integration**:
  - `openai` generates intelligent chatbot responses based on user input, serving as the brain of the chatbot.
  
- **3D Visualization and Animation**:
  - `matplotlib` dynamically renders 3D animations representing the chatbot's response, while `pygltflib` manages detailed 3D character animations.
  - `pygame` serves as a testing environment for previewing animations before sending them to the holographic fan.

- **Image Processing and Holographic Streaming**:
  - `Pillow` processes the generated frames, ensuring compatibility with the holographic LED fan's display requirements.
  - `requests` streams the processed frames to the LED fan's API for real-time visualization.

- **Audio and Lip Sync**:
  - `gtts` synthesizes speech for chatbot responses, while `pygltflib` adjusts the character's mouth animations to match the audio using phoneme analysis.
---

## **Pipeline Overview**

```mermaid
graph TD
    subgraph "User Interaction"
        A[User Speaks] --> B(Speech-to-Text)
    end

    subgraph "Natural Language Processing (NLP)"
        B --> C{ChatGPT}
        C -- AI Response --> D(Intent & Emotion Recognition)
    end

    subgraph "Animation Control"
        D --> E[Animation Selection]
        E --> F(glTF/VRM Animation)
    end

    subgraph "3D Character"
        F --> G["3D Model (glTF/VRM)"] 
        G --> H(Render & Display)
    end

    subgraph "Lip Sync"
        C -- Speech Output --> I(Text-to-Speech)
        I --> J(Phoneme Analysis)
        J --> F
    end

    subgraph "Holographic LED Fan Interaction"
        H --> L[Streaming 3D Frames to Holographic Fan]
        L --> M(Holographic Display)
    end

    M --> K(Visual Feedback to User)
    K --> A
```

---

## **Table of Contents**

1. [Setting Up the Environment](#setting-up-the-environment)
2. [Loading and Customizing a 3D Model](#loading-and-customizing-a-3d-model)
3. [Integrating ChatGPT with the 3D Model](#integrating-chatgpt-with-the-3d-model)
4. [Adding Lip Sync and Animations](#adding-lip-sync-and-animations)
5. [Streaming Real-Time 3D Frames to the LED Fan](#streaming-real-time-3d-frames-to-the-led-fan)
6. [Full Python Code](#full-python-code)
7. [Testing and Debugging](#testing-and-debugging)

---

## **1. Setting Up the Environment**

### Install Required Libraries

```bash
pip install openai pygltflib pillow requests pygame gtts
```

- **`openai`:** For ChatGPT API integration.
- **`pygltflib`:** To load and modify 3D models (glTF/VRM).
- **`Pillow`:** For frame image processing.
- **`requests`:** For sending frames to the LED fan API.
- **`pygame`:** For rendering animations locally.
- **`gtts`:** For generating speech from chatbot responses.

---

## **2. Loading and Customizing a 3D Model**

### Choose a 3D Model
Select a glTF/GLB or VRM model for your chatbot. Use platforms like:
- [**Sketchfab**](https://www.sketchfab.com/)
- [**Mixamo**](https://www.mixamo.com/)

### Python Code: Load and Customize the Model
Load the model using `pygltflib` and apply custom animations.

```python
import pygltflib

# Load a 3D model (glTF format)
model = pygltflib.GLTF2()
model.load_file("character_model.glb")

# Apply a simple customization (e.g., scaling the character)
def customize_model():
    for node in model.nodes:
        if node.name == "Head":  # Customize the head node
            node.scale = [1.2, 1.2, 1.2]  # Scale the head
    model.save("customized_character.glb")
    
customize_model()
```

---

## **3. Integrating ChatGPT with the 3D Model**

### Obtain ChatGPT Responses
Integrate ChatGPT for conversational responses.

```python
import openai

openai.api_key = "your-api-key"

def get_chat_response(user_input):
    """
    Get a response from ChatGPT.
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=user_input,
        max_tokens=150,
        temperature=0.7
    )
    return response.choices[0].text.strip()
```

---

## **4. Adding Lip Sync and Animations**

### Generate Speech and Analyze Phonemes
Use `gTTS` for speech generation and basic phoneme analysis.

```python
from gtts import gTTS
import os

def generate_speech(text):
    """
    Generate speech from text using gTTS.
    """
    tts = gTTS(text)
    tts.save("response.mp3")
    os.system("mpg123 response.mp3")
```

### Apply Lip Sync to the 3D Model
Map phonemes to blend shapes in the glTF/VRM model.

```python
def apply_lip_sync(phoneme):
    for node in model.nodes:
        if node.name == "Mouth":
            if phoneme == "A":
                node.scale = [1.1, 1.1, 1.1]
            elif phoneme == "O":
                node.scale = [1.3, 1.3, 1.3]
    model.save("lip_synced_character.glb")
```

---

## **5. Streaming Real-Time 3D Frames to the LED Fan**

### Generate 3D Frames
Render the 3D chatbot animation dynamically.

```python
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import io

# Initialize 3D plot
fig = plt.figure(figsize=(5, 5))
ax = fig.add_subplot(111, projection='3d')

def generate_frame(text, angle):
    """
    Generate a 3D frame displaying rotating chatbot text.
    """
    ax.clear()
    ax.text(0, 0, 0, text, color="blue", fontsize=15, ha="center", va="center")
    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    ax.set_zlim([-1, 1])
    ax.view_init(elev=20, azim=angle)
    
    fig.canvas.draw()
    frame = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    frame = frame.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    return frame
```

### Stream Frames to the Fan
Send frames to the holographic fan in real time.

```python
import requests
import time

FAN_API_URL = "http://<fan-ip-address>/upload_frame"

def send_frame_to_fan(frame):
    """
    Send a single frame to the LED fan.
    """
    buffer = io.BytesIO()
    image = Image.fromarray(frame)
    image.save(buffer, format="PNG")
    buffer.seek(0)

    response = requests.post(FAN_API_URL, files={'frame': buffer})
    return response.status_code
```

---

## **6. Full Python Code**

Here is the complete integrated script:

```python
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import io
import requests
import openai
from gtts import gTTS
import time

# ChatGPT API key
openai.api_key = "your-api-key"

# Initialize 3D plot
fig = plt.figure(figsize=(5, 5))
ax = fig.add_subplot(111, projection='3d')

# Fan API endpoint
FAN_API_URL = "http://<fan-ip-address>/upload_frame"

# Generate a 3D frame
def generate_frame(text, angle):
    ax.clear()
    ax.text(0, 0, 0, text, color="blue", fontsize=15, ha="center", va="center")
    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    ax.set_zlim([-1, 1])
    ax.view_init(elev=20, azim=angle)
    
    fig.canvas.draw()
    frame = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    frame = frame.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    return frame

# Get ChatGPT response
def get_chat_response(user_input):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=user_input,
        max_tokens=150,
        temperature=0.7
    )
    return response.choices[0].text.strip()

# Generate speech
def generate_speech(text):
    tts = gTTS(text)
    tts.save("response.mp3")
    os.system("mpg123 response.mp3")

# Stream frames to the fan
def send_frame_to_fan(frame):
    buffer = io.BytesIO()
    image = Image.fromarray(frame)
    image.save(buffer, format="PNG")
    buffer.seek(0)

    response = requests.post(FAN_API_URL, files={'frame': buffer})
    return response.status_code

# Main loop
angle = 0
try:
    while True:
        user_input = input("You: ")
        chatbot_response = get_chat_response(user_input)
        generate_speech(chatbot_response)
        
        for _ in range(60):  # Display for 2 seconds
            frame = generate_frame(chatbot_response, angle)
            send_frame_to_fan(frame)
            angle += 6
            time.sleep(0.033)
except KeyboardInterrupt:
    print("Streaming stopped.")
```

---

## **7. Testing and Debugging**

1. **Fan Connectivity**:
   - Test the fan's API using a static image upload.
2. **Streaming Performance**:
   - Optimize frame resolution and transmission speed for smooth animations.
3. **Chatbot Responses**:
   - Validate ChatGPT's responses and ensure they match user input.

---




## **Conclusion**

This comprehensive tutorial shows how to integrate a 3D chatbot with real-time animations and display it on a holographic LED fan. The interactive pipeline connects ChatGPT responses to 3D animations, creating a dynamic and engaging user experience.