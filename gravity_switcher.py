import pygame
import asyncio
import platform
import random
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity Switcher")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Game settings
TILE_SIZE = 40
PLAYER_SIZE = 20
ORB_SIZE = 10
FPS = 60

# Maze layout (1: wall, 0: empty, 2: player start, 3: orb, 4: exit, 5: spike)
maze = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 3, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 3, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

class Player:
    def __init__(self, x: int, y: int):
        self.x = x * TILE_SIZE + TILE_SIZE // 2
        self.y = y * TILE_SIZE + TILE_SIZE // 2
        self.vx = 0
        self.vy = 0
        self.gravity = 0.5
        self.gravity_dir = "down"

    def move(self, maze: List[List[int]]):
        # Apply gravity
        if self.gravity_dir == "down":
            self.vy += self.gravity
        elif self.gravity_dir == "up":
            self.vy -= self.gravity
        elif self.gravity_dir == "left":
            self.vx -= self.gravity
        elif self.gravity_dir == "right":
            self.vx += self.gravity

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Collision detection
        for i in range(len(maze)):
            for j in range(len(maze[0])):
                if maze[i][j] in [1, 5]:
                    rect = pygame.Rect(j * TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    player_rect = pygame.Rect(self.x - PLAYER_SIZE // 2, self.y - PLAYER_SIZE // 2, PLAYER_SIZE, PLAYER_SIZE)
                    if player_rect.colliderect(rect):
                        if maze[i][j] == 5:
                            return False
                        # Resolve collision based on gravity direction
                        if self.gravity_dir == "down" and self.vy > 0:
                            self.y = i * TILE_SIZE - PLAYER_SIZE // 2
                            self.vy = 0
                        elif self.gravity_dir == "up" and self.vy < 0:
                            self.y = (i + 1) * TILE_SIZE + PLAYER_SIZE // 2
                            self.vy = 0
                        elif self.gravity_dir == "left" and self.vx < 0:
                            self.x = (j + 1) * TILE_SIZE + PLAYER_SIZE // 2
                            self.vx = 0
                        elif self.gravity_dir == "right" and self.vx > 0:
                            self.x = j * TILE_SIZE - PLAYER_SIZE // 2
                            self.vx = 0
        return True

    def draw(self):
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), PLAYER_SIZE // 2)

class Game:
    def __init__(self):
        self.player = None
        self.orbs = []
        self.exit_pos = (0, 0)
        self.orb_count = 0
        self.collected_orbs = 0
        self.font = pygame.font.SysFont("arial", 24)
        self.clock = pygame.time.Clock()
        self.setup_level()

    def setup_level(self):
        for i in range(len(maze)):
            for j in range(len(maze[0])):
                if maze[i][j] == 2:
                    self.player = Player(j, i)
                elif maze[i][j] == 3:
                    self.orbs.append((j * TILE_SIZE + TILE_SIZE // 2, i * TILE_SIZE + TILE_SIZE // 2))
                    self.orb_count += 1
                elif maze[i][j] == 4:
                    self.exit_pos = (j * TILE_SIZE + TILE_SIZE // 2, i * TILE_SIZE + TILE_SIZE // 2)

    def draw(self):
        screen.fill(BLACK)
        for i in range(len(maze)):
            for j in range(len(maze[0])):
                if maze[i][j] == 1:
                    pygame.draw.rect(screen, WHITE, (j * TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                elif maze[i][j] == 3:
                    pygame.draw.circle(screen, YELLOW, (j * TILE_SIZE + TILE_SIZE // 2, i * TILE_SIZE + TILE_SIZE // 2), ORB_SIZE)
                elif maze[i][j] == 4:
                    pygame.draw.rect(screen, GREEN, (j * TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                elif maze[i][j] == 5:
                    pygame.draw.rect(screen, RED, (j * TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        self.player.draw()
        for orb in self.orbs:
            pygame.draw.circle(screen, YELLOW, orb, ORB_SIZE)
        score_text = self.font.render(f"Orbs: {self.collected_orbs}/{self.orb_count}", True, WHITE)
        screen.blit(score_text, (10, 10))

async def main():
    game = Game()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game.player.gravity_dir == "down":
                        game.player.gravity_dir = "up"
                        game.player.vy = 0
                    elif game.player.gravity_dir == "up":
                        game.player.gravity_dir = "left"
                        game.player.vy = 0
                        game.player.vx = 0
                    elif game.player.gravity_dir == "left":
                        game.player.gravity_dir = "right"
                        game.player.vx = 0
                    elif game.player.gravity_dir == "right":
                        game.player.gravity_dir = "down"
                        game.player.vx = 0

        # Update player
        if not game.player.move(maze):
            running = False

        # Check orb collection
        player_rect = pygame.Rect(game.player.x - PLAYER_SIZE // 2, game.player.y - PLAYER_SIZE // 2, PLAYER_SIZE, PLAYER_SIZE)
        for orb in game.orbs[:]:
            orb_rect = pygame.Rect(orb[0] - ORB_SIZE, orb[1] - ORB_SIZE, ORB_SIZE * 2, ORB_SIZE * 2)
            if player_rect.colliderect(orb_rect):
                game.orbs.remove(orb)
                game.collected_orbs += 1
                maze[orb[1] // TILE_SIZE][orb[0] // TILE_SIZE] = 0

        # Check exit condition
        if game.collected_orbs == game.orb_count:
            exit_rect = pygame.Rect(game.exit_pos[0] - TILE_SIZE // 2, game.exit_pos[1] - TILE_SIZE // 2, TILE_SIZE, TILE_SIZE)
            if player_rect.colliderect(exit_rect):
                running = False  # Win condition

        game.draw()
        pygame.display.flip()
        game.clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

    pygame.quit()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
