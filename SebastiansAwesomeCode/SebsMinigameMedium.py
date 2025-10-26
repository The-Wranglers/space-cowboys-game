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
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

cowboy_pos = [screen.get_width() // 2, screen.get_height() // 2]
stack = LinkedListStack()       # Player bullets
enemy_stack = LinkedListStack() # Enemy bullets

bulletSpeed = 600
enemyBulletSpeed = 400
speed = 300
target_speed = 200  # enemy’s max speed
target_alive = True
target_killed = False
counter = 0
shoot_cooldown = 0

# Spawn first target
Xtarget = random.randint(100, screen.get_width() - 100)
Ytarget = random.randint(100, screen.get_height() - 100)

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

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        cowboy_pos[1] -= speed * dt
    if keys[pygame.K_s]:
        cowboy_pos[1] += speed * dt
    if keys[pygame.K_a]:
        cowboy_pos[0] -= speed * dt
    if keys[pygame.K_d]:
        cowboy_pos[0] += speed * dt

    # --- Enemy AI movement (dodging bullets) ---
    dodge_x, dodge_y = 0, 0
    node = stack.top
    while node:
        dx = Xtarget - node.x
        dy = Ytarget - node.y
        dist = math.hypot(dx, dy)

        # Only dodge if the bullet is somewhat close
        if dist < 250:
            # Move away from the bullet’s direction, weighted by distance
            if dist > 0:
                dodge_x += dx / dist * (250 - dist) / 250
                dodge_y += dy / dist * (250 - dist) / 250
        node = node.next

    # Normalize dodge direction (make it smoother)
    mag = math.hypot(dodge_x, dodge_y)
    if mag > 0:
        dodge_x /= mag
        dodge_y /= mag

    # Add a little random movement so it’s not perfectly predictive
    dodge_x += random.uniform(-0.2, 0.2)
    dodge_y += random.uniform(-0.2, 0.2)

    # Move target
    Xtarget += dodge_x * target_speed * dt
    Ytarget += dodge_y * target_speed * dt

    # Keep inside screen
    Xtarget = max(50, min(screen.get_width() - 50, Xtarget))
    Ytarget = max(50, min(screen.get_height() - 50, Ytarget))

    # --- AI shooting ---
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
    pygame.draw.circle(screen, "brown", cowboy_pos, 50)
    if target_alive:
        pygame.draw.circle(screen, "green", (int(Xtarget), int(Ytarget)), 50)
    else:
        pygame.draw.circle(screen, "red", (int(Xtarget), int(Ytarget)), 50)
    node = stack.top
    while node:
        pygame.draw.circle(screen, "yellow", (int(node.x), int(node.y)), 8)
        node = node.next
    node = enemy_stack.top
    while node:
        pygame.draw.circle(screen, "red", (int(node.x), int(node.y)), 8)
        node = node.next
    pygame.display.flip()

pygame.quit()
