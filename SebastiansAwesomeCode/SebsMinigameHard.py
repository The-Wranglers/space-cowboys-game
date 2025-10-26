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
screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
clock = pygame.time.Clock()
running = True

cowboy_pos = [screen.get_width() // 2, screen.get_height() // 2]
stack = LinkedListStack()       # Player bullets
enemy_stack = LinkedListStack() # Enemy bullets

bulletSpeed = 600
enemyBulletSpeed = 400
speed = 300
target_speed = 120
target_alive = True
target_killed = False
counter = 0
shoot_cooldown = 0

# Enemy     
Xtarget = random.randint(100, screen.get_width() - 100)
Ytarget = random.randint(100, screen.get_height() - 100)

# Enemy movement direction
target_dir = [random.choice([-1, 1]), random.choice([-1, 1])]

# Enemy radius
ENEMY_RADIUS = 50

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

    # Enemy movement (wanders and dodges player bullets)
    Xtarget += target_dir[0] * target_speed * dt
    Ytarget += target_dir[1] * target_speed * dt

    # Keep enemy inside the screen
    if Xtarget < ENEMY_RADIUS:
        Xtarget = ENEMY_RADIUS
        target_dir[0] = abs(target_dir[0])  # Bounce right
    elif Xtarget > screen.get_width() - ENEMY_RADIUS:
        Xtarget = screen.get_width() - ENEMY_RADIUS
        target_dir[0] = -abs(target_dir[0])  # Bounce left

    if Ytarget < ENEMY_RADIUS:
        Ytarget = ENEMY_RADIUS
        target_dir[1] = abs(target_dir[1])  # Bounce down
    elif Ytarget > screen.get_height() - ENEMY_RADIUS:
        Ytarget = screen.get_height() - ENEMY_RADIUS
        target_dir[1] = -abs(target_dir[1])  # Bounce up

    # Occasionally change direction randomly
    if random.random() < 0.01:
        target_dir = [random.choice([-1, 0, 1]), random.choice([-1, 0, 1])]

    # Dodge nearest bullet if too close
    node = stack.top
    while node:
        dist = math.hypot(node.x - Xtarget, node.y - Ytarget)
        if dist < 200:  # Dodge if bullet nearby
            if node.x < Xtarget:
                target_dir[0] = 1
            else:
                target_dir[0] = -1
            if node.y < Ytarget:
                target_dir[1] = 1
            else:
                target_dir[1] = -1
        node = node.next

    # Enemy shooting logic — fires every 0.5 seconds
    if shoot_cooldown >= 0.5:
        # Predictive shot
        dx = cowboy_pos[0] - Xtarget
        dy = cowboy_pos[1] - Ytarget
        player_speed_x = (keys[pygame.K_d] - keys[pygame.K_a]) * speed
        player_speed_y = (keys[pygame.K_s] - keys[pygame.K_w]) * speed

        predicted_x = cowboy_pos[0] + player_speed_x * 0.3
        predicted_y = cowboy_pos[1] + player_speed_y * 0.3
        dx = predicted_x - Xtarget
        dy = predicted_y - Ytarget
        dist = math.sqrt(dx**2 + dy**2)
        if dist != 0:
            dx = (dx / dist) * enemyBulletSpeed
            dy = (dy / dist) * enemyBulletSpeed
        enemy_stack.push(Xtarget, Ytarget, dx, dy)

        # Random bullet
        angle = random.uniform(0, math.tau)
        dx2 = math.cos(angle) * enemyBulletSpeed
        dy2 = math.sin(angle) * enemyBulletSpeed
        enemy_stack.push(Xtarget, Ytarget, dx2, dy2)

        shoot_cooldown = 0

    # Move bullets
    stack.move_all(dt)
    enemy_stack.move_all(dt)
    stack.remove_offscreen(screen.get_width(), screen.get_height())
    enemy_stack.remove_offscreen(screen.get_width(), screen.get_height())

    # Collision check (player bullets hit target)
    node = stack.top
    while node:
        if math.hypot(node.x - Xtarget, node.y - Ytarget) < ENEMY_RADIUS:
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
        pygame.draw.circle(screen, "green", (int(Xtarget), int(Ytarget)), ENEMY_RADIUS)
    else:
        pygame.draw.circle(screen, "red", (int(Xtarget), int(Ytarget)), ENEMY_RADIUS)
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
