from gc import freeze
import pygame
import math
import random
import sys

class Node:
    def __init__(self, x, y, xSpeed, ySpeed):
        self.x = x
        self.y = y
        self.xSpeed = xSpeed
        self.ySpeed = ySpeed
        self.next = None

class LinkedListStack:
    def __init__(self):
        self.top = None
        self.size = 0

    def push(self, x, y , xSpeed, ySpeed):
        new_node = Node(x, y, xSpeed, ySpeed)
        new_node.next = self.top
        self.top = new_node
        self.size += 1

    def remove_offscreen(self, width, height):
        prev = None
        node = self.top
        while node:
            if node.x < 0 or node.x > width or node.y < 0 or node.y > height:
                if prev:
                    prev.next = node.next
                else:
                    self.top = node.next
                self.size -= 1
                node = node.next
                continue
            prev = node
            node = node.next

    def move_all(self, dt):
        node = self.top
        while node:
            node.x += node.xSpeed * dt
            node.y += node.ySpeed * dt
            node = node.next


pygame.init()
from utils.window_state import WindowState
window_state = WindowState.get_instance()
screen = window_state.create_screen()
clock = pygame.time.Clock()
running = True

# Store reference size for normalization
REF_WIDTH = 1280
REF_HEIGHT = 720

# Load player character images
project_root = __file__.rsplit('SebastiansAwesomeCode', 1)[0]
player_images = {}
player_images_original = {}  # Store original unscaled images
background_img_path = f"{project_root}assets/images/marsBackground.jpg"
dead_image_path = f"{project_root}assets/images/deadBara.png"
enemy_image_path = f"{project_root}assets/images/octopusNormal.png"
damaged_enemy_image_path = f"{project_root}assets/images/octopusDamaged.png"

# Load all images once
try:
    enemy_image_original = pygame.image.load(enemy_image_path)
    damaged_enemy_image_original = pygame.image.load(damaged_enemy_image_path)
    dead_image_original = pygame.image.load(dead_image_path)
except Exception as e:
    print(f"Failed to load enemy images: {e}", file=sys.stderr)
    enemy_image_original = pygame.Surface((100, 100))
    damaged_enemy_image_original = pygame.Surface((100, 100))
    dead_image_original = pygame.Surface((100, 100))
    enemy_image_original.fill("red")
    damaged_enemy_image_original.fill("orange")
    dead_image_original.fill("gray")

# Initialize the scaled versions
enemy_image = enemy_image_original
damaged_enemy_image = damaged_enemy_image_original
dead_image = dead_image_original

# Load player directional images
for direction in ['w', 'a', 's', 'd']:
    try:
        background_img_path = f"{project_root}assets/images/marsBackground.png"
        dead_image_path = f"{project_root}assets/images/deadBara.png"
        enemy_image_path = f"{project_root}assets/images/octopusNormal.png"
        damaged_enemy_image_path = f"{project_root}assets/images/octopusDamaged.png"
        img_path = f"{project_root}assets/images/{direction}Capy.png"
        player_images_original[direction] = pygame.image.load(img_path)
        player_images[direction] = player_images_original[direction]
    except Exception as e:
        print(f"Failed to load player image {direction}Capy.png: {e}", file=sys.stderr)
        player_images_original[direction] = pygame.Surface((100, 100))
        player_images[direction] = player_images_original[direction]
        player_images[direction].fill("brown")

# Default player image (facing left)
current_player_image = player_images.get('a')  # aCapy.png is the default
if not current_player_image:  # Fallback if image loading failed
    print("Failed to load default player image, using placeholder", file=sys.stderr)
    current_player_image = pygame.Surface((100, 100))  # Create a placeholder surface
    current_player_image.fill("brown")

from utils.ui_scaling import normalize_point, denormalize_point, normalize_radius, denormalize_radius

# Store original sizes and calculate size ratios
character_size_ratio = 0.15  # Character takes up 15% of screen height
original_sizes = {
    'player': player_images_original['a'].get_size(),
    'enemy': enemy_image_original.get_size(),
    'damaged_enemy': damaged_enemy_image_original.get_size(),
    'dead': dead_image_original.get_size()
}

def scale_images(screen_height):
    """Scale all images relative to screen height"""
    target_height = int(screen_height * character_size_ratio)
    
    # Scale player images
    for direction in player_images:
        orig = player_images_original[direction]
        aspect_ratio = orig.get_width() / orig.get_height()
        new_size = (int(target_height * aspect_ratio), target_height)
        player_images[direction] = pygame.transform.smoothscale(orig, new_size)
    
    # Scale enemy images
    aspect_ratio = enemy_image_original.get_width() / enemy_image_original.get_height()
    new_size = (int(target_height * aspect_ratio), target_height)
    global enemy_image, damaged_enemy_image, dead_image
    enemy_image = pygame.transform.smoothscale(enemy_image_original, new_size)
    damaged_enemy_image = pygame.transform.smoothscale(damaged_enemy_image_original, new_size)
    dead_image = pygame.transform.smoothscale(dead_image_original, new_size)

# Initial scaling
scale_images(screen.get_height())

# Store normalized coordinates (0-1 range) using reference size
# normalize_point returns a tuple; we need a mutable sequence because the code
# updates the normalized coordinates in-place (e.g., norm_cowboy_pos[0] += ...).
# Convert to list so item assignment is allowed.
norm_cowboy_pos = list(normalize_point(100, 100, (REF_WIDTH, REF_HEIGHT)))
cowboy_pos = list(denormalize_point(norm_cowboy_pos[0], norm_cowboy_pos[1], screen))
player_rect = current_player_image.get_rect(center=cowboy_pos)
stack = LinkedListStack()       # Player bullets
enemy_stack = LinkedListStack() # Enemy bullets

bulletSpeed = 600
enemyBulletSpeed = 400
player_speed = 300
enemy_speed = 150
target_alive = True 
target_killed = False
enemy_health = 3
max_enemy_health = 3
enemyActuallyDead = False
counter = 0
shoot_cooldown = 0
playerDead = False
displayDead = False
freeze = False
count = 0
# Spawn first target (enemy) using normalized coordinates
norm_Xtarget = 0.9  # 90% of screen width
norm_Ytarget = 0.9  # 90% of screen height
Xtarget = int(norm_Xtarget * screen.get_width())
Ytarget = int(norm_Ytarget * screen.get_height())
target_alive = True
# Spawn first target (enemy)
Xtarget = (screen.get_width() - 100)
Ytarget = (screen.get_height() - 100)

# Enemy dodge direction control
dodge_timer = 0
dodge_dx, dodge_dy = 0, 0

while running:
    dt = clock.tick(60) / 1000
    shoot_cooldown += dt
    dodge_timer += dt
  

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.VIDEORESIZE:
            # Update global window state
            window_state.update_size(event.w, event.h)
            screen = window_state.create_screen()
            
            # Update positions based on new screen size using reference-based normalization
            cowboy_pos[0], cowboy_pos[1] = denormalize_point(norm_cowboy_pos[0], norm_cowboy_pos[1], screen)
            Xtarget, Ytarget = denormalize_point(norm_Xtarget, norm_Ytarget, screen)
            
            # Rescale all images for new screen size
            scale_images(screen.get_height())
            
        # Left click to shoot
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            dx = mouse_x - cowboy_pos[0]
            dy = mouse_y - cowboy_pos[1]
            dist = math.sqrt(dx**2 + dy**2)
            if dist != 0:
                dx = (dx / dist) * bulletSpeed
                dy = (dy / dist) * bulletSpeed
            stack.push(cowboy_pos[0], cowboy_pos[1], dx, dy)

    # Player movement and image updates
    keys = pygame.key.get_pressed()
    moved = False
    
    # Calculate movement speed relative to reference size
    normalized_speed = (player_speed * dt) / REF_HEIGHT
    
    if keys[pygame.K_w]:
        norm_cowboy_pos[1] -= normalized_speed
        current_player_image = player_images.get('w', current_player_image)
        moved = True
    if keys[pygame.K_s]:
        norm_cowboy_pos[1] += normalized_speed
        current_player_image = player_images.get('s', current_player_image)
        moved = True
    if keys[pygame.K_a]:
        norm_cowboy_pos[0] -= normalized_speed * (REF_HEIGHT / REF_WIDTH)
        current_player_image = player_images.get('a', current_player_image)
        moved = True
    if keys[pygame.K_d]:
        norm_cowboy_pos[0] += normalized_speed * (REF_HEIGHT / REF_WIDTH)
        current_player_image = player_images.get('d', current_player_image)
        moved = True
    if keys[pygame.K_q] and playerDead:
        running = False

    # ✅ Keep player inside screen (in normalized coordinates)
    norm_cowboy_pos[0] = max(0.05, min(0.95, norm_cowboy_pos[0]))
    norm_cowboy_pos[1] = max(0.05, min(0.95, norm_cowboy_pos[1]))
    
    # Convert normalized coordinates to screen coordinates
    cowboy_pos[0] = int(norm_cowboy_pos[0] * screen.get_width())
    cowboy_pos[1] = int(norm_cowboy_pos[1] * screen.get_height())
    
    # Update player rectangle position
    player_rect.center = cowboy_pos

    if playerDead: 
        current_player_image = dead_image
        #current_player_image = player_images.get('deadBara.jpg')
    # === Enemy Movement (Smart AI) ===
    # Move toward the player
    dx = cowboy_pos[0] - Xtarget
    dy = cowboy_pos[1] - Ytarget
    dist = math.sqrt(dx**2 + dy**2)

    if dist > 0:
        dx /= dist
        dy /= dist

    # Add dodge every 1.5 seconds
    if dodge_timer > 1.5:
        dodge_timer = 0
        dodge_dx = random.uniform(-1, 1)
        dodge_dy = random.uniform(-1, 1)

    # Combine chase and dodge
    move_x = dx + dodge_dx * 0.3
    move_y = dy + dodge_dy * 0.3
    move_dist = math.sqrt(move_x**2 + move_y**2)
    if move_dist > 0:
        move_x /= move_dist
        move_y /= move_dist

    # Update enemy position using normalized speed
    normalized_enemy_speed = (enemy_speed * dt) / REF_HEIGHT
    norm_Xtarget += move_x * normalized_enemy_speed * (REF_HEIGHT / REF_WIDTH)
    norm_Ytarget += move_y * normalized_enemy_speed
    
    # Keep normalized coordinates for position tracking
    
    # Keep within screen bounds in normalized coordinates
    norm_Xtarget = max(0.05, min(0.95, norm_Xtarget))
    norm_Ytarget = max(0.05, min(0.95, norm_Ytarget))
    
    # Convert back to screen coordinates
    Xtarget = int(norm_Xtarget * screen.get_width())
    Ytarget = int(norm_Ytarget * screen.get_height())

    # AI shooting
    if shoot_cooldown >= 1.0:  # Fire every second
        dx = cowboy_pos[0] - Xtarget
        dy = cowboy_pos[1] - Ytarget
        dist = math.sqrt(dx**2 + dy**2)
        if dist != 0:
            dx = (dx / dist) * enemyBulletSpeed
            dy = (dy / dist) * enemyBulletSpeed
        enemy_stack.push(Xtarget, Ytarget, dx, dy)
        shoot_cooldown = 0

    # Move bullets
    stack.move_all(dt)
    enemy_stack.move_all(dt)
    stack.remove_offscreen(screen.get_width(), screen.get_height())
    enemy_stack.remove_offscreen(screen.get_width(), screen.get_height())

    # Collision check (player bullets hit target)
    node = stack.top
    while node:
        if math.hypot(node.x - Xtarget, node.y - Ytarget) < 50 and target_alive:
                target_killed = True
                 # Stop after one hit per bullet frame

        node = node.next

    # Collision check (enemy bullets hit player)
    node = enemy_stack.top
    while node:
        if math.hypot(node.x - cowboy_pos[0], node.y - cowboy_pos[1]) < 50:
            print("💀 You got hit!")
            playerDead = True
        node = node.next

    # Respawn target if killed
    if target_killed:
        target_alive = False
        counter += dt
        if counter >= 0.5:
            # Generate normalized random position
            norm_Xtarget = random.uniform(0.1, 0.9)
            norm_Ytarget = random.uniform(0.1, 0.9)
            # Convert to screen coordinates
            Xtarget = int(norm_Xtarget * screen.get_width())
            Ytarget = int(norm_Ytarget * screen.get_height())
        
        if counter >= 1.0:
            enemy_health -= 1
            if enemy_health < 0: enemyActuallyDead = True
            Xtarget = random.randint(100, screen.get_width() - 100)
            Ytarget = random.randint(100, screen.get_height() - 100)
            target_alive = True
            target_killed = False
            counter = 0

    # Draw everything
    screen.fill("white")
    background_img = pygame.image.load(background_img_path).convert()
    scale_x = screen.get_width() / background_img.get_width()
    scale_y = screen.get_height() / background_img.get_height()
    scale = min(scale_x, scale_y)  # keeps aspect ratio
    background_scaled = pygame.transform.smoothscale_by(background_img, scale)
    screen.blit(background_scaled, (0, 0))

    # Draw player character using current image
    screen.blit(current_player_image, player_rect)
    if enemyActuallyDead:    
        freeze = True
        target_alive = False

    if target_alive:
        enemy_rect = enemy_image.get_rect(center=(Xtarget, Ytarget))
        screen.blit(enemy_image, enemy_rect)
    else:
        damaged_enemy_rect = damaged_enemy_image.get_rect(center=(Xtarget, Ytarget))
        screen.blit(damaged_enemy_image, damaged_enemy_rect)

    # Draw player bullets with relative size
    bullet_radius = denormalize_radius(0.01, screen)  # 1% of screen size
    bar_width = 100
    bar_height = 10
    bar_x = Xtarget - bar_width / 2
    bar_y = Ytarget - 70
    health_ratio = max(enemy_health / max_enemy_health, 0)
    pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))

    # Player bullets
    node = stack.top
    while node:
        pygame.draw.circle(screen, "yellow", (int(node.x), int(node.y)), int(bullet_radius))
        node = node.next

    # Enemy bullets with relative size
    node = enemy_stack.top
    while node:
        pygame.draw.circle(screen, "red", (int(node.x), int(node.y)), int(bullet_radius))
        node = node.next
    if not freeze:
        pygame.display.flip()
        if playerDead: 
            count += dt
            if count >= 0.5:
                freeze = True
    if playerDead:
        displayDead = True

pygame.quit()
