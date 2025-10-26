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
screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
clock = pygame.time.Clock()
running = True

# Load player character images
project_root = __file__.rsplit('SebastiansAwesomeCode', 1)[0]
player_images = {}
for direction in ['w', 'a', 's', 'd']:
    try:
        img_path = f"{project_root}assets/images/{direction}Capy.png"
        player_images[direction] = pygame.image.load(img_path)
    except Exception as e:
        print(f"Failed to load player image {direction}Capy.png: {e}", file=sys.stderr)

# Default player image (facing left)
current_player_image = player_images.get('a')  # aCapy.png is the default
if not current_player_image:  # Fallback if image loading failed
    print("Failed to load default player image, using placeholder", file=sys.stderr)
    current_player_image = pygame.Surface((100, 100))  # Create a placeholder surface
    current_player_image.fill("brown")

cowboy_pos = [screen.get_width() // 2, screen.get_height() // 2]
player_rect = current_player_image.get_rect(center=cowboy_pos)
stack = LinkedListStack()       # Player bullets
enemy_stack = LinkedListStack() # Enemy bullets

bulletSpeed = 600
enemyBulletSpeed = 400
player_speed = 300
enemy_speed = 150
target_alive = True
target_killed = False
counter = 0
shoot_cooldown = 0

# Spawn first target (enemy)
Xtarget = random.randint(100, screen.get_width() - 100)
Ytarget = random.randint(100, screen.get_height() - 100)

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
    if keys[pygame.K_w]:
        cowboy_pos[1] -= player_speed * dt
        current_player_image = player_images.get('w', current_player_image)
        moved = True
    if keys[pygame.K_s]:
        cowboy_pos[1] += player_speed * dt
        current_player_image = player_images.get('s', current_player_image)
        moved = True
    if keys[pygame.K_a]:
        cowboy_pos[0] -= player_speed * dt
        current_player_image = player_images.get('a', current_player_image)
        moved = True
    if keys[pygame.K_d]:
        cowboy_pos[0] += player_speed * dt
        current_player_image = player_images.get('d', current_player_image)
        moved = True
    
    # Update player rectangle position
    player_rect.center = cowboy_pos

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

    # Update enemy position
    Xtarget += move_x * enemy_speed * dt
    Ytarget += move_y * enemy_speed * dt

    # Keep within screen
    Xtarget = max(50, min(screen.get_width() - 50, Xtarget))
    Ytarget = max(50, min(screen.get_height() - 50, Ytarget))

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
        if math.hypot(node.x - Xtarget, node.y - Ytarget) < 50:
            target_killed = True
            target_alive = False
        node = node.next

    # Collision check (enemy bullets hit player)
    node = enemy_stack.top
    while node:
        if math.hypot(node.x - cowboy_pos[0], node.y - cowboy_pos[1]) < 50:
            print("💀 You got hit!")
            running = False
        node = node.next

    # Respawn target if killed
    if target_killed:
        counter += dt
        if counter >= 0.5:
            Xtarget = random.randint(100, screen.get_width() - 100)
            Ytarget = random.randint(100, screen.get_height() - 100)
            target_alive = True
            target_killed = False
            counter = 0

    # Draw everything
    screen.fill("white")
    # Draw player character using current image
    screen.blit(current_player_image, player_rect)
    if target_alive:
        pygame.draw.circle(screen, "green", (int(Xtarget), int(Ytarget)), 50)
    else:
        pygame.draw.circle(screen, "red", (int(Xtarget), int(Ytarget)), 50)

    # Player bullets
    node = stack.top
    while node:
        pygame.draw.circle(screen, "yellow", (int(node.x), int(node.y)), 8)
        node = node.next

    # Enemy bullets
    node = enemy_stack.top
    while node:
        pygame.draw.circle(screen, "red", (int(node.x), int(node.y)), 8)
        node = node.next
 
    pygame.display.flip()

pygame.quit()
