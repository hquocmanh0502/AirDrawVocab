import cv2
from collections import deque
import mediapipe as mp
import numpy as np
from src.utils import get_images, get_overlay
from src.config import *
import tensorflow as tf  # Thay thế torch bằng tensorflow

# Khởi tạo MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# Load TensorFlow model thay vì PyTorch
model = tf.keras.models.load_model("models/quickdraw_model.h5")  # Đường dẫn đến model của bạn
with open('class_names.txt', 'r') as f:  # Load class names của bạn
    CLASSES = f.read().split('\n')

predicted_class = None

cap = cv2.VideoCapture(0)
points = deque(maxlen=512)
canvas = np.zeros((480, 640, 3), dtype=np.uint8)
is_drawing = False
is_shown = False
class_images = get_images("images", CLASSES)  # Đảm bảo thư mục images chứa ảnh đại diện cho các class của bạn

with mp_hands.Hands(
        max_num_hands=1,
        model_complexity=0,
        min_detection_confidence=0.5,  # Sửa lỗi chính tả: detection -> detection
        min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        success, image = cap.read()
        image = cv2.flip(image, 1)
        if not success:
            continue

        # Xử lý ảnh
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Kiểm tra gesture (ngón trỏ và các ngón khác)
                if (hand_landmarks.landmark[8].y < hand_landmarks.landmark[7].y and 
                    hand_landmarks.landmark[12].y < hand_landmarks.landmark[11].y and 
                    hand_landmarks.landmark[16].y < hand_landmarks.landmark[15].y):
                    
                    if len(points):
                        is_drawing = False
                        is_shown = True
                        
                        # Tiền xử lý ảnh để phù hợp với model TensorFlow
                        canvas_gs = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
                        canvas_gs = cv2.medianBlur(canvas_gs, 9)
                        canvas_gs = cv2.GaussianBlur(canvas_gs, (5, 5), 0)
                        
                        ys, xs = np.nonzero(canvas_gs)
                        if len(ys) and len(xs):
                            min_y = np.min(ys)
                            max_y = np.max(ys)
                            min_x = np.min(xs)
                            max_x = np.max(xs)
                            
                            cropped_image = canvas_gs[min_y:max_y, min_x:max_x]
                            cropped_image = cv2.resize(cropped_image, (28, 28))
                            
                            # Chuẩn bị input cho TensorFlow model
                            cropped_image = cropped_image.reshape(1, 28, 28, 1).astype('float32') / 255.0
                            
                            # Dự đoán
                            predictions = model.predict(cropped_image)
                            predicted_class = np.argmax(predictions[0])
                            
                            points = deque(maxlen=512)
                            canvas = np.zeros((480, 640, 3), dtype=np.uint8)
                else:
                    is_drawing = True
                    is_shown = False
                    points.append((int(hand_landmarks.landmark[8].x*640), 
                                 int(hand_landmarks.landmark[8].y*480)))
                    
                    # Vẽ các điểm
                    for i in range(1, len(points)):
                        cv2.line(image, points[i - 1], points[i], (0, 255, 0), 2)
                        cv2.line(canvas, points[i - 1], points[i], (255, 255, 255), 5)
                
                # Vẽ landmarks
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
                
                # Hiển thị kết quả
                if not is_drawing and is_shown:
                    # Hiển thị kết quả dạng text thay vì ảnh
                    cv2.putText(image, f'Recognized: {CLASSES[predicted_class]}', 
                            (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                            1, GREEN_RGB, 2, cv2.LINE_AA)
                    
                    # Hiển thị thêm tên class lớn hơn
                    cv2.putText(image, CLASSES[predicted_class], 
                            (490, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                            1, YELLOW_RGB, 2, cv2.LINE_AA)

        cv2.imshow('QuickDraw Recognition', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()