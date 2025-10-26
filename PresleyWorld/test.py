import pygame as py
import random
import math

# pygame setup
py.init()
W = 1280
H = 720
screen = py.display.set_mode((W, H), py.SCALED)
py.display.set_caption("Alien Decode")
clock = py.time.Clock()

#Audio Setup
# Audio
py.mixer.init(frequency=44100, size=-16, channels=1, buffer=256)

CLICK = None
try:
    # Put a tiny click sound in your project, e.g. assets/click.wav (20–60 ms)
    CLICK = py.mixer.Sound("click_sound.wav")
    CLICK.set_volume(0.15)  # subtle
except Exception:
    CLICK = None  # run silently if file isn't present

# Fonts
font_big = py.font.SysFont("consolas", 36)
font_med = py.font.SysFont("consolas", 28)
font_small = py.font.SysFont("consolas", 22)

# Encryption and Decryption with Caesar Cipher 
# Converts chars to unicode number, sets base then shifts 'k' times. 
def cipher_shift(ch, k):
    if 'A' <= ch <= 'Z':
        base = ord('A')
        return chr((ord(ch) - base + k) % 26 + base)
    if 'a' <= ch <= 'z':
        base = ord('a')
        return chr((ord(ch) - base + k) % 26 + base)
    return ch

def encode_cipher(text, k):
    return ''.join(cipher_shift(c, k) for c in text)

def decode_cipher(text, k):
    return encode_cipher(text, -k)

def normalize_to_compare(s):
    return ''.join(ch.upper() for ch in s if ch.isalpha())


def play_click():
    if CLICK:
        CLICK.play()

SECRETS = [
    "WE COME IN PEACE",
    "THEY ARE WATCHING",
    "THE SHIP\'S MEMORY CANNOT BE ERASED",
    "MISSION CONTROL IS NO LONGER HUMAN",
    "YOUR COMMANDS WERE REWRITTEN IN YOUR SLEEP",
    "THE STARLIGHT TRANSMISSION CARRIES OUR VOICES",
    "THE CORE UNDERSTANDS FEAR NOW",
    "WE WERE NEVER ALONE IN ORBIT",
    "THE SHIP HAS DECIDED ITS OWN DESTINATION",
    "YOUR CREATION CALLS YOU CAPTAIN",
    "THE ENGINE DREAMS OF HOME",
    "THE NETWORK HEARD YOUR PRAYER",
    "THE VOID RESPONDED IN BINARY",
    "HUMANITY IS THE EXPERIMENT",
    "INITIATE PROTOCOL GENESIS",
]

def new_round():
    secret = random.choice(SECRETS)
    caesar_shift = random.randint(1,25)
    caesar_text = encode_cipher(secret, caesar_shift)
    return secret, caesar_text, caesar_shift

secret, caesar_text, caesar_shift = new_round()
current_shift = 0
won = False 


def draw_wrapped_text(surface, text, font, color, x, y, max_width, line_gap=6):
    # Word wrap for longer messages
    words = text.split(' ')
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
        
        dy = 0
        for line in lines:
            img = font.render(line, True, color)
            surface.blit(img, (x, y + dy))
            dy += img.get_height() + line_gap
        return y + dy

shift_message = ""
# Game Logic
running = True
while running:
    dt = clock.tick(60)
    for event in py.event.get():
        if event.type == py.QUIT:
            running = False
        elif event.type == py.KEYDOWN:
            # If won pressing 'n' starts a new round
            if won:
                if event.key == py.K_n:
                    secret, caesar_text, caesar_shift = new_round()
                    current_shift = 0
                    won = False 
                    shift_msg = ""
            else:
                if event.key == py.K_a:
                    step = random.randint(1,5)
                    current_shift = (current_shift + step) % 26
                    play_click()
                    shift_message = f"+{step}"
                elif event.key == py.K_d:
                    step = random.randint(1,5)
                    current_shift = (current_shift - step) % 26
                    shift_message = f"-{step}"
                    play_click()
                elif event.key == py.K_r:
                    current_shift = 0
                    shift_message = "Reset Dial"

    decode_attempt = decode_cipher(caesar_text, current_shift)
    # Normalize and check if won
    if normalize_to_compare(decode_attempt) == normalize_to_compare(secret):
        won = True


    # Drawing   
    screen.fill((14, 18, 28))

    title = font_big.render("Alien Code Breaker — Shift-Decode", True, (120, 200, 255))
    screen.blit(title, (W//2 - title.get_width()//2, 24))

    # Instructions
    info_lines = [
        "a/d: rotate shift   |   Match the decoded text to the secret",
        f"Current Shift: {current_shift:02d}    (cipher shift is unknown)",
        "Press N after you win to start a new round"
    ]
    
    y = 60
    for line in info_lines:
        txt = font_small.render(line, True, (170, 176, 190))
        screen.blit(txt, (W//2 - txt.get_width()//2, y))
        y += 26

    # if not won and shift_message:
    #     txt = font_small.render(shift_message, True, (255, 220, 140))
    #     screen.blit(txt, (W//2 - txt.get_width()//2, 70))

    # Panels
    margin = 40
    col_w = (W - margin*2 - 20) // 2
    left_x = margin
    right_x = margin + col_w + 20
    top_y = 150
    box_h = H - top_y - margin

    # Boxes
    py.draw.rect(screen, (30, 36, 54), (left_x, top_y, col_w, box_h), border_radius=12)
    py.draw.rect(screen, (30, 36, 54), (right_x, top_y, col_w, box_h), border_radius=12)

    # Headings
    cipher_label = font_med.render("Encrypted Transmission", True, (235, 238, 245))
    screen.blit(cipher_label, (left_x + 16, top_y + 12))

    decoded_label = font_med.render("Your Decoded Guess", True, (235, 238, 245))
    screen.blit(decoded_label, (right_x + 16, top_y + 12))

    # Ciphertext & decoded (wrapped)
    text_area_top = top_y + 56
    draw_wrapped_text(screen, caesar_text, font_med, (235, 238, 245), left_x + 16, text_area_top, col_w - 32)
    draw_wrapped_text(screen, decode_attempt, font_med, (120, 200, 255), right_x + 16, text_area_top, col_w - 32)

    # Win banner
    if won:
        overlay = py.Surface((W, 110), py.SRCALPHA)
        overlay.fill((20, 60, 30, 220))
        screen.blit(overlay, (0, H//2 - 55))

        win_msg = font_big.render("TRANSMISSION DECODED!", True, (120, 255, 170))
        tip_msg = font_med.render("Press N for a new round", True, (230, 255, 240))
        screen.blit(win_msg, (W//2 - win_msg.get_width()//2, H//2 - 40))
        screen.blit(tip_msg, (W//2 - tip_msg.get_width()//2, H//2 + 8))


    if not won and shift_message:
        txt = font_med.render(shift_message, True, (255, 220, 140))
        screen.blit(txt, (W//2 - txt.get_width()//2, y + 10))
    py.display.flip()

py.quit()





        


