import pygame
import random
import sys
import math

pygame.init()

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 870
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Enes ve Agartha...")
clock = pygame.time.Clock()

BACKGROUND = pygame.image.load("assets/yol.png").convert()
PLAYER_IMG = pygame.image.load("assets/camaro.png").convert_alpha()
TREE_IMG = pygame.image.load("assets/agac.png").convert_alpha()
AGA_IMG = pygame.image.load("assets/aga.png").convert_alpha()
ENES_IMG = pygame.image.load("assets/enes.png").convert_alpha()
MONSTER_IMG = pygame.image.load("assets/monster.png").convert_alpha()
GUN_IMG = pygame.image.load("assets/gun.png").convert_alpha()
ALIEN_IMG = pygame.image.load("assets/alien.png").convert_alpha()
BOSS_IMG = pygame.image.load("assets/alien.png").convert_alpha()

pygame.mixer.music.load("assets/hmm.mp3")
pygame.mixer.music.set_volume(0.6)

PLAYER_IMG = pygame.transform.scale(PLAYER_IMG, (90, 150))
TREE_IMG = pygame.transform.scale(TREE_IMG, (80, 120))
AGA_IMG = pygame.transform.scale(AGA_IMG, (200, 300))
ENES_IMG = pygame.transform.scale(ENES_IMG, (100, 150))
ENES_DIALOGUE_IMG = pygame.transform.scale(ENES_IMG, (200, 300))  
NPC_CAR_IMG = pygame.transform.scale(PLAYER_IMG, (90, 150))
GUN_IMG = pygame.transform.scale(GUN_IMG, (150, 80))  
ALIEN_IMG = pygame.transform.scale(ALIEN_IMG, (80, 80))
BOSS_IMG = pygame.transform.scale(BOSS_IMG, (300, 300))
MONSTER_DIALOGUE_IMG = pygame.transform.scale(MONSTER_IMG, (220, 220))

shoot_sound = pygame.mixer.Sound("assets/shot.wav")
shoot_sound.set_volume(0.3)

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.1, 0.5)
        self.brightness = random.randint(150, 255)
    
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
    
    def draw(self, surface):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)

class NPC_Car(pygame.sprite.Sprite):
    def __init__(self, lane):
        super().__init__()
        self.lane = lane
        self.image = NPC_CAR_IMG
        
        if self.lane == "left":
            self.image = pygame.transform.rotate(self.image, 180)
            min_x = 50
            max_x = SCREEN_WIDTH // 2 - 50
            self.rect = self.image.get_rect(midtop=(random.randint(min_x, max_x), -100))
            self.speed = random.randint(10, 15)
        else:
            min_x = SCREEN_WIDTH // 2 + 50
            max_x = SCREEN_WIDTH - 50
            self.rect = self.image.get_rect(midtop=(random.randint(min_x, max_x), -100))
            self.speed = random.randint(3, 6)

    def update(self, road_speed):
        self.rect.y += road_speed + self.speed

        if self.rect.top > SCREEN_HEIGHT + 50:
            self.kill()

class ShooterPlayer:
    def __init__(self):
        self.image = ENES_IMG
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.gun_image = GUN_IMG
        self.gun_offset = 100
        self.score = 10
        self.boss_fight = False

    def update_gun(self, mouse_pos):
        dx = mouse_pos[0] - self.rect.centerx
        dy = mouse_pos[1] - self.rect.centery
        angle = math.atan2(dy, dx)
        
        gun_x = self.rect.centerx + math.cos(angle) * self.gun_offset
        gun_y = self.rect.centery + math.sin(angle) * self.gun_offset
        
        rotated_gun = pygame.transform.rotate(self.gun_image, -math.degrees(angle))
        gun_rect = rotated_gun.get_rect(center=(gun_x, gun_y))
        
        return rotated_gun, gun_rect, angle

    def draw(self, surface, mouse_pos):
        surface.blit(self.image, self.rect)
        rotated_gun, gun_rect, _ = self.update_gun(mouse_pos)
        surface.blit(rotated_gun, gun_rect)
        
        bar_width = 200
        bar_height = 15
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - 25
        
        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, bar_width * (self.score / 100), bar_height))
        
        font = pygame.font.Font(None, 24)
        score_text = font.render(f"SCORE: {self.score}", True, (255, 255, 255))
        surface.blit(score_text, (bar_x, bar_y - 20))

class Boss:
    def __init__(self):
        self.image = BOSS_IMG
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH * 3//4, SCREEN_HEIGHT//2))
        self.health = 500
        self.wave_timer = 0
        self.wave_delay = 10 * FPS
        self.alien_bullets = []
        self.last_shot_time = 0
        self.shot_delay = 90

    def update(self):
        self.wave_timer += 1
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shot_delay * 1000 // FPS:
            self.shoot_alien_bullet()
            self.last_shot_time = current_time

    def shoot_alien_bullet(self):
        dx = SCREEN_WIDTH//4 - self.rect.centerx
        dy = SCREEN_HEIGHT//2 - self.rect.centery
        distance = max(math.sqrt(dx*dx + dy*dy), 0.1)
        
        speed = 8
        vx = dx / distance * speed
        vy = dy / distance * speed
        
        self.alien_bullets.append({
            'x': self.rect.centerx,
            'y': self.rect.centery,
            'vx': vx,
            'vy': vy,
            'radius': 8,
            'color': (255, 0, 0)
        })

    def spawn_alien_wave(self):
        aliens = []
        wave_size = 5
        
        for _ in range(wave_size):
            side = random.choice(["top", "right", "bottom"])
            if side == "top":
                x = random.randint(SCREEN_WIDTH//2, SCREEN_WIDTH)
                y = -50
            elif side == "right":
                x = SCREEN_WIDTH + 50
                y = random.randint(0, SCREEN_HEIGHT)
            else:
                x = random.randint(SCREEN_WIDTH//2, SCREEN_WIDTH)
                y = SCREEN_HEIGHT + 50
                
            aliens.append(BossAlien(x, y))
        
        return aliens

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
        bar_width = 200
        bar_height = 20
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - 30
        
        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, bar_width * (self.health / 500), bar_height))
        
        font = pygame.font.Font(None, 24)
        health_text = font.render(f"BOSS: {self.health}", True, (255, 255, 255))
        surface.blit(health_text, (bar_x, bar_y - 20))
        
        for bullet in self.alien_bullets:
            pygame.draw.circle(surface, bullet['color'], (int(bullet['x']), int(bullet['y'])), bullet['radius'])

class BossAlien:
    def __init__(self, x, y):
        self.image = ALIEN_IMG
        self.x = x
        self.y = y
        self.speed = random.randint(3, 5)
        self.target_x = SCREEN_WIDTH // 4
        self.target_y = SCREEN_HEIGHT // 2
        
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = max(math.sqrt(dx*dx + dy*dy), 0.1)
        self.vx = dx / distance * self.speed
        self.vy = dy / distance * self.speed
        
        angle = math.degrees(math.atan2(-dy, dx))
        self.rotated_image = pygame.transform.rotate(self.image, angle)
        self.rect = self.rotated_image.get_rect(center=(self.x, self.y))

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)

    def draw(self, surface):
        surface.blit(self.rotated_image, self.rect)

class Alien:
    def __init__(self):
        self.image = ALIEN_IMG
        self.speed = random.randint(2, 4)
        
        side = random.choice(["top", "right", "bottom", "left"])
        if side == "top":
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = -50
        elif side == "right":
            self.x = SCREEN_WIDTH + 50
            self.y = random.randint(0, SCREEN_HEIGHT)
        elif side == "bottom":
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = SCREEN_HEIGHT + 50
        else:
            self.x = -50
            self.y = random.randint(0, SCREEN_HEIGHT)
            
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.target_x = SCREEN_WIDTH // 2
        self.target_y = SCREEN_HEIGHT // 2
        
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = max(math.sqrt(dx*dx + dy*dy), 0.1)
        self.vx = dx / distance * self.speed
        self.vy = dy / distance * self.speed
        
        angle = math.degrees(math.atan2(-dy, dx))
        self.rotated_image = pygame.transform.rotate(self.image, angle)
        self.rect = self.rotated_image.get_rect(center=(self.x, self.y))

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)

    def draw(self, surface):
        surface.blit(self.rotated_image, self.rect)

class Bullet:
    def __init__(self, start_pos, angle):
        self.x, self.y = start_pos
        self.speed = 15
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed
        self.radius = 4
        self.color = (255, 255, 0)

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def is_off_screen(self):
        return (self.x < 0 or self.x > SCREEN_WIDTH or 
                self.y < 0 or self.y > SCREEN_HEIGHT)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = PLAYER_IMG
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 30))
        self.speed = 8
        self.can_move = True

    def update(self, *args): 
        if not self.can_move:
            return
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

class Tree(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = TREE_IMG
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, -100)
        self.speed = random.randint(4, 7)
        self.has_entered_screen = False

    def update(self, *args):
        self.rect.y += self.speed
        
        if not self.has_entered_screen and self.rect.top >= 0:
            self.has_entered_screen = True
            
        if self.rect.top > SCREEN_HEIGHT + 50:
            self.kill()

class Game:
    def __init__(self):
        self.state = "menu"
        self.font = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 70)
        self.font_small = pygame.font.Font(None, 40)

        self.bg_y1 = 0
        self.bg_y2 = -SCREEN_HEIGHT
        self.road_speed = 5
        
        self.player = Player()
        self.trees = pygame.sprite.Group()
        self.npc_cars = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group(self.player)

        self.tree_spawned = False
        
        self.npc_spawn_timer = 0
        self.npc_spawn_delay = 40
        
        self.center_passes_required = random.randint(1, 10)
        self.current_center_passes = 0
        self.is_centered_and_counted = False
        
        self.dialogue_stage = 0
        self.dialogue_timer = 0
        self.dialogue_delay = 180
        
        self.shooter_player = None
        self.aliens = []
        self.bullets = []
        self.alien_spawn_timer = 0
        self.alien_spawn_delay = 60
        
        self.boss = None
        self.boss_aliens = []
        self.boss_active = False
        self.boss_wave_timer = 0
        
        self.stars = [Star() for _ in range(100)]

    def spawn_tree(self):
        self.player.can_move = False
        tree = Tree()
        self.trees.add(tree)
        self.all_sprites.add(tree)
        self.tree_spawned = True

    def start_shooter_game(self):
        self.shooter_player = ShooterPlayer()
        self.aliens = []
        self.bullets = []
        self.alien_spawn_timer = 0
        self.boss_active = False
        self.boss = None
        self.boss_aliens = []

    def start_boss_fight(self):
        self.boss_active = True
        self.boss = Boss()
        self.boss_aliens = []
        self.boss_wave_timer = 0
        self.shooter_player.rect.center = (SCREEN_WIDTH//4, SCREEN_HEIGHT//2)
        self.shooter_player.boss_fight = True

    def run_menu(self):
        screen.fill((0, 0, 0))
        title = self.font_large.render("Agartha'yı koru!", True, (255, 255, 255))
        start = self.font_small.render("ENTER tuşu ile başla!", True, (200, 200, 200))
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 250)))
        screen.blit(start, start.get_rect(center=(SCREEN_WIDTH//2, 350)))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                pygame.mixer.music.play(-1)
                self.state = "play"

    def run_play(self):
        self.bg_y1 += self.road_speed
        self.bg_y2 += self.road_speed
        if self.bg_y1 >= SCREEN_HEIGHT:
            self.bg_y1 = -SCREEN_HEIGHT
        if self.bg_y2 >= SCREEN_HEIGHT:
            self.bg_y2 = -SCREEN_HEIGHT

        screen.blit(BACKGROUND, (0, self.bg_y1))
        screen.blit(BACKGROUND, (0, self.bg_y2))

        if not self.tree_spawned:
            self.npc_spawn_timer += 1
            if self.npc_spawn_timer >= self.npc_spawn_delay:
                lane = random.choice(["left", "right"])
                new_car = NPC_Car(lane)
                self.npc_cars.add(new_car)
                self.all_sprites.add(new_car)
                self.npc_spawn_timer = 0
        
        if self.player.can_move and not self.tree_spawned:
            center_tolerance = 5
            center_x = SCREEN_WIDTH // 2
            player_center_x = self.player.rect.centerx
            
            player_centered = abs(player_center_x - center_x) < center_tolerance

            if player_centered:
                if not self.is_centered_and_counted:
                    self.current_center_passes += 1
                    self.is_centered_and_counted = True
                    
                    if self.current_center_passes >= self.center_passes_required:
                        self.spawn_tree()
            else:
                self.is_centered_and_counted = False
        
        self.all_sprites.update(self.road_speed)
        
        if pygame.sprite.spritecollide(self.player, self.npc_cars, False):
            self.state = "dead"
            return
            
        for tree in self.trees:
            if tree.has_entered_screen and self.player.can_move:
                self.player.can_move = False

        if pygame.sprite.spritecollide(self.player, self.trees, False):
            self.state = "dialogue"

        self.all_sprites.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def run_dialogue(self):
        screen.fill((20, 20, 40))
        
        screen.blit(AGA_IMG, (100, SCREEN_HEIGHT - 700))
        screen.blit(ENES_DIALOGUE_IMG, (SCREEN_WIDTH - 300, SCREEN_HEIGHT - 700))  
        
        pygame.draw.rect(screen, (30, 30, 60), (50, SCREEN_HEIGHT - 200, SCREEN_WIDTH - 100, 150))
        pygame.draw.rect(screen, (100, 100, 200), (50, SCREEN_HEIGHT - 200, SCREEN_WIDTH - 100, 150), 3)
        
        self.dialogue_timer += 1
        
        if self.dialogue_stage == 0:
            dialogue_text = "Agartha: Uyandın Enes."
            name_text = self.font_small.render("Agartha", True, (100, 200, 255))
            
            if self.dialogue_timer > self.dialogue_delay:
                self.dialogue_stage = 1
                self.dialogue_timer = 0
                
        elif self.dialogue_stage == 1:
            dialogue_text = "Enes: Ne- ne diyorsun sen?"
            name_text = self.font_small.render("Enes", True, (255, 200, 100))
            
            if self.dialogue_timer > self.dialogue_delay:
                self.dialogue_stage = 2
                self.dialogue_timer = 0
                
        elif self.dialogue_stage == 2:
            dialogue_text = "Agartha: Artık sen de Agartha'yı koruyacaksın."
            name_text = self.font_small.render("Agartha", True, (100, 200, 255))
            
            if self.dialogue_timer > self.dialogue_delay:
                self.dialogue_stage = 3
                self.dialogue_timer = 0
                
        elif self.dialogue_stage == 3:
            screen.blit(MONSTER_DIALOGUE_IMG, (270, SCREEN_HEIGHT - 670))
            dialogue_text = "Agartha: Al bunu Enes!"
            name_text = self.font_small.render("Agartha", True, (100, 200, 255))
            
            if self.dialogue_timer > self.dialogue_delay:
                self.start_shooter_game()
                self.state = "shooter"
                self.dialogue_stage = 0
                self.dialogue_timer = 0
        
        text_surface = self.font.render(dialogue_text, True, (255, 255, 255))
        screen.blit(name_text, (70, SCREEN_HEIGHT - 190))
        screen.blit(text_surface, (70, SCREEN_HEIGHT - 140))
        
        if self.dialogue_timer > 30:
            continue_text = self.font_small.render("SPACE ile devam et", True, (200, 200, 200))
            screen.blit(continue_text, (SCREEN_WIDTH - 300, SCREEN_HEIGHT - 50))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.dialogue_stage < 3:
                    self.dialogue_stage += 1
                    self.dialogue_timer = 0
                else:
                    self.start_shooter_game()
                    self.state = "shooter"
                    self.dialogue_stage = 0
                    self.dialogue_timer = 0

    def run_shooter(self):
        screen.fill((0, 0, 20))
        
        for star in self.stars:
            star.update()
            star.draw(screen)
        
        if not self.boss_active and self.shooter_player.score >= 85:
            self.start_boss_fight()
        
        if self.boss_active:
            self.run_boss_fight()
        else:
            self.run_normal_shooter()

    def run_normal_shooter(self):
        self.alien_spawn_timer += 1
        if self.alien_spawn_timer >= self.alien_spawn_delay:
            self.aliens.append(Alien())
            self.alien_spawn_timer = 0
        
        mouse_pos = pygame.mouse.get_pos()
        self.shooter_player.draw(screen, mouse_pos)
        
        for alien in self.aliens[:]:
            alien.update()
            alien.draw(screen)
            
            if alien.rect.colliderect(self.shooter_player.rect):
                self.aliens.remove(alien)
                self.shooter_player.score -= 10
                if self.shooter_player.score <= 0:
                    self.state = "dead"
        
        for bullet in self.bullets[:]:
            bullet.update()
            bullet.draw(screen)
            
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
                continue
                
            for alien in self.aliens[:]:
                bullet_pos = (bullet.x, bullet.y)
                alien_pos = alien.rect.center
                distance = math.sqrt((bullet_pos[0]-alien_pos[0])**2 + (bullet_pos[1]-alien_pos[1])**2)
                
                if distance < 40:
                    player_pos = self.shooter_player.rect.center
                    alien_distance = math.sqrt((player_pos[0]-alien_pos[0])**2 + (player_pos[1]-alien_pos[1])**2)
                    
                    if alien_distance < 100:
                        self.shooter_player.score += 10
                    elif alien_distance < 200:
                        self.shooter_player.score += 5
                    else:
                        self.shooter_player.score += 2
                    
                    self.aliens.remove(alien)
                    self.bullets.remove(bullet)
                    break
        
        if self.shooter_player.score >= 80:
            boss_warning = self.font.render("BOSS SAVAŞI GELİYEAHH", True, (255, 0, 0))
            screen.blit(boss_warning, (SCREEN_WIDTH//2 - 150, 50))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    _, _, angle = self.shooter_player.update_gun(mouse_pos)
                    gun_x = self.shooter_player.rect.centerx + math.cos(angle) * self.shooter_player.gun_offset
                    gun_y = self.shooter_player.rect.centery + math.sin(angle) * self.shooter_player.gun_offset
                    self.bullets.append(Bullet((gun_x, gun_y), angle))
                    shoot_sound.play()

    def run_boss_fight(self):
        mouse_pos = pygame.mouse.get_pos()
        
        self.boss.update()
        
        self.boss.wave_timer += 1
        if self.boss.wave_timer >= self.boss.wave_delay:
            new_aliens = self.boss.spawn_alien_wave()
            self.boss_aliens.extend(new_aliens)
            self.boss.wave_timer = 0
        
        for bullet in self.boss.alien_bullets[:]:
            bullet['x'] += bullet['vx']
            bullet['y'] += bullet['vy']
            
            bullet_rect = pygame.Rect(bullet['x'] - bullet['radius'], bullet['y'] - bullet['radius'], 
                                    bullet['radius'] * 2, bullet['radius'] * 2)
            if bullet_rect.colliderect(self.shooter_player.rect):
                self.shooter_player.score -= 10
                self.boss.alien_bullets.remove(bullet)
                if self.shooter_player.score <= 0:
                    self.state = "dead"
                continue
            
            if (bullet['x'] < 0 or bullet['x'] > SCREEN_WIDTH or 
                bullet['y'] < 0 or bullet['y'] > SCREEN_HEIGHT):
                self.boss.alien_bullets.remove(bullet)
        
        for alien in self.boss_aliens[:]:
            alien.update()
            
            if alien.rect.colliderect(self.shooter_player.rect):
                self.shooter_player.score -= 10
                self.boss_aliens.remove(alien)
                if self.shooter_player.score <= 0:
                    self.state = "dead"
        
        for bullet in self.bullets[:]:
            bullet.update()
            
            if self.boss and math.sqrt((bullet.x - self.boss.rect.centerx)**2 + (bullet.y - self.boss.rect.centery)**2) < 150:
                self.boss.health -= 5
                self.bullets.remove(bullet)
                if self.boss.health <= 0:
                    self.state = "win"
                continue
            
            for alien_bullet in self.boss.alien_bullets[:]:
                distance = math.sqrt((bullet.x - alien_bullet['x'])**2 + (bullet.y - alien_bullet['y'])**2)
                if distance < 20:
                    self.boss.alien_bullets.remove(alien_bullet)
                    self.bullets.remove(bullet)
                    break
            
            for alien in self.boss_aliens[:]:
                distance = math.sqrt((bullet.x - alien.rect.centerx)**2 + (bullet.y - alien.rect.centery)**2)
                if distance < 40:
                    self.boss_aliens.remove(alien)
                    self.bullets.remove(bullet)
                    self.shooter_player.score += 5
                    break
            
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
        
        self.shooter_player.draw(screen, mouse_pos)
        self.boss.draw(screen)
        
        for alien in self.boss_aliens:
            alien.draw(screen)
        
        for bullet in self.bullets:
            bullet.draw(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    _, _, angle = self.shooter_player.update_gun(mouse_pos)
                    gun_x = self.shooter_player.rect.centerx + math.cos(angle) * self.shooter_player.gun_offset
                    gun_y = self.shooter_player.rect.centery + math.sin(angle) * self.shooter_player.gun_offset
                    self.bullets.append(Bullet((gun_x, gun_y), angle))
                    shoot_sound.play()

    def run_dead(self):
        screen.fill((30, 0, 0))
        txt = self.font_large.render("KAYBETTİN", True, (255, 0, 0))
        score_text = self.font_large.render(f"Final skor: {self.shooter_player.score if self.shooter_player else 0}", True, (255, 255, 255))
        restart = self.font_small.render("ENTER tuşu ile yeniden dene!", True, (255, 255, 255))
        
        screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2, 200)))
        screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH//2, 300)))
        screen.blit(restart, restart.get_rect(center=(SCREEN_WIDTH//2, 400)))
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.__init__()
                pygame.mixer.music.play(-1)

    def run_win(self):
        screen.fill((0, 30, 0))
        txt = self.font_large.render("KAZANDIN!", True, (0, 255, 0))
        score_text = self.font_large.render(f"Final Skor: {self.shooter_player.score}", True, (255, 255, 255))
        restart = self.font_small.render("ENTER tuşu ile yeniden oyna!", True, (255, 255, 255))
        
        screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2, 200)))
        screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH//2, 300)))
        screen.blit(restart, restart.get_rect(center=(SCREEN_WIDTH//2, 400)))
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.__init__()
                pygame.mixer.music.play(-1)

    def loop(self):
        while True:
            if self.state == "menu":
                self.run_menu()
            elif self.state == "play":
                self.run_play()
            elif self.state == "dialogue":
                self.run_dialogue()
            elif self.state == "shooter":
                self.run_shooter()
            elif self.state == "dead":
                self.run_dead()
            elif self.state == "win":
                self.run_win()

            clock.tick(FPS)

if __name__ == "__main__":
    Game().loop()