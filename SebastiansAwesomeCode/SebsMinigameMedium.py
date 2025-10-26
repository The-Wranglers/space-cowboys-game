import pygame
import math
import random

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

    def push(self, x, y, xSpeed, ySpeed):
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

cowboy_pos = [screen.get_width() // 2, screen.get_height() // 2]
stack = LinkedListStack()       # Player bullets
enemy_stack = LinkedListStack() # Enemy bullets

bulletSpeed = 600
enemyBulletSpeed = 400
speed = 300
target_speed = 220
target_alive = True
target_killed = False
counter = 0
shoot_cooldown = 0

# Spawn target
Xtarget = random.randint(100, screen.get_width() - 100)
Ytarget = random.randint(100, screen.get_height() - 100)

# Enemy AI movement state
target_dir_x = random.uniform(-1, 1)
target_dir_y = random.uniform(-1, 1)

while running:
    dt = clock.tick(60) / 1000
    shoot_cooldown += dt

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

    # --- Player movement ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        cowboy_pos[1] -= speed * dt
    if keys[pygame.K_s]:
        cowboy_pos[1] += speed * dt
    if keys[pygame.K_a]:
        cowboy_pos[0] -= speed * dt
    if keys[pygame.K_d]:
        cowboy_pos[0] += speed * dt

    # --- Enemy AI (smart dodging + movement) ---
    dodge_x, dodge_y = 0, 0
    threat_count = 0

    node = stack.top
    while node:
        dx = node.x - Xtarget
        dy = node.y - Ytarget
        dist = math.hypot(dx, dy)
        if dist < 300:
            # Predict bullet trajectory by its velocity direction
            bullet_angle = math.atan2(node.ySpeed, node.xSpeed)
            # Vector perpendicular to bullet (strafing)
            strafe_x = -math.sin(bullet_angle)
            strafe_y = math.cos(bullet_angle)
            # Move sideways relative to bullet path
            dodge_x += strafe_x * (300 - dist) / 300
            dodge_y += strafe_y * (300 - dist) / 300
            threat_count += 1
        node = node.next

    # Normalize dodge
    mag = math.hypot(dodge_x, dodge_y)
    if mag > 0:
        dodge_x /= mag
        dodge_y /= mag

    # If no bullets nearby, roam naturally
    if threat_count == 0:
        # Gradually change direction for smooth wandering
        target_dir_x += random.uniform(-0.3, 0.3) * dt
        target_dir_y += random.uniform(-0.3, 0.3) * dt
        mag = math.hypot(target_dir_x, target_dir_y)
        if mag > 0:
            target_dir_x /= mag
            target_dir_y /= mag
        move_x = target_dir_x
        move_y = target_dir_y
    else:
        # Combine dodging with a little random jitter
        move_x = dodge_x + random.uniform(-0.1, 0.1)
        move_y = dodge_y + random.uniform(-0.1, 0.1)

    # Move the target
    Xtarget += move_x * target_speed * dt
    Ytarget += move_y * target_speed * dt

    # Keep inside the screen
    if Xtarget < 50 or Xtarget > screen.get_width() - 50:
        target_dir_x *= -1
    if Ytarget < 50 or Ytarget > screen.get_height() - 50:
        target_dir_y *= -1
    Xtarget = max(50, min(screen.get_width() - 50, Xtarget))
    Ytarget = max(50, min(screen.get_height() - 50, Ytarget))

    # --- AI shooting ---
    if shoot_cooldown >= 1.2:  # Fire every 1.2 seconds
        dx = cowboy_pos[0] - Xtarget
        dy = cowboy_pos[1] - Ytarget
        dist = math.sqrt(dx**2 + dy**2)
        if dist != 0:
            dx = (dx / dist) * enemyBulletSpeed
            dy = (dy / dist) * enemyBulletSpeed
        enemy_stack.push(Xtarget, Ytarget, dx, dy)
        shoot_cooldown = 0

    # --- Update bullets ---
    stack.move_all(dt)
    enemy_stack.move_all(dt)
    stack.remove_offscreen(screen.get_width(), screen.get_height())
    enemy_stack.remove_offscreen(screen.get_width(), screen.get_height())

    # --- Collision detection ---
    node = stack.top
    while node:
        if math.hypot(node.x - Xtarget, node.y - Ytarget) < 50:
            target_killed = True
            target_alive = False
        node = node.next

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

    # --- Drawing ---
    screen.fill("white")
    pygame.draw.circle(screen, "brown", cowboy_pos, 50)
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
