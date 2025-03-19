import pgzrun
import random
from pygame import Rect

# Configurações da janela
WIDTH = 1200
HEIGHT = 600
TITLE = "Platformer Game"

# Gravidade e movimento
GRAVITY = 0.4
VELOCIDADE_PULO = -10
VELOCIDADE_MOVIMENTO = 150  # Pixels por segundo
ANIMACAO_INTERVALO = 0.2  # Segundos entre cada frame de animação

# Estados do jogo
MENU = 0
JOGANDO = 1
estado = MENU
tempo_ataque = 0

# Sprites
heroi = Actor('adventurer/adventurer_idle', (WIDTH // 2, HEIGHT - 100))
heroi.velocidade_y = 0
heroi.no_chao = False
heroi.ultima_animacao_tempo = 0
heroi.frame_animacao = 0
heroi.socando = False  # Estado de soco
heroi.direcao = 1  # 1 para direita, -1 para esquerda
heroi_agarrado = False
inimigos = []
sprites_heroi_idle_direita = ['adventurer/adventurer_idle', 'adventurer/adventurer_stand']
sprites_heroi_idle_esquerda = ['adventurer/adventurer_idle_left', 'adventurer/adventurer_stand_left']
sprites_heroi_mover_direita = ['adventurer/adventurer_walk1', 'adventurer/adventurer_walk2']
sprites_heroi_mover_esquerda = ['adventurer/adventurer_walk1_left', 'adventurer/adventurer_walk2_left']
sprites_heroi_pulo_direita = ['adventurer/adventurer_jump']
sprites_heroi_pulo_esquerda = ['adventurer/adventurer_jump_left']
sprites_heroi_soco_direita = ['adventurer/adventurer_action2', 'adventurer/adventurer_action2']
sprites_heroi_soco_esquerda = ['adventurer/adventurer_action2_left', 'adventurer/adventurer_action2_left']
sprites_heroi_hurt = ['adventurer/adventurer_hurt']  # Sprite de herói ferido (direita)
sprites_heroi_hurt_esquerda = ['adventurer/adventurer_hurt_left']  # Sprite de herói ferido (esquerda)

# Sprites dos zumbis
sprites_inimigo_idle_direita = ['zombie/zombie_idle', 'zombie/zombie_stand']
sprites_inimigo_idle_esquerda = ['zombie/zombie_idle_left', 'zombie/zombie_stand_left']
sprites_inimigo_mover_direita = ['zombie/zombie_walk1', 'zombie/zombie_walk2']
sprites_inimigo_mover_esquerda = ['zombie/zombie_walk1_left', 'zombie/zombie_walk2_left']
sprites_inimigo_ferido = ['zombie/zombie_hurt']
sprites_inimigo_hold_direita = ['zombie/zombie_hold1']
sprites_inimigo_hold_esquerda = ['zombie/zombie_hold1_left']

# Plataformas
PLATAFORMAS = [
    Rect(0, HEIGHT - 40, WIDTH, 40),  # Chão
    Rect(180, HEIGHT - 250, 200, 20),  # Plataforma 1
    Rect(500, HEIGHT - 150, 200, 20),  # Plataforma 2
    Rect(820, HEIGHT - 250, 200, 20),  # Plataforma 3
]

# Música e sons
musica_ligada = True
som_ligado = True

def draw():
    screen.clear()
    if estado == MENU:
        desenhar_menu()
    elif estado == JOGANDO:
        desenhar_jogo()

def desenhar_menu():
    screen.draw.text("Platformer Game", center=(WIDTH // 2, HEIGHT // 4), fontsize=60, color="white")
    screen.draw.text("1. Começar o jogo", center=(WIDTH // 2, HEIGHT // 2), fontsize=40, color="white")
    screen.draw.text("2. Música: " + ("Ligada" if musica_ligada else "Desligada"), center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=40, color="white")
    screen.draw.text("3. Sair", center=(WIDTH // 2, HEIGHT // 2 + 100), fontsize=40, color="white")

def desenhar_jogo():
    for plataforma in PLATAFORMAS:
        screen.draw.filled_rect(plataforma, (100, 100, 100))
    heroi.draw()
    for inimigo in inimigos:
        inimigo.draw()

def update(dt):
    global estado
    if estado == JOGANDO:
        atualizar_jogo(dt)

def atualizar_jogo(dt):
    atualizar_heroi(dt)
    atualizar_inimigos(dt)

def atualizar_heroi(dt):
    global estado
    if estado != JOGANDO or heroi_agarrado:  # Não atualizar o herói se o jogo não estiver em andamento ou se ele estiver agarrado
        return

    # Lógica normal de movimento do herói
    if keyboard.left:
        heroi.x -= VELOCIDADE_MOVIMENTO * dt
        heroi.direcao = -1  # Definir direção para esquerda
        if heroi.no_chao and not heroi.socando:
            animar_heroi(sprites_heroi_mover_esquerda, dt)
    elif keyboard.right:
        heroi.x += VELOCIDADE_MOVIMENTO * dt
        heroi.direcao = 1  # Definir direção para direita
        if heroi.no_chao and not heroi.socando:
            animar_heroi(sprites_heroi_mover_direita, dt)
    elif heroi.no_chao and not heroi.socando:
        if heroi.direcao == -1:
            animar_heroi(sprites_heroi_idle_esquerda, dt)
        else:
            animar_heroi(sprites_heroi_idle_direita, dt)

    # Gravidade e pulo
    heroi.velocidade_y += GRAVITY
    heroi.y += heroi.velocidade_y

    # Verificar colisão com plataformas
    heroi.no_chao = False
    for plataforma in PLATAFORMAS:
        if heroi.colliderect(plataforma) and heroi.velocidade_y > 0:
            heroi.velocidade_y = 0
            heroi.bottom = plataforma.top
            heroi.no_chao = True

    # Pulo
    if keyboard.up and heroi.no_chao:
        heroi.velocidade_y = VELOCIDADE_PULO
        if heroi.direcao == -1:
            heroi.image = sprites_heroi_pulo_esquerda[0]
        else:
            heroi.image = sprites_heroi_pulo_direita[0]

    # Atualizar animação de soco
    if heroi.socando:
        animar_soco(dt)

def animar_heroi(sprites, dt):
    heroi.ultima_animacao_tempo += dt
    if heroi.ultima_animacao_tempo >= ANIMACAO_INTERVALO:
        heroi.ultima_animacao_tempo = 0
        heroi.frame_animacao = (heroi.frame_animacao + 1) % len(sprites)
        heroi.image = sprites[heroi.frame_animacao]

def animar_soco(dt):
    global inimigos
    heroi.ultima_animacao_tempo += dt
    if heroi.ultima_animacao_tempo >= ANIMACAO_INTERVALO:
        heroi.ultima_animacao_tempo = 0
        heroi.frame_animacao += 1
        if heroi.frame_animacao < len(sprites_heroi_soco_direita):
            # Escolher o sprite de soco com base na direção do herói
            if heroi.direcao == -1:
                heroi.image = sprites_heroi_soco_esquerda[heroi.frame_animacao]
            else:
                heroi.image = sprites_heroi_soco_direita[heroi.frame_animacao]

            # Verificar colisão com zumbis durante o soco
            for inimigo in inimigos:
                if heroi.colliderect(inimigo):
                    inimigo.image = sprites_inimigo_ferido[0]  # Mudar para sprite de zumbi ferido
                    inimigo.estado = "ferido"  # Atualizar estado do zumbi
                    inimigo.tempo_ferido = 0  # Iniciar contador de tempo para desaparecer
        else:
            # Finalizar a animação de soco
            heroi.socando = False
            heroi.frame_animacao = 0
            # Voltar para a animação de idle com base na direção
            if heroi.direcao == -1:
                heroi.image = sprites_heroi_idle_esquerda[0]
            else:
                heroi.image = sprites_heroi_idle_direita[0]

def atualizar_inimigos(dt):
    global inimigos, estado, tempo_ataque, heroi_agarrado
    for inimigo in inimigos[:]:  # Usar uma cópia da lista para evitar problemas ao remover itens
        if inimigo.estado == "ferido":
            # Lógica para zumbi ferido (já implementada)
            inimigo.tempo_ferido += dt
            if inimigo.tempo_ferido >= 1.0:
                inimigos.remove(inimigo)
        elif inimigo.estado == "hold":
            # Lógica para zumbi agarrando o herói
            if inimigo.direcao == -1:
                inimigo.image = sprites_inimigo_hold_esquerda[0]
            else:
                inimigo.image = sprites_inimigo_hold_direita[0]

            # Mudar o sprite do herói para "hurt" com base na direção do zumbi
            if inimigo.direcao == -1:
                heroi.image = sprites_heroi_hurt[0]  # Herói ferido para a direita
            else:
                heroi.image = sprites_heroi_hurt_esquerda[0]  # Herói ferido para a esquerda

            # Iniciar o contador de tempo de ataque
            tempo_ataque += dt
            if tempo_ataque >= 3.0:  # Esperar 3 segundos
                reiniciar_jogo()  # Reiniciar o jogo
                return  # Sair da função para evitar atualizações adicionais
        else:
            # Lógica normal de movimento do zumbi
            inimigo.tempo_estado += dt
            if inimigo.tempo_estado >= 5:
                inimigo.tempo_estado = 0
                inimigo.estado = "parado" if inimigo.estado == "movendo" else "movendo"

            if inimigo.estado == "movendo":
                inimigo.x += inimigo.direcao * VELOCIDADE_MOVIMENTO * dt
                if inimigo.right > WIDTH:
                    inimigo.right = WIDTH
                    inimigo.direcao *= -1
                elif inimigo.left < 0:
                    inimigo.left = 0
                    inimigo.direcao *= -1
                if inimigo.direcao == -1:
                    animar_inimigo(inimigo, sprites_inimigo_mover_esquerda, dt)
                else:
                    animar_inimigo(inimigo, sprites_inimigo_mover_direita, dt)
            else:
                if inimigo.direcao == -1:
                    animar_inimigo(inimigo, sprites_inimigo_idle_esquerda, dt)
                else:
                    animar_inimigo(inimigo, sprites_inimigo_idle_direita, dt)

            # Verificar se o herói está próximo o suficiente para ser agarrado
            if not heroi_agarrado and abs(heroi.x - inimigo.x) < 50 and abs(heroi.y - inimigo.y) < 50:
                inimigo.estado = "hold"  # Mudar para estado de "hold"
                inimigo.direcao = 1 if heroi.x > inimigo.x else -1  # Direção do zumbi ao agarrar
                heroi_agarrado = True  # Marcar o herói como agarrado
                tempo_ataque = 0  # Reiniciar o contador de tempo de ataque

def animar_inimigo(inimigo, sprites, dt):
    inimigo.ultima_animacao_tempo += dt
    if inimigo.ultima_animacao_tempo >= ANIMACAO_INTERVALO:
        inimigo.ultima_animacao_tempo = 0
        inimigo.frame_animacao = (inimigo.frame_animacao + 1) % len(sprites)
        inimigo.image = sprites[inimigo.frame_animacao]

def on_key_down(key):
    global estado, musica_ligada
    if estado == MENU:
        if key == keys.K_1:
            estado = JOGANDO
            iniciar_jogo()
        elif key == keys.K_2:
            musica_ligada = not musica_ligada
            if musica_ligada:
                music.play('background_music')
            else:
                music.stop()
        elif key == keys.K_3:
            quit()
    elif estado == JOGANDO:
        if key == keys.SPACE and not heroi.socando:
            heroi.socando = True
            heroi.frame_animacao = 0  # Reiniciar a animação de soco

def iniciar_jogo():
    global heroi, inimigos
    heroi.pos = (WIDTH // 2, HEIGHT - 100)
    heroi.velocidade_y = 0
    heroi.ultima_animacao_tempo = 0
    heroi.frame_animacao = 0
    heroi.socando = False
    heroi.direcao = 1  # Começar virado para a direita
    # Posicionar zumbis sobre o chão
    inimigos = [Actor('zombie/zombie_idle', (random.randint(0, WIDTH), HEIGHT - 70 - 20)) for _ in range(2)]
    for inimigo in inimigos:
        inimigo.direcao = random.choice([-1, 1])  # Direção inicial do inimigo
        inimigo.ultima_animacao_tempo = 0
        inimigo.frame_animacao = 0
        inimigo.estado = "movendo"  # Estado inicial: movendo
        inimigo.tempo_estado = 0  # Contador de tempo para alternar estados
        inimigo.tempo_ferido = 0  # Contador de tempo para desaparecer quando ferido
    if musica_ligada:
        music.play('background_music')

def reiniciar_jogo():
    global estado, tempo_ataque, heroi, inimigos, heroi_agarrado
    estado = JOGANDO  # Voltar ao estado de jogo
    tempo_ataque = 0  # Reiniciar o contador de tempo de ataque
    heroi_agarrado = False  # Reiniciar o estado do herói
    iniciar_jogo()  # Reiniciar o jogo

# Iniciar o jogo
pgzrun.go()