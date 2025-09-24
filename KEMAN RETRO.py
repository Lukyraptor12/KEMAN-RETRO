import pygame
import random
import sys

# --- CONFIGURACIÓN ---
WIDTH, HEIGHT = 900, 700
FPS = 60

# --- COLORES ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
SHIP_COLOR = (100, 200, 255)
ENEMY_COLOR = (200, 50, 80)
BUTTON_COLOR = (30, 30, 120)
BUTTON_HOVER = (60, 60, 200)
SHOP_BG = (40, 20, 60)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (80, 80, 255)
PURPLE = (180, 80, 220)
SHIELD_COLOR = (80, 200, 255, 120)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("KEMAN RETRO")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 30)
big_font = pygame.font.SysFont("consolas", 60)

# --- ASSETS ---
def create_background():
    bg = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        color = (10 + y // 20, 10 + y // 8, 40 + y // 6)
        pygame.draw.line(bg, color, (0, y), (WIDTH, y))
    for _ in range(80):
        x, y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        r = random.randint(1, 3)
        pygame.draw.circle(bg, WHITE, (x, y), r)
    pygame.draw.circle(bg, (120, 60, 200), (WIDTH//4, HEIGHT//3), 70)
    pygame.draw.circle(bg, (255, 160, 50), (WIDTH//2, HEIGHT//1.5), 50)
    pygame.draw.circle(bg, (100, 255, 180), (WIDTH//1.2, HEIGHT//4), 40)
    return bg
background = create_background()

# --- CLASES ---
class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2-25, HEIGHT-120, 60, 60)
        self.speed = 6
        self.coins = 0
        self.skin = SHIP_COLOR
        self.shots = []
        self.shot_power = 1
        self.shot_speed = 11
        self.cooldown = 0
        self.lives = 3
        self.shield = False
        self.shield_timer = 0

    def move(self, keys):
        dx = dy = 0
        if keys[pygame.K_a]: dx -= self.speed
        if keys[pygame.K_d]: dx += self.speed
        if keys[pygame.K_w]: dy -= self.speed
        if keys[pygame.K_s]: dy += self.speed
        self.rect.x = max(0, min(WIDTH-self.rect.width, self.rect.x + dx))
        self.rect.y = max(0, min(HEIGHT-self.rect.height, self.rect.y + dy))

    def shoot(self):
        if self.cooldown == 0:
            if self.shot_power == 1:
                self.shots.append([self.rect.centerx, self.rect.top, 0])
            elif self.shot_power == 2:
                self.shots.append([self.rect.centerx-10, self.rect.top, -2])
                self.shots.append([self.rect.centerx+10, self.rect.top, 2])
            elif self.shot_power == 3:
                self.shots.append([self.rect.centerx-15, self.rect.top, -3])
                self.shots.append([self.rect.centerx, self.rect.top, 0])
                self.shots.append([self.rect.centerx+15, self.rect.top, 3])
            self.cooldown = 10

    def update_shots(self):
        for shot in self.shots[:]:
            shot[1] -= self.shot_speed
            shot[0] += shot[2]
            if shot[1] < -10 or shot[0] < -10 or shot[0] > WIDTH+10:
                self.shots.remove(shot)
        if self.cooldown > 0:
            self.cooldown -= 1

    def draw(self, surface):
        # Nave detallada
        body = pygame.Rect(self.rect.x+10, self.rect.y+10, 40, 40)
        pygame.draw.ellipse(surface, self.skin, body)
        pygame.draw.polygon(surface, self.skin, [
            (self.rect.centerx, self.rect.top),
            (self.rect.x+10, self.rect.y+20),
            (self.rect.x+50, self.rect.y+20)
        ])
        pygame.draw.polygon(surface, (255, 80, 80), [
            (self.rect.centerx, self.rect.bottom),
            (self.rect.centerx-10, self.rect.bottom+15),
            (self.rect.centerx+10, self.rect.bottom+15)
        ])
        # Ventana
        pygame.draw.ellipse(surface, WHITE, (self.rect.centerx-10, self.rect.y+20, 20, 16))
        # Detalle alas
        pygame.draw.polygon(surface, BLUE, [
            (self.rect.x+6, self.rect.y+35),
            (self.rect.x-5, self.rect.y+60),
            (self.rect.x+15, self.rect.y+45)
        ])
        pygame.draw.polygon(surface, BLUE, [
            (self.rect.x+54, self.rect.y+35),
            (self.rect.x+65, self.rect.y+60),
            (self.rect.x+45, self.rect.y+45)
        ])
        # Escudo visual
        if self.shield:
            s = pygame.Surface((self.rect.width+14, self.rect.height+14), pygame.SRCALPHA)
            pygame.draw.ellipse(s, SHIELD_COLOR, (0,0,self.rect.width+14,self.rect.height+14), 4)
            surface.blit(s, (self.rect.x-7, self.rect.y-7))
        # Disparos
        for shot in self.shots:
            pygame.draw.rect(surface, GOLD, (shot[0]-4, shot[1]-12, 8, 18))

    def take_damage(self):
        if self.shield:
            return False
        self.lives -= 1
        return True

class Enemy:
    def __init__(self):
        x = random.randint(50, WIDTH-50)
        y = -60
        self.rect = pygame.Rect(x, y, 60, 60)
        self.speed = random.randint(2, 5)
        self.type = random.choice(["normal", "fast", "tank"])
        self.lives = {"normal": 1, "fast": 1, "tank": 3}[self.type]

    def move(self):
        self.rect.y += self.speed
        if self.type == "fast":
            self.rect.x += random.choice([-1,0,1])

    def draw(self, surface):
        # Enemigo detallado
        if self.type == "normal":
            pygame.draw.polygon(surface, ENEMY_COLOR, [
                (self.rect.centerx, self.rect.top),
                (self.rect.left+10, self.rect.bottom-10),
                (self.rect.right-10, self.rect.bottom-10)
            ])
            pygame.draw.ellipse(surface, PURPLE, (self.rect.x+15, self.rect.y+20, 30, 18))
            pygame.draw.circle(surface, WHITE, (self.rect.centerx, self.rect.y+25), 8)
        elif self.type == "fast":
            pygame.draw.ellipse(surface, RED, self.rect)
            pygame.draw.ellipse(surface, WHITE, (self.rect.x+15, self.rect.y+20, 30, 18))
        elif self.type == "tank":
            pygame.draw.rect(surface, GREEN, (self.rect.x+6, self.rect.y+6, 48, 48))
            pygame.draw.rect(surface, WHITE, (self.rect.x+24, self.rect.y+24, 12, 12))
            pygame.draw.line(surface, BLACK, (self.rect.centerx, self.rect.top), (self.rect.centerx, self.rect.top-12), 6)

class Coin:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(50, WIDTH-50), random.randint(50, HEIGHT-250), 30, 30)
        self.value = random.choice([1,2,5])

    def draw(self, surface):
        pygame.draw.circle(surface, GOLD, self.rect.center, 15)
        pygame.draw.circle(surface, WHITE, self.rect.center, 8, 1)
        value_text = font.render(str(self.value), True, BLACK)
        surface.blit(value_text, (self.rect.centerx-8, self.rect.centery-12))

class Shop:
    def __init__(self, player):
        self.player = player
        self.options = [
            {"name": "Mejorar velocidad nave", "cost": 20, "action": self.upgrade_speed},
            {"name": "Skin azul", "cost": 10, "action": self.skin_blue},
            {"name": "Skin oro", "cost": 50, "action": self.skin_gold},
            {"name": "Mejorar disparo", "cost": 30, "action": self.upgrade_shot},
            {"name": "Activar escudo", "cost": 40, "action": self.give_shield},
            {"name": "Vida extra", "cost": 25, "action": self.extra_life},
            {"name": "Skin especial", "cost": 80, "action": self.skin_special}
        ]

    def upgrade_speed(self):
        if self.player.coins >= 20:
            self.player.coins -= 20
            self.player.speed += 2

    def skin_blue(self):
        if self.player.coins >= 10:
            self.player.coins -= 10
            self.player.skin = (50, 180, 255)

    def skin_gold(self):
        if self.player.coins >= 50:
            self.player.coins -= 50
            self.player.skin = GOLD

    def upgrade_shot(self):
        if self.player.coins >= 30 and self.player.shot_power < 3:
            self.player.coins -= 30
            self.player.shot_power += 1

    def give_shield(self):
        if self.player.coins >= 40 and not self.player.shield:
            self.player.coins -= 40
            self.player.shield = True
            self.player.shield_timer = FPS * 10  # 10 segundos

    def extra_life(self):
        if self.player.coins >= 25:
            self.player.coins -= 25
            self.player.lives += 1

    def skin_special(self):
        if self.player.coins >= 80:
            self.player.coins -= 80
            self.player.skin = (255, 80, 220)

    def draw(self, surface):
        surface.fill(SHOP_BG)
        shop_title = big_font.render("TIENDA", True, GOLD)
        surface.blit(shop_title, (WIDTH//2-120, 60))
        coin_text = font.render(f"Monedas: {self.player.coins}", True, GOLD)
        surface.blit(coin_text, (50, 30))
        for i, opt in enumerate(self.options):
            btn_rect = pygame.Rect(150, 160+i*70, 600, 60)
            mouse = pygame.mouse.get_pos()
            color = BUTTON_HOVER if btn_rect.collidepoint(mouse) else BUTTON_COLOR
            pygame.draw.rect(surface, color, btn_rect, border_radius=12)
            opt_text = font.render(f"{opt['name']} ({opt['cost']} monedas)", True, WHITE)
            surface.blit(opt_text, (btn_rect.x+30, btn_rect.y+12))
        # Volver
        back_btn = pygame.Rect(WIDTH-180, HEIGHT-80, 160, 50)
        pygame.draw.rect(surface, BUTTON_COLOR, back_btn, border_radius=15)
        back_text = font.render("Volver", True, WHITE)
        surface.blit(back_text, (back_btn.x+32, back_btn.y+9))
        return [pygame.Rect(150, 160+i*70, 600, 60) for i in range(len(self.options))], back_btn

# --- FUNCIONES ---
def draw_menu(surface):
    surface.blit(background, (0,0))
    title = big_font.render("KEMAN RETRO", True, GOLD)
    play_btn = pygame.Rect(WIDTH//2-140, 270, 280, 70)
    shop_btn = pygame.Rect(WIDTH//2-140, 370, 280, 70)
    pygame.draw.rect(surface, BUTTON_COLOR, play_btn, border_radius=18)
    pygame.draw.rect(surface, BUTTON_COLOR, shop_btn, border_radius=18)
    play_txt = font.render("JUGAR", True, WHITE)
    shop_txt = font.render("TIENDA", True, WHITE)
    surface.blit(title, (WIDTH//2-180, 140))
    surface.blit(play_txt, (play_btn.x+80, play_btn.y+20))
    surface.blit(shop_txt, (shop_btn.x+80, shop_btn.y+20))
    return play_btn, shop_btn

def game_loop(player):
    coins = []
    enemies = []
    score = 0
    running = True
    spawn_timer = 0
    while running:
        screen.blit(background, (0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    player.shoot()

        keys = pygame.key.get_pressed()
        player.move(keys)
        player.update_shots()

        # Escudo timer
        if player.shield:
            player.shield_timer -= 1
            if player.shield_timer <= 0:
                player.shield = False

        # Generar monedas
        if len(coins) < 6 and random.random() < 0.03:
            coins.append(Coin())

        # Generar enemigos
        spawn_timer += 1
        if spawn_timer > 30:
            if len(enemies) < 7:
                enemies.append(Enemy())
            spawn_timer = 0

        # Colisión monedas
        for coin in coins[:]:
            if player.rect.colliderect(coin.rect):
                player.coins += coin.value
                score += coin.value
                coins.remove(coin)

        # Colisión disparos/enemigos
        for enemy in enemies[:]:
            for shot in player.shots[:]:
                shot_rect = pygame.Rect(shot[0]-4, shot[1]-12, 8, 18)
                if enemy.rect.colliderect(shot_rect):
                    enemy.lives -= 1
                    try: player.shots.remove(shot)
                    except: pass
                    if enemy.lives <= 0:
                        enemies.remove(enemy)
                        player.coins += 4
                        score += 10

        # Colisión jugador/enemigos
        for enemy in enemies[:]:
            if player.rect.colliderect(enemy.rect):
                if player.take_damage():
                    enemies.remove(enemy)
                    if player.lives <= 0:
                        running = False

        # Mover enemigos
        for enemy in enemies[:]:
            enemy.move()
            if enemy.rect.top > HEIGHT:
                try: enemies.remove(enemy)
                except: pass

        # Dibujar monedas, enemigos, jugador
        for coin in coins: coin.draw(screen)
        for enemy in enemies: enemy.draw(screen)
        player.draw(screen)

        # HUD
        hud = font.render(f"Monedas: {player.coins} | Score: {score} | Vidas: {player.lives} | ESC para menú", True, GOLD)
        screen.blit(hud, (20, 20))
        if player.shield:
            shield_text = font.render("ESCUDO ACTIVADO", True, BLUE)
            screen.blit(shield_text, (20, 60))

        pygame.display.flip()
        clock.tick(FPS)

def shop_loop(shop):
    running = True
    while running:
        btns, back_btn = shop.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                for i, btn in enumerate(btns):
                    if btn.collidepoint((mx, my)):
                        shop.options[i]["action"]()
                if back_btn.collidepoint((mx, my)):
                    running = False
        pygame.display.flip()
        clock.tick(30)

# --- MAIN ---
def main():
    player = Player()
    shop = Shop(player)
    while True:
        play_btn, shop_btn = draw_menu(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if play_btn.collidepoint((mx, my)):
                    game_loop(player)
                elif shop_btn.collidepoint((mx, my)):
                    shop_loop(shop)
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()