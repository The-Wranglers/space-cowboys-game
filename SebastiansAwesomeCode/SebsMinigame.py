# Example file showing a circle moving on screen + linked-list bullets
import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0.0

class Bullet:
    def __init__(self, pos: pygame.Vector2, vel: pygame.Vector2  ):
        self.pos = pos
        self.vel = vel

    def update(self, dt: float):
        self.pos += self.vel * dt

    def is_offscreen(self, width: int, height: int) -> bool:
        return (self.pos.x < 0 or self.pos.x > width or
                self.pos.y < 0 or self.pos.y > height)


class Node:

    def __init__(self, bullet: Bullet):
        self.bullet = bullet
        self.next = None


class BulletLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def append(self, bullet: Bullet):
        node = Node(bullet)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.length += 1

    def remove_next_of(self, prev: Node):
        """Remove prev.next. If prev is None remove head."""
        if prev is None:
            # remove head
            if self.head is None:
                return
            removed = self.head
            self.head = removed.next
            if self.head is None:
                self.tail = None
        else:
            removed = prev.next
            if removed is None:
                return
            prev.next = removed.next
            if prev.next is None:
                self.tail = prev
        self.length -= 1

    def iterate(self):
        """Yield (prev_node, node) pairs for safe removal while iterating."""
        prev = None
        node = self.head
        while node is not None:
            yield prev, node
            prev = node
            node = node.next

    def __len__(self):
        return self.length

# ----- Game state -----
player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

# last known aim direction (set when player presses WASD). Default to "up".
aim_dir = "up"

# linked list of bullets
bullets = BulletLinkedList()

# bullet settings
BULLET_SPEED = 700  # pixels per second

# ----- Main loop -----
while running:
    # Event handling (use KEYDOWN so each space press spawns one bullet)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # create bullet at player position, velocity based on aim_dir
                start_pos = player_pos.copy()
                if aim_dir == "up":
                    vel = pygame.Vector2(0, -BULLET_SPEED)
                    start_pos.y -= 40  # offset to front of player
                elif aim_dir == "down":
                    vel = pygame.Vector2(0, BULLET_SPEED)
                    start_pos.y += 40
                elif aim_dir == "left":
                    vel = pygame.Vector2(-BULLET_SPEED, 0)
                    start_pos.x -= 40
                elif aim_dir == "right":
                    vel = pygame.Vector2(BULLET_SPEED, 0)
                    start_pos.x += 40
                else:
                    # fallback
                    vel = pygame.Vector2(0, -BULLET_SPEED)

                b = Bullet(pos=start_pos, vel=vel)
                bullets.append(b)

    # continuous input for player movement and updating aim_dir
    keys = pygame.key.get_pressed()
    speed = 300
    if keys[pygame.K_w]:
        player_pos.y -= speed * dt
        aim_dir = "up"
    if keys[pygame.K_s]:
        player_pos.y += speed * dt
        aim_dir = "down"
    if keys[pygame.K_a]:
        player_pos.x -= speed * dt
        aim_dir = "left"
    if keys[pygame.K_d]:
        player_pos.x += speed * dt
        aim_dir = "right"

    # Update bullets: move and remove offscreen bullets
    screen_width, screen_height = screen.get_size()
    for prev, node in list(bullets.iterate()):
        node.bullet.update(dt)
        if node.bullet.is_offscreen(screen_width, screen_height):
            bullets.remove_next_of(prev)

    # draw
    screen.fill("black")

    # player
    pygame.draw.circle(screen, "blue", (int(player_pos.x), int(player_pos.y)), 40)
    pygame.draw.circle(screen, "black", (int(player_pos.x-15), int(player_pos.y-10)), 10)
    pygame.draw.circle(screen, "black", (int(player_pos.x+15), int(player_pos.y-10)), 10)
    pygame.draw.rect(screen, "black", (int(player_pos.x-30), int(player_pos.y+10), 60, 10))

    if aim_dir == "up":
        pygame.draw.polygon(screen, "black", [(player_pos.x - 10, player_pos.y - 30),
                                              (player_pos.x + 10, player_pos.y - 30),
                                              (player_pos.x, player_pos.y - 50)])
    elif aim_dir == "down":
        pygame.draw.polygon(screen, "black", [(player_pos.x - 10, player_pos.y + 30),
                                              (player_pos.x + 10, player_pos.y + 30),
                                              (player_pos.x, player_pos.y + 50)])
    elif aim_dir == "left":
        pygame.draw.polygon(screen, "black", [(player_pos.x - 30, player_pos.y - 10),
                                              (player_pos.x - 30, player_pos.y + 10),
                                              (player_pos.x - 50, player_pos.y)])
    elif aim_dir == "right":
        pygame.draw.polygon(screen, "black", [(player_pos.x + 30, player_pos.y - 10),
                                              (player_pos.x + 30, player_pos.y + 10),
                                              (player_pos.x + 50, player_pos.y)])

    node = bullets.head
    while node is not None:
        b = node.bullet
        pygame.draw.circle(screen, "yellow", (int(b.pos.x), int(b.pos.y)), 15)
        node = node.next

    pygame.display.flip()

    # tick
    dt = clock.tick(60) / 1000.0

pygame.quit()
