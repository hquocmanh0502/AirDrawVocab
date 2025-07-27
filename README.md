# ✨ AirDrawVocab

**AirDrawVocab** is an innovative hand-gesture drawing game powered by AI that makes learning English vocabulary fun and interactive. Using **MediaPipe** for real-time hand tracking, **TensorFlow** for image recognition, and **Pygame** for a friendly interface, users draw English words like “apple” or “lightning” in the air. The AI predicts the drawing, shows translations and IPA, and rewards users with levels, hints, and achievement badges like “Sketch Novice” or “Draw Master”.

---

## 👨‍💻 Developed by

**hquocmanh0502**  
📜 License: MIT License *(Open for contributions!)*

---

## 🛠 Tech Stack

- Python 3.12+
- MediaPipe
- TensorFlow
- Pygame
- OpenCV
- pyttsx3 (text-to-speech)

---

## 🎮 Features

- ✍️ Draw in the air using your hand and webcam.
- 🤖 AI recognition of 19 English vocabulary words.
- 📈 Level-up system (15 levels with decreasing time).
- 🔉 Pronunciation with text-to-speech (TTS).
- 🎯 Streak bonus & achievements (badges).
- 🇻🇳 Vietnamese translation and usage examples.
- 🎨 Simple, interactive UI with sound effects.

---

## 📦 Installation

### ✅ Prerequisites

- Python 3.12 or higher
- Webcam

### 📥 Clone the repository

```bash
git clone https://github.com/hquocmanh0502/AirDrawVocab.git
cd AirDrawVocab
```

### 📦 Install dependencies

```bash
pip install opencv-python mediapipe tensorflow pygame pyttsx3
```

### 📁 Add model files

Ensure the following files exist in a `models/` folder:

- `quickdraw_model.h5`
- `class_names.txt`

You can download these from the training notebook or train your own using the provided Jupyter notebook.

### 🔊 (Optional) Add sound files

Place these in a `sounds/` folder:

- `correct.wav`
- `wrong.wav`
- `level_up.wav`
- `bg_music.mp3`

If you skip this step, comment out related lines in `game.py`.

---

## ▶️ Usage

Run the game:

```bash
python game.py
```

### 🎮 How to play

- **Draw:** Use your index finger (hand open).
- **Submit:** Open all 5 fingers to confirm your drawing.
- **Clear screen:** Click the “Clear” button.
- **Exit game:** Click the “Menu” button.
- **Listen to pronunciation:** Click the speaker icon 🔊.

---

## 🧠 AI Model Training

### Dataset

- Google’s QuickDraw Dataset
- 19 classes, 800 samples/class
- Preprocessed to 28x28 grayscale images

### Model Architecture

- CNN (Conv2D → MaxPooling → Dropout → Dense)
- Trained for 10 epochs on GPU (Colab)
- Accuracy: ~85–90%

### Metrics

- Accuracy: 85–90%
- Precision/Recall/F1: ~0.85–0.90
- Good prediction confidence (e.g., "apple" → 90%)

---

## 🚀 Roadmap

- 🔡 Add more vocabulary by topic
- 🧑‍🤝‍🧑 Multiplayer mode
- 📱 Deploy to Android/iOS
- ⚡ Optimize for faster inference
- 🧾 User stats & tracking

---

## 🤝 Contributing

Contributions are welcome!

```bash
# Fork the repo
git checkout -b feature-name
git commit -m "Add feature"
git push origin feature-name
```

Then create a Pull Request.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Google – for the QuickDraw Dataset
- Open source communities behind MediaPipe, TensorFlow, Pygame, pyttsx3
- Educational AI inspiration projects

---

> ✨ AirDrawVocab makes learning English vocabulary a hands-on, tech-powered adventure!
