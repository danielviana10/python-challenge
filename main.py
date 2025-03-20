import pgzrun
import random
from pygame import Rect

# Configurações da janela
WIDTH = 1000
HEIGHT = 600

# Gravidade e movimento
GRAVITY = 0.4
JUMP_VELOCITY = -10
MOVE_VELOCITY = 150
ANIMATION_INTERVAL = 0.2

# Estados do jogo
MENU = 0
PLAYING = 1
state = MENU
selected_option = 0
attack_time = 0
show_mission = True
mission_time = 0
victory = False
defeat = False

menu_options = ["Start Game", "Music: On", "Quit"]
hovered_option = None 

# Plataformas
PLATFORMS = [
    Rect(0, HEIGHT - 40, WIDTH, 40),  # Chão
    Rect(100, HEIGHT - 300, 200, 10),  # Plataforma 1
    Rect(380, HEIGHT - 180, 200, 10),  # Plataforma 2
    Rect(650, HEIGHT - 300, 200, 10),  # Plataforma 3
]

# Carregar o tile
TILE = "tiles/tundrahalf"
TILE_WIDTH = 40
TILE_HEIGHT = 40 

background = Actor("winter")
background_menu = Actor("zombiesurvival")

# Ajustar o tamanho da imagem de fundo para cobrir toda a tela
background.width = WIDTH 
background.height = HEIGHT

# Música e sons
music_on = True
sound_on = True


# Classe para o Herói
class Hero:
    def __init__(self, x, y):
        self.actor = Actor('adventurer/adventurer_idle', (x, y))
        self.velocity_y = 0
        self.on_ground = False
        self.last_animation_time = 0
        self.animation_frame = 0
        self.punching = False
        self.direction = 1
        self.grabbed = False
        self.crouching = False

        # Sprites do herói
        self.idle_right_sprites = ['adventurer/adventurer_idle', 'adventurer/adventurer_stand']
        self.idle_left_sprites = ['adventurer/adventurer_idle_left', 'adventurer/adventurer_stand_left']
        self.move_right_sprites = ['adventurer/adventurer_walk1', 'adventurer/adventurer_walk2']
        self.move_left_sprites = ['adventurer/adventurer_walk1_left', 'adventurer/adventurer_walk2_left']
        self.jump_right_sprites = ['adventurer/adventurer_jump']
        self.jump_left_sprites = ['adventurer/adventurer_jump_left']
        self.punch_right_sprites = ['adventurer/adventurer_action2', 'adventurer/adventurer_action2']
        self.punch_left_sprites = ['adventurer/adventurer_action2_left', 'adventurer/adventurer_action2_left']
        self.hurt_sprites = ['adventurer/adventurer_hurt']
        self.hurt_left_sprites = ['adventurer/adventurer_hurt_left']
        self.crouch_right_sprites = ['adventurer/adventurer_duck']
        self.crouch_left_sprites = ['adventurer/adventurer_duck_left']

    def update(self, dt):
        if state != PLAYING or self.grabbed:
            return

        # Agachar
        if keyboard.down:
            self.crouching = True
            if self.direction == -1:
                self.actor.image = self.crouch_left_sprites[0]
            else:
                self.actor.image = self.crouch_right_sprites[0]
        else:
            self.crouching = False

        # Movimento horizontal
        if keyboard.left and not self.crouching:
            self.actor.x -= MOVE_VELOCITY * dt
            self.direction = -1
            if self.on_ground and not self.punching:
                self.animate(self.move_left_sprites, dt)
        elif keyboard.right and not self.crouching:
            self.actor.x += MOVE_VELOCITY * dt
            self.direction = 1
            if self.on_ground and not self.punching:
                self.animate(self.move_right_sprites, dt)
        elif self.on_ground and not self.punching and not self.crouching:
            if self.direction == -1:
                self.animate(self.idle_left_sprites, dt)
            else:
                self.animate(self.idle_right_sprites, dt)

        # Gravidade e pulo
        self.velocity_y += GRAVITY
        self.actor.y += self.velocity_y

        # Verificar colisão com plataformas
        self.on_ground = False
        for platform in PLATFORMS:
            if self.actor.colliderect(platform) and self.velocity_y > 0:
                self.velocity_y = 0
                self.actor.bottom = platform.top
                self.on_ground = True

        # Pulo
        if keyboard.up and self.on_ground and not self.crouching:
            self.velocity_y = JUMP_VELOCITY
            if self.direction == -1:
                self.actor.image = self.jump_left_sprites[0]
            else:
                self.actor.image = self.jump_right_sprites[0]

        # Atualizar animação de soco
        if self.punching:
            self.animate_punch(dt)

    def animate(self, sprites, dt):
        self.last_animation_time += dt
        if self.last_animation_time >= ANIMATION_INTERVAL:
            self.last_animation_time = 0
            self.animation_frame = (self.animation_frame + 1) % len(sprites)
            self.actor.image = sprites[self.animation_frame]

    def animate_punch(self, dt):
        global enemies
        self.last_animation_time += dt
        if self.last_animation_time >= ANIMATION_INTERVAL:
            self.last_animation_time = 0
            self.animation_frame += 1
            if self.animation_frame < len(self.punch_right_sprites):
                if self.direction == -1:
                    self.actor.image = self.punch_left_sprites[self.animation_frame]
                else:
                    self.actor.image = self.punch_right_sprites[self.animation_frame]

                # Verificar colisão com inimigos
                for enemy in enemies:
                    if self.actor.colliderect(enemy.actor):
                        enemy.hurt()
            else:
                self.punching = False
                self.animation_frame = 0
                if self.direction == -1:
                    self.actor.image = self.idle_left_sprites[0]
                else:
                    self.actor.image = self.idle_right_sprites[0]


# Classe para os Inimigos
class Enemy:
    def __init__(self, x, y):
        self.actor = Actor('zombie/zombie_idle', (x, y))
        self.direction = random.choice([-1, 1])
        self.last_animation_time = 0
        self.animation_frame = 0
        self.state = "moving"
        self.state_time = 0
        self.hurt_time = 0

        # Sprites do inimigo
        self.idle_right_sprites = ['zombie/zombie_idle', 'zombie/zombie_stand']
        self.idle_left_sprites = ['zombie/zombie_idle_left', 'zombie/zombie_stand_left']
        self.move_right_sprites = ['zombie/zombie_walk1', 'zombie/zombie_walk2']
        self.move_left_sprites = ['zombie/zombie_walk1_left', 'zombie/zombie_walk2_left']
        self.hurt_right_sprites = ['zombie/zombie_hurt']
        self.hurt_left_sprites = ['zombie/zombie_hurt_left']
        self.hold_right_sprites = ['zombie/zombie_hold1']
        self.hold_left_sprites = ['zombie/zombie_hold1_left']

    def update(self, dt):
        if self.state == "hurt":
            self.hurt_time += dt
            if self.hurt_time >= 1.0:
                enemies.remove(self)
        elif self.state == "hold":
            if self.direction == -1:
                self.actor.image = self.hold_left_sprites[0]
            else:
                self.actor.image = self.hold_right_sprites[0]

            # Manter o herói agarrado
            if hero.grabbed:
                hero.actor.x = self.actor.x + (20 if self.direction == 1 else -20)
                hero.actor.y = self.actor.y
                if self.direction == -1:
                    hero.actor.image = hero.hurt_left_sprites[0]
                else:
                    hero.actor.image = hero.hurt_sprites[0]
        else:
            self.state_time += dt
            if self.state_time >= 5:
                self.state_time = 0
                self.state = "idle" if self.state == "moving" else "moving"

            if self.state == "moving":
                self.actor.x += self.direction * MOVE_VELOCITY * dt
                if self.actor.right > WIDTH:
                    self.actor.right = WIDTH
                    self.direction *= -1
                elif self.actor.left < 0:
                    self.actor.left = 0
                    self.direction *= -1
                if self.direction == -1:
                    self.animate(self.move_left_sprites, dt)
                else:
                    self.animate(self.move_right_sprites, dt)
            else:
                if self.direction == -1:
                    self.animate(self.idle_left_sprites, dt)
                else:
                    self.animate(self.idle_right_sprites, dt)

            # Verificar se o herói está próximo o suficiente para ser agarrado
            if not hero.grabbed and abs(hero.actor.x - self.actor.x) < 50 and abs(hero.actor.y - self.actor.y) < 50:
                if not hero.crouching:  # Só capturar se o herói não estiver agachado
                    self.state = "hold"  # Mudar para estado de "hold"
                    self.direction = 1 if hero.actor.x > self.actor.x else -1  # Direção do zumbi ao agarrar
                    hero.grabbed = True  # Marcar o herói como agarrado
                    global attack_time
                    attack_time = 0  # Reiniciar o contador de tempo de ataque

    def animate(self, sprites, dt):
        self.last_animation_time += dt
        if self.last_animation_time >= ANIMATION_INTERVAL:
            self.last_animation_time = 0
            self.animation_frame = (self.animation_frame + 1) % len(sprites)
            self.actor.image = sprites[self.animation_frame]

    def hurt(self):
        if self.direction == -1:
            self.actor.image = self.hurt_left_sprites[0]
        else:
            self.actor.image = self.hurt_right_sprites[0]
        self.state = "hurt"
        self.hurt_time = 0


# Instâncias do herói e inimigos
hero = Hero(WIDTH // 2, HEIGHT - 100)
enemies = []


def draw():
    screen.clear()
    background.draw() 

    if state == MENU:
        draw_menu()
    elif state == PLAYING:
        if defeat:
            draw_defeat()
        elif victory:  # Verificar se o jogador venceu
            draw_victory()
        elif show_mission:
            draw_mission()
        else:
            draw_game()


def draw_menu():
    screen.clear()
    background_menu.draw()
    # Desenhar as opções do menu
    for i, option in enumerate(menu_options):
        # Verificar se o mouse está sobre a opção
        if hovered_option == i:
            color = "yellow"  # Cor de hover
        else:
            color = "white"  # Cor normal

        # Desenhar o texto da opção
        screen.draw.text(option, center=(WIDTH // 2, HEIGHT // 2 + i * 50), fontsize=40, color=color)

def on_mouse_down(pos):
    global state, music_on, hovered_option

    if state == MENU:
        # Verificar em qual opção o jogador clicou
        for i, option in enumerate(menu_options):
            # Calcular a área clicável da opção
            option_rect = Rect(WIDTH // 2 - 100, HEIGHT // 2 + i * 50 - 20, 200, 40)
            if option_rect.collidepoint(pos):
                if i == 0:  # Start Game
                    state = PLAYING
                    start_game()
                elif i == 1:  # Toggle Music
                    music_on = not music_on
                    menu_options[1] = "Music: On" if music_on else "Music: Off"
                    if music_on:
                        music.play('background_music')
                    else:
                        music.stop()
                elif i == 2:  # Quit
                    quit()


def on_mouse_move(pos):
    global hovered_option

    if state == MENU:
        # Verificar se o mouse está sobre alguma opção
        hovered_option = None
        for i, option in enumerate(menu_options):
            # Calcular a área clicável da opção
            option_rect = Rect(WIDTH // 2 - 100, HEIGHT // 2 + i * 50 - 20, 200, 40)
            if option_rect.collidepoint(pos):
                hovered_option = i
                break


def draw_mission():
    # Mensagem da missão
    screen.draw.text(
        "Mission: Defeat the zombies and don't get caught",
        center=(WIDTH // 2, HEIGHT // 2 - 80),
        fontsize=40,
        color="white"
    )

    # Instruções de controle
    instructions = [
        "(Up) Jump",
        "(Down) Crouch",
        "(Left) Move left",
        "(Right) Move right",
        "(SPACE) Punch"
    ]

    # Desenhar as instruções
    for i, instruction in enumerate(instructions):
        screen.draw.text(
            instruction,
            center=(WIDTH // 2, HEIGHT // 2 + i * 30 - 20),
            fontsize=30,
            color="white"
        )

    # Mensagem "Press SPACE to continue"
    screen.draw.text(
        "Press SPACE to continue",
        center=(WIDTH // 2, HEIGHT // 2 + 150),
        fontsize=30,
        color="yellow"
    )


def draw_game():
    # Desenhar as plataformas com tiles
    for platform in PLATFORMS:
        # Calcular quantos tiles são necessários para preencher a plataforma
        num_tiles = int(platform.width / TILE_WIDTH)
        for i in range(num_tiles):
            screen.blit(
                TILE,
                (platform.x + i * TILE_WIDTH, platform.y)
            )

    # Desenhar o herói e os inimigos
    hero.actor.draw()
    for enemy in enemies:
        enemy.actor.draw()


def update(dt):
    global state, show_mission, mission_time, victory, defeat, attack_time

    if state == PLAYING:
        if defeat:
            if keyboard.SPACE:
                restart_game()
        elif victory:
            if keyboard.SPACE:
                restart_game()
        elif show_mission:
            mission_time += dt
            if keyboard.SPACE:
                show_mission = False
        else:
            update_game(dt)

            # Verificar se o herói está sendo agarrado
            if hero.grabbed:
                attack_time += dt
                if attack_time >= 3.0:
                    defeat = True


def update_game(dt):
    hero.update(dt)
    for enemy in enemies[:]:
        enemy.update(dt)

    # Verificar se todos os inimigos foram eliminados
    if not enemies:
        global victory
        victory = True


def on_key_down(key):
    global state, show_mission

    if state == PLAYING:
        if key == keys.SPACE and not hero.punching:
            hero.punching = True
            hero.animation_frame = 0
        elif key == keys.ESCAPE:  # Voltar ao menu
            state = MENU
            show_mission = False
            if music_on:
                music.play('background_music')
            else:
                music.stop()


def start_game():
    global hero, enemies, show_mission, mission_time
    hero.actor.pos = (WIDTH // 2, HEIGHT - 200)
    hero.velocity_y = 0
    hero.last_animation_time = 0
    hero.animation_frame = 0
    hero.punching = False
    hero.direction = 1
    hero.grabbed = False
    enemies = [Enemy(random.randint(0, WIDTH), HEIGHT - 74 - 20) for _ in range(2)]
    if music_on:
        music.play('background_music')

    # Mostrar a tela de missão apenas ao iniciar o jogo, não ao voltar ao menu
    if state == PLAYING:
        show_mission = True
    mission_time = 0


def restart_game():
    global state, attack_time, hero, enemies, victory, defeat, show_mission
    state = PLAYING
    attack_time = 0
    hero.grabbed = False
    victory = False
    defeat = False
    show_mission = False
    start_game()


def draw_victory():
    screen.draw.text(
        "You Win!",
        center=(WIDTH // 2, HEIGHT // 2 - 50),
        fontsize=60,
        color="green"
    )
    screen.draw.text(
        "Press SPACE to restart",
        center=(WIDTH // 2, HEIGHT // 2 + 50),
        fontsize=40,
        color="yellow"
    )


def draw_defeat():
    screen.draw.text(
        "You Lose!",
        center=(WIDTH // 2, HEIGHT // 2 - 100),
        fontsize=60,
        color="red"
    )
    screen.draw.text(
        "Press SPACE to try again",
        center=(WIDTH // 2, HEIGHT // 2 + 30),
        fontsize=40,
        color="yellow"
    )

    screen.draw.text(
        "Tip: If you crounch down, the zombies won't get you",
        center=(WIDTH // 2, HEIGHT // 2 + 100),
        fontsize=30,
        color="yellow"
    )


# Iniciar o jogo
pgzrun.go()