import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen Settings
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooting Game")

# Colors
WHITE = (255, 255, 255)
RED = (255, 50, 50)
PURPLE = (138, 43, 226)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 100)
BLUE = (50, 150, 255)
ORANGE = (255, 165, 0)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Fonts
font_small = pygame.font.SysFont("Arial", 20, bold=True)
font_med = pygame.font.SysFont("Arial", 30, bold=True)
font_big = pygame.font.SysFont("Arial", 50, bold=True)


# ---------------- CLASSES ---------------- #

class Player:
    def __init__(self):
        self.width = 40
        self.height = 40
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 70
        self.speed = 6
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.cooldown = 0
        self.lives = 3
        self.invincible = 0

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > HEIGHT // 2:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT - 10:
            self.rect.y += self.speed

    def draw(self, surf):
        # Flash when invincible
        if self.invincible > 0 and self.invincible % 10 < 5:
            return
        # Ship body (triangle)
        cx = self.rect.centerx
        top_y = self.rect.top
        bottom_y = self.rect.bottom
        left_x = self.rect.left
        right_x = self.rect.right
        pygame.draw.polygon(surf, BLUE, [(cx, top_y), (left_x, bottom_y), (right_x, bottom_y)])
        pygame.draw.polygon(surf, WHITE, [(cx, top_y), (left_x, bottom_y), (right_x, bottom_y)], 2)
        # Cockpit
        pygame.draw.circle(surf, YELLOW, (cx, self.rect.centery + 4), 5)
        # Thrusters
        pygame.draw.polygon(surf, ORANGE, [(cx - 10, bottom_y), (cx + 10, bottom_y), (cx, bottom_y + 12)])

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.invincible > 0:
            self.invincible -= 1


class Bullet:
    def __init__(self, x, y, vy=-10, color=YELLOW, radius=3):
        self.x = x
        self.y = y
        self.vy = vy
        self.color = color
        self.radius = radius

    def update(self):
        self.y += self.vy

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

    def offscreen(self):
        return self.y < -10 or self.y > HEIGHT + 10


class Enemy:
    def __init__(self, level):
        self.size = random.randint(25, 40)
        self.x = random.randint(self.size, WIDTH - self.size)
        self.y = -self.size
        # Difficulty scales with level
        self.base_speed = 1.5 + level * 0.5
        self.speed = self.base_speed + random.uniform(0, level * 0.3)
        self.hp = 1 + (level - 1) // 2  # More HP at higher levels
        self.color = RED if self.hp == 1 else PURPLE
        self.wobble = random.uniform(0, math.pi * 2)
        self.shoot_timer = random.randint(60, 180) - level * 10
        self.shoot_timer = max(self.shoot_timer, 30)
        self.shoot_counter = self.shoot_timer

    def update(self):
        self.y += self.speed
        self.wobble += 0.05
        self.x += math.sin(self.wobble) * 0.8

    def draw(self, surf):
        rect = pygame.Rect(int(self.x - self.size // 2), int(self.y - self.size // 2), self.size, self.size)
        # Draw UFO shape
        pygame.draw.ellipse(surf, self.color, rect)
        pygame.draw.ellipse(surf, WHITE, rect, 2)
        # Eyes
        eye_r = max(3, self.size // 6)
        pygame.draw.circle(surf, WHITE, (int(self.x - self.size // 4), int(self.y)), eye_r)
        pygame.draw.circle(surf, WHITE, (int(self.x + self.size // 4), int(self.y)), eye_r)
        pygame.draw.circle(surf, BLACK, (int(self.x - self.size // 4), int(self.y)), eye_r // 2)
        pygame.draw.circle(surf, BLACK, (int(self.x + self.size // 4), int(self.y)), eye_r // 2)

    def get_rect(self):
        return pygame.Rect(int(self.x - self.size // 2), int(self.y - self.size // 2), self.size, self.size)

    def should_shoot(self):
        self.shoot_counter -= 1
        if self.shoot_counter <= 0:
            self.shoot_counter = self.shoot_timer
            return True
        return False


class EnemyBullet(Bullet):
    def __init__(self, x, y):
        super().__init__(x, y, vy=5, color=RED, radius=4)


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(20, 40)
        self.max_life = self.life
        self.color = color
        self.size = random.randint(2, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        self.life -= 1

    def draw(self, surf):
        if self.life > 0:
            alpha = max(0, min(255, int(255 * self.life / self.max_life)))
            r = self.size * (self.life / self.max_life)
            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), max(1, int(r)))


class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.5, 2.5)
        self.size = random.choice([1, 1, 1, 2, 2, 3])

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surf):
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), self.size)


# ---------------- GAME STATE ---------------- #

def reset_game():
    return {
        "player": Player(),
        "bullets": [],
        "enemies": [],
        "enemy_bullets": [],
        "particles": [],
        "stars": [Star() for _ in range(80)],
        "score": 0,
        "level": 1,
        "enemies_killed": 0,
        "kills_needed": 8,
        "spawn_timer": 0,
        "spawn_delay": 60,
        "game_over": False,
    }


def spawn_particles(particles, x, y, color, count=15):
    for _ in range(count):
        particles.append(Particle(x, y, color))


def draw_hud(surf, state):
    score_txt = font_small.render(f"Score: {state['score']}", True, WHITE)
    level_txt = font_small.render(f"Level: {state['level']}", True, YELLOW)
    lives_txt = font_small.render(f"Lives: {state['player'].lives}", True, GREEN)
    progress_txt = font_small.render(
        f"Kills: {state['enemies_killed']}/{state['kills_needed']}", True, PURPLE
    )
    surf.blit(score_txt, (10, 8))
    surf.blit(level_txt, (WIDTH - 100, 8))
    surf.blit(lives_txt, (10, 30))
    surf.blit(progress_txt, (WIDTH - 130, 30))


def draw_game_over(surf, state):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surf.blit(overlay, (0, 0))
    go_txt = font_big.render("GAME OVER", True, RED)
    surf.blit(go_txt, (WIDTH // 2 - go_txt.get_width() // 2, HEIGHT // 2 - 100))
    score_txt = font_med.render(f"Final Score: {state['score']}", True, WHITE)
    surf.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, HEIGHT // 2 - 30))
    lvl_txt = font_med.render(f"Reached Level: {state['level']}", True, YELLOW)
    surf.blit(lvl_txt, (WIDTH // 2 - lvl_txt.get_width() // 2, HEIGHT // 2 + 10))
    restart_txt = font_small.render("Press R to Restart or ESC to Quit", True, WHITE)
    surf.blit(restart_txt, (WIDTH // 2 - restart_txt.get_width() // 2, HEIGHT // 2 + 70))


# ---------------- MAIN LOOP ---------------- #

def main():
    state = reset_game()
    running = True

    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r and state["game_over"]:
                    state = reset_game()

        # Background
        screen.fill(BLACK)
        for s in state["stars"]:
            s.update()
            s.draw(screen)

        if not state["game_over"]:
            player = state["player"]
            player.move(keys)
            player.update()

            # Shooting
            if (keys[pygame.K_SPACE] or keys[pygame.K_z]) and player.cooldown == 0:
                state["bullets"].append(Bullet(player.rect.centerx, player.rect.top))
                player.cooldown = 10

            # Update bullets
            for b in state["bullets"]:
                b.update()
            state["bullets"] = [b for b in state["bullets"] if not b.offscreen()]

            # Spawn enemies
            state["spawn_timer"] += 1
            # Faster spawns at higher levels
            effective_delay = max(20, state["spawn_delay"] - state["level"] * 5)
            if state["spawn_timer"] >= effective_delay:
                state["spawn_timer"] = 0
                state["enemies"].append(Enemy(state["level"]))
                # Chance to spawn extra enemies at high level
                if state["level"] >= 4 and random.random() < 0.3:
                    state["enemies"].append(Enemy(state["level"]))

            # Update enemies
            for e in state["enemies"]:
                e.update()
                if e.should_shoot():
                    state["enemy_bullets"].append(EnemyBullet(e.x, e.y + e.size // 2))

            # Remove enemies that pass bottom
            for e in list(state["enemies"]):
                if e.y - e.size // 2 > HEIGHT:
                    state["enemies"].remove(e)
                    player.lives -= 1
                    if player.lives <= 0:
                        state["game_over"] = True

            # Update enemy bullets
            for eb in state["enemy_bullets"]:
                eb.update()
            state["enemy_bullets"] = [eb for eb in state["enemy_bullets"] if not eb.offscreen()]

            # Bullet-enemy collisions
            for b in list(state["bullets"]):
                for e in list(state["enemies"]):
                    if e.get_rect().collidepoint(b.x, b.y):
                        if b in state["bullets"]:
                            state["bullets"].remove(b)
                        e.hp -= 1
                        if e.hp <= 0:
                            state["enemies"].remove(e)
                            state["enemies_killed"] += 1
                            points = 10 * state["level"]
                            state["score"] += points
                            spawn_particles(state["particles"], e.x, e.y, e.color, 20)
                        else:
                            spawn_particles(state["particles"], b.x, b.y, YELLOW, 5)
                        break

            # Enemy bullet - player collision
            if player.invincible == 0:
                player_rect = player.rect.inflate(-10, -10)
                for eb in list(state["enemy_bullets"]):
                    if player_rect.collidepoint(eb.x, eb.y):
                        state["enemy_bullets"].remove(eb)
                        player.lives -= 1
                        player.invincible = 90
                        spawn_particles(state["particles"], player.rect.centerx, player.rect.centery, BLUE, 20)
                        if player.lives <= 0:
                            state["game_over"] = True
                        break

            # Enemy - player collision
            if player.invincible == 0:
                player_rect = player.rect.inflate(-10, -10)
                for e in list(state["enemies"]):
                    if e.get_rect().colliderect(player_rect):
                        state["enemies"].remove(e)
                        player.lives -= 1
                        player.invincible = 90
                        spawn_particles(state["particles"], e.x, e.y, e.color, 20)
                        if player.lives <= 0:
                            state["game_over"] = True
                        break

            # Level progression
            if state["enemies_killed"] >= state["kills_needed"]:
                state["level"] += 1
                state["enemies_killed"] = 0
                state["kills_needed"] += 4
                # Clear enemy bullets on level up to give a small break
                state["enemy_bullets"].clear()

            # Draw everything
            for b in state["bullets"]:
                b.draw(screen)
            for eb in state["enemy_bullets"]:
                eb.draw(screen)
            for e in state["enemies"]:
                e.draw(screen)
            player.draw(screen)

        # Particles (always drawn)
        for p in list(state["particles"]):
            p.update()
            p.draw(screen)
            if p.life <= 0:
                state["particles"].remove(p)

        # HUD
        draw_hud(screen, state)

        if state["game_over"]:
            draw_game_over(screen, state)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()