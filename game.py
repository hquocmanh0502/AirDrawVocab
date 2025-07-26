import cv2
import random
from collections import deque
import mediapipe as mp
import numpy as np
import tensorflow as tf
import pygame
from pygame.locals import *
import os
import json
import pyttsx3
import threading  # Thêm cho TTS không freeze

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# Load model
model = tf.keras.models.load_model("models/quickdraw_model.h5")
with open('class_names.txt', 'r') as f:
    CLASSES = f.read().splitlines()

# Cài đặt game
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
FPS = 60
INITIAL_TIME = 60
TIME_DECREASE_PER_LEVEL = 3
MAX_LEVELS = 15
LIVES = 3
STREAK_BONUS = 2
WORD_LIST = CLASSES

# Màu sắc
BG_COLOR = (25, 30, 45)
PRIMARY_COLOR = (100, 200, 255)
SECONDARY_COLOR = (255, 150, 100)
ACCENT_COLOR = (255, 80, 220)
TEXT_COLOR = (240, 240, 240)
SUCCESS_COLOR = (100, 255, 150)
ERROR_COLOR = (255, 100, 100)
DRAWING_COLOR = (100, 255, 255)
PARTICLE_COLORS = [
    (255, 200, 100), (100, 255, 200), 
    (200, 100, 255), (255, 255, 100),
    (100, 255, 255), (255, 100, 255)
]

# Bố cục
INFO_HEIGHT = 120
INFO_RECT = pygame.Rect(0, 0, SCREEN_WIDTH, INFO_HEIGHT)
CAMERA_RECT = pygame.Rect(0, INFO_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT - INFO_HEIGHT)
CAMERA_WIDTH, CAMERA_HEIGHT = CAMERA_RECT.width, CAMERA_RECT.height

# Dịch nghĩa và phiên âm
translation_dict = {
    "bowtie": "nơ bướm",
    "diamond": "kim cương",
    "baseball": "bóng chày",
    "moon": "mặt trăng",
    "t-shirt": "áo phông",
    "star": "ngôi sao",
    "scissors": "kéo",
    "pants": "quần dài",
    "leaf": "lá",
    "lightning": "tia chớp",
    "hat": "mũ",
    "fish": "cá",
    "envelope": "phong bì",
    "eye": "mắt",
    "door": "cửa",
    "cup": "cái cốc",
    "book": "quyển sách",
    "apple": "trái táo"
}

pron_dict = {
    "bowtie": "/ˈboʊ.taɪ/",
    "diamond": "/ˈdaɪ.mənd/",
    "baseball": "/ˈbeɪs.bɔːl/",
    "moon": "/muːn/",
    "t-shirt": "/ˈtiːˌʃɜːrt/",
    "star": "/stɑːr/",
    "scissors": "/ˈsɪz.ərz/",
    "pants": "/pænts/",
    "leaf": "/liːf/",
    "lightning": "/ˈlaɪt.nɪŋ/",
    "hat": "/hæt/",
    "fish": "/fɪʃ/",
    "envelope": "/ˈen.və.loʊp/",
    "eye": "/aɪ/",
    "door": "/dɔːr/",
    "cup": "/kʌp/",
    "book": "/bʊk/",
    "apple": "/ˈæp.əl/"
}

LEVEL_WORDS = {
    1: ["apple", "cup", "door", "eye", "fish", "hat", "moon", "star"],
    2: ["book", "leaf", "pants", "t-shirt"],
    3: ["baseball", "scissors"],
    4: ["bowtie", "diamond", "envelope"],
    5: ["lightning"],
    6: ["apple", "cup", "door", "eye", "fish", "hat", "moon", "star"],
    7: ["book", "leaf", "pants", "t-shirt"],
    8: ["baseball", "scissors"],
    9: ["bowtie", "diamond", "envelope"],
    10: ["lightning"],
    11: ["apple", "cup", "door", "eye", "fish", "hapkt", "moon", "star"],
    12: ["book", "leaf", "pants", "t-shirt"],
    13: ["baseball", "scissors"],
    14: ["bowtie", "diamond", "envelope"],
    15: CLASSES
}

class Button:
    def __init__(self, x, y, width, height, text, **kwargs):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = kwargs.get('color', PRIMARY_COLOR)
        self.hover_color = kwargs.get('hover_color', (150, 230, 255))
        self.text_color = kwargs.get('text_color', TEXT_COLOR)
        self.border_radius = kwargs.get('border_radius', 12)
        self.font_size = kwargs.get('font_size', 32)
        self.font = pygame.font.SysFont("Arial", self.font_size, bold=True)
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        shadow_rect = self.rect.move(5, 5)
        pygame.draw.rect(surface, (0, 0, 0, 100), shadow_rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click

class Particle:
    def __init__(self, x, y, color=None):
        self.x = x
        self.y = y
        self.size = random.randint(3, 8)
        self.color = color or random.choice(PARTICLE_COLORS)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-8, -2)
        self.life = random.randint(30, 60)
        self.gravity = 0.2
        self.fade = random.uniform(2, 4)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= self.fade
        self.size = max(0, self.size - 0.05)
        
    def draw(self, surface):
        s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
        alpha = min(255, int(self.life * 4.25))
        pygame.draw.circle(s, self.color, (self.size, self.size), self.size)
        s.set_alpha(alpha)
        surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class DrawingGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Draw & Learn English")
        self.clock = pygame.time.Clock()
        
        # Fonts (Times New Roman cho IPA)
        self.title_font = pygame.font.SysFont("Times New Roman", 64, bold=True)
        self.header_font = pygame.font.SysFont("Times New Roman", 48, bold=True)
        self.main_font = pygame.font.SysFont("Arial", 36)
        self.small_font = pygame.font.SysFont("Arial", 24)
        self.ipa_font = pygame.font.SysFont("Times New Roman", 36)  # Font riêng cho IPA
        
        self.cap = cv2.VideoCapture(0)
        self.points = deque(maxlen=512)
        self.canvas = np.zeros((CAMERA_HEIGHT, CAMERA_WIDTH, 3), dtype=np.uint8)
        self.is_drawing = False
        self.is_shown = False
        self.predicted_class = None
        
        self.score = 0
        self.high_score = self.load_high_score()
        self.lives = LIVES
        self.level = 1
        self.level_progress = 0
        self.streak = 0
        self.time_limit = INITIAL_TIME
        self.current_word = random.choice(LEVEL_WORDS[1])
        self.time_left = self.time_limit
        self.game_active = False
        self.game_over = False
        self.particles = []
        self.show_word_info = False
        self.level_up_timer = 0
        self.hint_given = False
        self.shake_timer = 0
        self.success_icon_timer = 0
        
        self.hands = mp_hands.Hands(
            max_num_hands=1,
            model_complexity=0,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        voices = self.tts_engine.getProperty('voices')
        for voice in voices:
            if 'english' in voice.name.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break
        
        self.state = "menu"
        self.create_ui_elements()
        self.load_sounds()
        
        self.word_data = {
            word: {
                "pron": pron_dict.get(word, ""),
                "translation": translation_dict.get(word, ""),
                "example": self.generate_example(word)
            } 
            for word in WORD_LIST
        }
        
    def generate_example(self, word):
        examples = {
            "apple": "I eat an apple every day.",
            "book": "This book is very interesting.",
            "fish": "The fish is swimming in the water.",
            "moon": "The moon is bright tonight.",
            "star": "I can see many stars in the sky.",
            "hat": "She is wearing a beautiful hat.",
            "scissors": "Use scissors to cut the paper.",
            "cup": "Can I have a cup of coffee?",
            "bowtie": "He wears a bowtie to the party.",
            "diamond": "The diamond ring is shiny.",
            "baseball": "We play baseball on weekends.",
            "t-shirt": "I wear a t-shirt in summer.",
            "pants": "These pants are comfortable.",
            "leaf": "The leaf fell from the tree.",
            "lightning": "Lightning flashed in the sky.",
            "envelope": "I sent a letter in an envelope.",
            "eye": "She has beautiful eyes.",
            "door": "Please close the door."
        }
        return examples.get(word, f"This is a {word}.")
        
    def create_ui_elements(self):
        self.start_button = Button(
            SCREEN_WIDTH//2 - 150, 200, 300, 70, "Start Game", color=PRIMARY_COLOR)
        self.instructions_button = Button(
            SCREEN_WIDTH//2 - 150, 300, 300, 70, "How to Play", color=SECONDARY_COLOR)
        self.exit_button = Button(
            SCREEN_WIDTH//2 - 150, 400, 300, 70, "Exit", color=ERROR_COLOR)
        self.menu_button = Button(
            20, SCREEN_HEIGHT - 70, 120, 50, "Menu", font_size=24)
        self.clear_button = Button(
            SCREEN_WIDTH - 140, SCREEN_HEIGHT - 70, 120, 50, "Clear", font_size=24)
        self.speaker_button = Button(
            SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT - 100, 60, 60, "🔊", font_size=32)
        self.continue_button = Button(
            SCREEN_WIDTH//2 + 40, SCREEN_HEIGHT - 100, 200, 60, "Continue", font_size=32)
        self.back_button = Button(
            SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 80, 200, 50, "Back to Menu", font_size=28)
        
    def load_sounds(self):
        self.correct_sound = pygame.mixer.Sound("sounds/correct.wav") if os.path.exists("sounds/correct.wav") else None
        self.wrong_sound = pygame.mixer.Sound("sounds/wrong.wav") if os.path.exists("sounds/wrong.wav") else None
        self.level_up_sound = pygame.mixer.Sound("sounds/level_up.wav") if os.path.exists("sounds/level_up.wav") else None
        if os.path.exists("sounds/bg_music.mp3"):
            pygame.mixer.music.load("sounds/bg_music.mp3")
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
        
    def load_high_score(self):
        try:
            if os.path.exists("highscore.json"):
                with open("highscore.json", "r") as f:
                    return json.load(f).get("high_score", 0)
        except:
            return 0
        
    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            with open("highscore.json", "w") as f:
                json.dump({"high_score": self.high_score}, f)
                
    def create_particles(self, x, y, count=50):
        for _ in range(count):
            self.particles.append(Particle(x, y))
            
    def reset_game(self):
        self.score = 0
        self.lives = LIVES
        self.level = 1
        self.level_progress = 0
        self.streak = 0
        self.time_limit = INITIAL_TIME
        self.current_word = random.choice(LEVEL_WORDS[1])
        self.time_left = self.time_limit
        self.game_active = True
        self.game_over = False
        self.points.clear()
        self.canvas.fill(0)
        self.particles = []
        self.show_word_info = False
        self.hint_given = False
        self.shake_timer = 0
        self.success_icon_timer = 0
        
    def speak(self, text):
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
        
    def process_frame(self):
        if not self.game_active or self.show_word_info:
            return None
        if not self.hint_given and self.level <= 5:
            hint = f"Hint: {self.current_word} means {self.word_data[self.current_word]['translation']}"
            threading.Thread(target=self.speak, args=(hint,)).start()
            self.hint_given = True
        success, image = self.cap.read()
        if not success:
            return None
        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                if (hand_landmarks.landmark[8].y < hand_landmarks.landmark[7].y and
                    hand_landmarks.landmark[12].y < hand_landmarks.landmark[11].y and
                    hand_landmarks.landmark[16].y < hand_landmarks.landmark[15].y):
                    if len(self.points) > 10:
                        self.recognize_drawing()
                else:
                    self.is_drawing = True
                    pt = (int(hand_landmarks.landmark[8].x * CAMERA_WIDTH),
                          int(hand_landmarks.landmark[8].y * CAMERA_HEIGHT))
                    self.points.append(pt)
                    for i in range(1, len(self.points)):
                        cv2.line(self.canvas, self.points[i-1], self.points[i], (255, 255, 255), 5)
        
        return image_rgb
        
    def recognize_drawing(self):
        self.is_drawing = False
        canvas_gs = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        canvas_gs = cv2.medianBlur(canvas_gs, 9)
        canvas_gs = cv2.GaussianBlur(canvas_gs, (5, 5), 0)
        ys, xs = np.nonzero(canvas_gs)
        if len(ys) == 0 or len(xs) == 0:
            return
        min_y, max_y = np.min(ys), np.max(ys)
        min_x, max_x = np.min(xs), np.max(xs)
        cropped = canvas_gs[min_y:max_y+1, min_x:max_x+1]
        cropped = cv2.resize(cropped, (28, 28))
        cropped = cropped.reshape(1, 28, 28, 1).astype('float32') / 255.0
        predictions = model.predict(cropped)
        self.predicted_class = np.argmax(predictions[0])
        predicted_word = CLASSES[self.predicted_class]
        
        if predicted_word == self.current_word:
            self.handle_correct_guess()
        else:
            self.handle_wrong_guess()
            
        self.points.clear()
        self.canvas.fill(0)
        
    def handle_correct_guess(self):
        self.streak += 1
        bonus = max(0, int(self.time_left / 10)) + (STREAK_BONUS if self.streak >= 3 else 0)
        self.score += 1 + bonus
        self.level_progress += 1
        if self.correct_sound:
            self.correct_sound.play()
        self.create_particles(SCREEN_WIDTH//2, CAMERA_RECT.centery, 100)
        threading.Thread(target=self.speak, args=(self.current_word,)).start()
        if self.level_progress >= 5:
            self.level = min(self.level + 1, MAX_LEVELS)
            self.level_progress = 0
            self.time_limit = max(15, self.time_limit - TIME_DECREASE_PER_LEVEL)
            self.level_up_timer = FPS * 3
            if self.level_up_sound:
                self.level_up_sound.play()
            self.create_particles(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, 200)
        self.show_word_info = True
        self.success_icon_timer = FPS * 2
        self.time_left = self.time_limit
        self.hint_given = False
        
    def handle_wrong_guess(self):
        self.streak = 0
        self.lives -= 1
        self.shake_timer = FPS // 2
        if self.wrong_sound:
            self.wrong_sound.play()
        if self.lives <= 0:
            self.game_over = True
            self.game_active = False
            self.save_high_score()
            
    def draw_menu(self):
        for y in range(SCREEN_HEIGHT):
            color = (BG_COLOR[0] + y//30, BG_COLOR[1] + y//20, BG_COLOR[2] + y//10)
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        title = self.title_font.render("Draw & Learn English", True, ACCENT_COLOR)
        shadow = self.title_font.render("Draw & Learn English", True, (0, 0, 0))
        self.screen.blit(shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 3, 53))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        high_text = self.main_font.render(f"Best Score: {self.high_score}", True, TEXT_COLOR)
        self.screen.blit(high_text, (SCREEN_WIDTH//2 - high_text.get_width()//2, 130))
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        self.start_button.update(mouse_pos)
        self.instructions_button.update(mouse_pos)
        self.exit_button.update(mouse_pos)
        self.start_button.draw(self.screen)
        self.instructions_button.draw(self.screen)
        self.exit_button.draw(self.screen)
        
        footer = self.small_font.render("Use your hand to draw in the air!", True, (200, 200, 200))
        self.screen.blit(footer, (SCREEN_WIDTH//2 - footer.get_width()//2, SCREEN_HEIGHT - 50))
        
        if mouse_click:
            if self.start_button.is_clicked(mouse_pos, mouse_click):
                self.state = "game"
                self.reset_game()
            elif self.instructions_button.is_clicked(mouse_pos, mouse_click):
                self.state = "instructions"
            elif self.exit_button.is_clicked(mouse_pos, mouse_click):
                return False
        return True
        
    def draw_instructions(self):
        self.screen.fill(BG_COLOR)
        title = self.header_font.render("How to Play", True, ACCENT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        instructions = [
            "1. Draw the English word shown at the top",
            "2. Use your hand in the air to draw:",
            "   - Open hand: Draw",
            "   - Close fingers: Submit drawing",
            "3. Correct guesses earn points + bonuses",
            "4. Wrong guesses lose lives",
            "5. Level up every 5 correct answers",
            "6. Time decreases as you level up",
            "7. Get hints for early levels",
            "8. Streak of 3+ correct gives bonus!"
        ]
        y_pos = 150
        for line in instructions:
            text = self.main_font.render(line, True, TEXT_COLOR)
            self.screen.blit(text, (50, y_pos))
            y_pos += 40
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        self.back_button.update(mouse_pos)
        self.back_button.draw(self.screen)
        if mouse_click and self.back_button.is_clicked(mouse_pos, mouse_click):
            self.state = "menu"
        return True
        
    def draw_game(self, frame_surf):
        self.screen.fill(BG_COLOR)
        pygame.draw.rect(self.screen, (30, 50, 80), INFO_RECT)
        pygame.draw.line(self.screen, PRIMARY_COLOR, (0, INFO_HEIGHT), (SCREEN_WIDTH, INFO_HEIGHT), 3)
        
        # Hiệu ứng rung khi sai
        shake_offset = (random.randint(-5, 5), random.randint(-5, 5)) if self.shake_timer > 0 else (0, 0)
        self.shake_timer = max(0, self.shake_timer - 1)
        
        word_text = self.main_font.render(f"Draw: {self.current_word}", True, ACCENT_COLOR)
        self.screen.blit(word_text, (30 + shake_offset[0], 20 + shake_offset[1]))
        score_text = self.main_font.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (30 + shake_offset[0], 60 + shake_offset[1]))
        time_text = self.main_font.render(f"Time: {int(self.time_left)}", True, TEXT_COLOR)
        self.screen.blit(time_text, (SCREEN_WIDTH//2 - time_text.get_width()//2 + shake_offset[0], 20 + shake_offset[1]))
        level_text = self.main_font.render(f"Level: {self.level}/{MAX_LEVELS}", True, TEXT_COLOR)
        self.screen.blit(level_text, (SCREEN_WIDTH//2 - level_text.get_width()//2 + shake_offset[0], 60 + shake_offset[1]))
        lives_text = self.main_font.render(f"Lives: {'❤️' * self.lives}", True, ERROR_COLOR if self.lives == 1 else TEXT_COLOR)
        self.screen.blit(lives_text, (SCREEN_WIDTH - 150 + shake_offset[0], 20 + shake_offset[1]))
        streak_text = self.main_font.render(f"Streak: {self.streak}", True, SUCCESS_COLOR if self.streak >= 3 else TEXT_COLOR)
        self.screen.blit(streak_text, (SCREEN_WIDTH - 150 + shake_offset[0], 60 + shake_offset[1]))
        
        # Progress bar
        progress_bar_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 80, 200, 10)
        pygame.draw.rect(self.screen, (100, 100, 100), progress_bar_rect)
        fill_width = (self.level_progress / 5) * 200
        pygame.draw.rect(self.screen, SUCCESS_COLOR, (progress_bar_rect.x, progress_bar_rect.y, fill_width, 10))
        
        if frame_surf:
            cam_surf = pygame.transform.scale(frame_surf, (CAMERA_WIDTH, CAMERA_HEIGHT))
            self.screen.blit(cam_surf, (CAMERA_RECT.topleft[0] + shake_offset[0], CAMERA_RECT.topleft[1] + shake_offset[1]))
        for i in range(1, len(self.points)):
            pt1 = (self.points[i-1][0] + CAMERA_RECT.x + shake_offset[0], self.points[i-1][1] + CAMERA_RECT.y + shake_offset[1])
            pt2 = (self.points[i][0] + CAMERA_RECT.x + shake_offset[0], self.points[i][1] + CAMERA_RECT.y + shake_offset[1])
            pygame.draw.line(self.screen, DRAWING_COLOR, pt1, pt2, 4)
        
        for particle in self.particles[:]:
            particle.update()
            particle.draw(self.screen)
            if particle.life <= 0:
                self.particles.remove(particle)
                
        if self.level_up_timer > 0:
            blink = self.level_up_timer % 10 < 5
            if blink:
                level_up_text = self.header_font.render(f"Level Up! Now Level {self.level}", True, SUCCESS_COLOR)
                self.screen.blit(level_up_text, (SCREEN_WIDTH//2 - level_up_text.get_width()//2, SCREEN_HEIGHT//2))
            self.level_up_timer -= 1
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        self.menu_button.update(mouse_pos)
        self.clear_button.update(mouse_pos)
        self.menu_button.draw(self.screen)
        self.clear_button.draw(self.screen)
        
        if mouse_click:
            if self.menu_button.is_clicked(mouse_pos, mouse_click):
                self.state = "menu"
                self.save_high_score()
            elif self.clear_button.is_clicked(mouse_pos, mouse_click):
                self.points.clear()
                self.canvas.fill(0)
                
        if self.show_word_info:
            self.draw_word_info()
        if self.game_over:
            self.draw_game_over()
        
        # Vẽ icon success overlay
        if self.success_icon_timer > 0:
            alpha = min(255, self.success_icon_timer * 8)  # Fade in/out
            surface = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(surface, SUCCESS_COLOR, (50, 50), 50)
            pygame.draw.line(surface, TEXT_COLOR, (30, 50), (45, 65), 10)
            pygame.draw.line(surface, TEXT_COLOR, (45, 65), (70, 35), 10)
            surface.set_alpha(alpha)
            self.screen.blit(surface, (SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2 - 50))
            self.success_icon_timer -= 1
            
        return True
        
    def draw_word_info(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        info_box = pygame.Rect(SCREEN_WIDTH//4, INFO_HEIGHT + 50, SCREEN_WIDTH//2, SCREEN_HEIGHT - INFO_HEIGHT - 200)
        pygame.draw.rect(self.screen, (40, 70, 120), info_box, border_radius=15)
        pygame.draw.rect(self.screen, PRIMARY_COLOR, info_box, 3, border_radius=15)
        
        word = self.current_word
        data = self.word_data[word]
        word_text = self.main_font.render(word, True, ACCENT_COLOR)
        pron_text = self.ipa_font.render(data['pron'], True, ACCENT_COLOR)
        trans_text = self.main_font.render(data['translation'], True, TEXT_COLOR)
        example_text = self.small_font.render(data['example'], True, (200, 200, 255))
        
        word_x = SCREEN_WIDTH//2 - (word_text.get_width() + pron_text.get_width() + 10)//2
        self.screen.blit(word_text, (word_x, info_box.y + 30))
        self.screen.blit(pron_text, (word_x + word_text.get_width() + 10, info_box.y + 30))
        self.screen.blit(trans_text, (SCREEN_WIDTH//2 - trans_text.get_width()//2, info_box.y + 90))
        self.screen.blit(example_text, (SCREEN_WIDTH//2 - example_text.get_width()//2, info_box.y + 140))
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        self.speaker_button.update(mouse_pos)
        self.continue_button.update(mouse_pos)
        self.speaker_button.draw(self.screen)
        self.continue_button.draw(self.screen)
        
        if mouse_click:
            if self.speaker_button.is_clicked(mouse_pos, mouse_click):
                threading.Thread(target=self.speak, args=(self.current_word,)).start()
            elif self.continue_button.is_clicked(mouse_pos, mouse_click):
                self.show_word_info = False
                self.current_word = random.choice(LEVEL_WORDS[self.level])
                self.time_left = self.time_limit
                self.hint_given = False
                
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        game_over_box = pygame.Rect(SCREEN_WIDTH//4, SCREEN_HEIGHT//3, SCREEN_WIDTH//2, SCREEN_HEIGHT//3)
        pygame.draw.rect(self.screen, (80, 30, 30), game_over_box, border_radius=15)
        pygame.draw.rect(self.screen, ERROR_COLOR, game_over_box, 3, border_radius=15)
        
        game_over_text = self.header_font.render("Game Over", True, ERROR_COLOR)
        self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//3 + 30))
        score_text = self.main_font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//3 + 100))
        high_score_text = self.main_font.render(f"Best Score: {self.high_score}", True, TEXT_COLOR)
        self.screen.blit(high_score_text, (SCREEN_WIDTH//2 - high_score_text.get_width()//2, SCREEN_HEIGHT//3 + 150))
        
        badge_y = SCREEN_HEIGHT//3 + 190
        scale = 1 + 0.1 * abs((pygame.time.get_ticks() % 1000 - 500) / 500)
        if self.level >= 5:
            badge_text = self.main_font.render("Sketch Novice!", True, SUCCESS_COLOR)
            scaled_text = pygame.transform.scale(badge_text, (int(badge_text.get_width() * scale), int(badge_text.get_height() * scale)))
            self.screen.blit(scaled_text, (SCREEN_WIDTH//2 - scaled_text.get_width()//2, badge_y))
            badge_y += 40
        if self.level >= 10:
            badge_text = self.main_font.render("Draw Master!", True, SUCCESS_COLOR)
            scaled_text = pygame.transform.scale(badge_text, (int(badge_text.get_width() * scale), int(badge_text.get_height() * scale)))
            self.screen.blit(scaled_text, (SCREEN_WIDTH//2 - scaled_text.get_width()//2, badge_y))
            badge_y += 40
        if self.level >= 15:
            badge_text = self.main_font.render("English Draw Legend!", True, SUCCESS_COLOR)
            scaled_text = pygame.transform.scale(badge_text, (int(badge_text.get_width() * scale), int(badge_text.get_height() * scale)))
            self.screen.blit(scaled_text, (SCREEN_WIDTH//2 - scaled_text.get_width()//2, badge_y))
        
        menu_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//3 + 310, 200, 50, "Menu", color=PRIMARY_COLOR)
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        menu_button.update(mouse_pos)
        menu_button.draw(self.screen)
        
        if mouse_click and menu_button.is_clicked(mouse_pos, mouse_click):
            self.state = "menu"
            
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        if self.state == "game":
                            self.state = "menu"
                            self.save_high_score()
                        else:
                            running = False
            
            frame = self.process_frame()
            frame_surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1)) if frame is not None else None
            
            if self.state == "game" and self.game_active and not self.game_over:
                self.time_left -= 1 / FPS
                if self.time_left <= 0:
                    self.lives -= 1
                    self.shake_timer = FPS // 2
                    self.time_left = self.time_limit
                    if self.lives <= 0:
                        self.game_over = True
                        self.game_active = False
                        self.save_high_score()
            
            if self.state == "menu":
                running = self.draw_menu()
            elif self.state == "instructions":
                running = self.draw_instructions()
            elif self.state == "game":
                running = self.draw_game(frame_surf)
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        self.cleanup()
        
    def cleanup(self):
        self.cap.release()
        self.hands.close()
        try:
            self.tts_engine.stop()
            self.tts_engine.endLoop()
        except:
            pass
        pygame.quit()

if __name__ == "__main__":
    game = DrawingGame()
    game.run()