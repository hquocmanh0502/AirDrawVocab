AirDrawVocab
About
AirDrawVocab is an innovative hand-gesture drawing game powered by AI to learn English vocabulary in a fun way. Using MediaPipe for hand tracking, TensorFlow for image recognition, and Pygame for an interactive interface, players draw words like "apple" or "lightning" in the air. The AI predicts the drawing, provides Vietnamese translations, IPA pronunciations, and examples, with features like level-ups, hints, and achievement badges (e.g., "Sketch Novice", "Draw Master"). This project combines education and technology, making English learning enjoyable!

Developed by: hquocmanh0502
License: MIT License (open for contributions!)
Tech Stack: Python, MediaPipe, TensorFlow, Pygame, pyttsx3
Features
Real-time hand drawing with a webcam.
AI-powered recognition of 19 vocabulary words.
Level system (up to 15 levels) with decreasing time limits.
Text-to-speech (TTS) hints and pronunciation.
Streak bonuses and achievement badges.
User-friendly UI with success animations.
Installation
Prerequisites
Python 3.12 or higher
Webcam (for hand tracking)
Steps
Clone the repository:
bash

Thu gọn

Bọc lại

Chạy

Sao chép
git clone https://github.com/hquocmanh0502/AirDrawVocab.git
cd AirDrawVocab
Install required libraries:
bash

Thu gọn

Bọc lại

Chạy

Sao chép
pip install opencv-python mediapipe tensorflow pygame pyttsx3
Ensure the trained model and class names are in the models directory:
Download quickdraw_model.h5 and class_names.txt from the training notebook or train using the provided notebook.
Place them in a models folder.
(Optional) Add sound files:
Place correct.wav, wrong.wav, level_up.wav, and bg_music.mp3 in the sounds folder (or comment out sound-related code if not used).
Usage
Run the game:
bash

Thu gọn

Bọc lại

Chạy

Sao chép
python game.py
Use your hand to draw:
Draw: Point with your index finger (open palm).
Submit: Raise all five fingers (open hand fully).
The game displays the camera feed, your drawing, and recognizes the word.
Interact:
Earn points for correct guesses, level up every 5 correct answers.
Use the "Clear" button to reset, "Menu" to exit, and speaker icon to hear pronunciation.
Training the Model
The model is trained using a Jupyter Notebook (included in the repo or available on Colab).
Dataset: QuickDraw Dataset (19 classes, 800 samples/class).
Architecture: CNN with Conv2D, MaxPooling, Dense layers.
Training: 10 epochs on GPU T4, accuracy ~85-90% (with efforts to reduce overfitting via Dropout and Early Stopping).
Results
Accuracy: ~85-90% on test set.
Precision, Recall, F1-Score: Calculated in the notebook (e.g., ~0.85-0.90 weighted average).
MAE/MSE: Minor metrics for probability deviation.
Minh chứng: Predicts sample images with high probability (e.g., "apple" with 0.9 confidence).
Future Improvements
Add more vocabulary words.
Implement multiplayer mode for online drawing challenges.
Deploy to mobile (Android/iOS) platforms.
Optimize model for faster inference.
Contributing
Fork the repository.
Create a new branch: git checkout -b feature-name.
Commit changes: git commit -m "Add feature-name".
Push to the branch: git push origin feature-name.
Submit a pull request.
License
This project is licensed under the MIT License - see the LICENSE file for details.

Acknowledgments
Google for the QuickDraw Dataset.
MediaPipe, TensorFlow, Pygame, and pyttsx3 communities.
Inspiration from educational AI projects.
