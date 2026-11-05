import pygame
import random
import sys

# ============================================================
# CAMINHO SEGURO - Jogo educativo sobre seguranca no transito
# Controles: setas do teclado | ENTER inicia/reinicia | ESC sai
# ============================================================

pygame.init()

LARGURA = 900
ALTURA = 650
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Caminho Seguro")

RELOGIO = pygame.time.Clock()
FPS = 60

# Cores
VERDE = (65, 150, 85)
VERDE_ESCURO = (35, 105, 55)
CINZA = (65, 68, 75)
CINZA_CLARO = (105, 108, 115)
BRANCO = (245, 245, 245)
PRETO = (25, 25, 25)
AMARELO = (250, 210, 55)
VERMELHO = (220, 55, 55)
AZUL = (55, 130, 220)
AZUL_ESCURO = (35, 75, 145)
MARROM = (130, 85, 50)

FONTE = pygame.font.SysFont("arial", 25)
FONTE_PEQUENA = pygame.font.SysFont("arial", 18)
FONTE_TITULO = pygame.font.SysFont("arial", 54, bold=True)
FONTE_SUBTITULO = pygame.font.SysFont("arial", 34, bold=True)

# Areas do cenario
CALCADA_SUPERIOR = pygame.Rect(0, 75, LARGURA, 125)
PISTA = pygame.Rect(0, 200, LARGURA, 300)
CALCADA_INFERIOR = pygame.Rect(0, 500, LARGURA, 125)
FAIXA = pygame.Rect(385, 200, 130, 300)
AREA_ESCOLA = pygame.Rect(330, 85, 240, 90)

# Jogador
TAMANHO_JOGADOR = 30
VELOCIDADE_JOGADOR = 4

# Configuracoes das tres fases
CONFIG_FASES = {
    1: {"multiplicador": 1.0, "duracao_sinal": 5000, "quantidade_carros": 4},
    2: {"multiplicador": 1.3, "duracao_sinal": 4000, "quantidade_carros": 5},
    3: {"multiplicador": 1.6, "duracao_sinal": 3000, "quantidade_carros": 6}
}

estado = "inicio"
pontuacao = 0
vidas = 3
fase_atual = 1
jogador = pygame.Rect(435, 535, TAMANHO_JOGADOR, TAMANHO_JOGADOR)
carros = []
tempo_sinal = 0
sinal_verde = False
mensagem = "Use as setas para se movimentar."
cor_mensagem = BRANCO
tempo_mensagem = 0
entrou_na_pista = False
travessia_segura = False
penalidade_aplicada = False
ultimo_tempo = 0


def desenhar_texto(texto, fonte, cor, x, y, centralizado=True):
    imagem = fonte.render(texto, True, cor)
    retangulo = imagem.get_rect()
    if centralizado:
        retangulo.center = (x, y)
    else:
        retangulo.topleft = (x, y)
    TELA.blit(imagem, retangulo)


def mostrar_mensagem(texto, cor=BRANCO, duracao=2200):
    global mensagem, cor_mensagem, tempo_mensagem
    mensagem = texto
    cor_mensagem = cor
    tempo_mensagem = pygame.time.get_ticks() + duracao


def criar_carros():
    global carros

    carros = []
    configuracao = CONFIG_FASES[fase_atual]

    # Distribui os carros pelas faixas da pista
    faixas_y = [220, 280, 340, 400, 460, 250]
    cores_carros = [VERMELHO, AZUL, AMARELO, (235, 235, 235), (30, 170, 170)]

    for i in range(configuracao["quantidade_carros"]):
        y = faixas_y[i]
        sentido = 1 if i % 2 == 0 else -1
        x = random.randint(-650, 850)
        largura = random.randint(65, 90)
        velocidade_base = random.uniform(2.0, 3.4)
        velocidade = velocidade_base * configuracao["multiplicador"]

        carros.append({
            "rect": pygame.Rect(x, y, largura, 38),
            "sentido": sentido,
            "velocidade": velocidade,
            "cor": random.choice(cores_carros)
        })


def reiniciar_travessia():
    """Reposiciona o jogador e limpa os dados da travessia atual."""
    global jogador, entrou_na_pista, travessia_segura, penalidade_aplicada

    jogador = pygame.Rect(435, 535, TAMANHO_JOGADOR, TAMANHO_JOGADOR)
    entrou_na_pista = False
    travessia_segura = False
    penalidade_aplicada = False


def reiniciar_jogo():
    global pontuacao, vidas, tempo_sinal, sinal_verde
    global estado, ultimo_tempo, fase_atual

    pontuacao = 0
    vidas = 3
    fase_atual = 1
    tempo_sinal = pygame.time.get_ticks()
    sinal_verde = False
    ultimo_tempo = pygame.time.get_ticks()

    reiniciar_travessia()
    criar_carros()
    mostrar_mensagem("Observe o semaforo e atravesse pela faixa!")
    estado = "jogando"


def avancar_fase():
    global fase_atual, tempo_sinal, sinal_verde

    if fase_atual < 3:
        fase_atual += 1
        reiniciar_travessia()

        # Reinicia o ciclo do semaforo ao comecar a nova fase
        tempo_sinal = pygame.time.get_ticks()
        sinal_verde = False

        # Cria os carros com a dificuldade da nova fase
        criar_carros()

        mostrar_mensagem(
            f"FASE {fase_atual}! O transito esta mais dificil!",
            AMARELO,
            3000
        )


def finalizar_travessia():
    global pontuacao, estado

    if travessia_segura:
        pontuacao += 100

        if fase_atual < 3:
            mostrar_mensagem(
                f"Travessia perfeita! +100 pontos. Preparado para a fase {fase_atual + 1}?",
                (150, 255, 150),
                2500
            )
            avancar_fase()
        else:
            pontuacao += 0
            mostrar_mensagem("Parabens! Voce concluiu as tres fases!", (150, 255, 150))
            estado = "vitoria"

    else:
        # Uma travessia perigosa nao permite avancar de fase.
        # O jogador volta ao inicio da mesma fase para tentar novamente.
        reiniciar_travessia()
        mostrar_mensagem(
            "Travessia nao foi perfeita! Tente novamente.",
            (255, 150, 100),
            2500
        )


def desenhar_cenario():
    TELA.fill(VERDE)

    # Calcadas e pista
    pygame.draw.rect(TELA, (190, 185, 165), CALCADA_SUPERIOR)
    pygame.draw.rect(TELA, (190, 185, 165), CALCADA_INFERIOR)
    pygame.draw.rect(TELA, CINZA, PISTA)

    # Bordas da pista
    pygame.draw.line(TELA, BRANCO, (0, 200), (LARGURA, 200), 5)
    pygame.draw.line(TELA, BRANCO, (0, 500), (LARGURA, 500), 5)

    # Linhas tracejadas das pistas
    for x in range(0, LARGURA, 70):
        pygame.draw.rect(TELA, AMARELO, (x, 285, 38, 5))
        pygame.draw.rect(TELA, AMARELO, (x, 375, 38, 5))

    # Faixa de pedestres
    for y in range(207, 495, 38):
        pygame.draw.rect(TELA, BRANCO, (FAIXA.x, y, FAIXA.width, 22))

    # Escola
    pygame.draw.rect(TELA, (245, 225, 175), AREA_ESCOLA, border_radius=8)
    pygame.draw.rect(TELA, MARROM, AREA_ESCOLA, 4, border_radius=8)
    pygame.draw.polygon(TELA, VERMELHO, [
        (AREA_ESCOLA.left - 12, AREA_ESCOLA.top + 5),
        (AREA_ESCOLA.centerx, AREA_ESCOLA.top - 30),
        (AREA_ESCOLA.right + 12, AREA_ESCOLA.top + 5)
    ])
    pygame.draw.rect(TELA, AZUL, (430, 125, 40, 50))
    pygame.draw.rect(TELA, MARROM, (442, 150, 16, 25))
    desenhar_texto("ESCOLA", FONTE_PEQUENA, PRETO, 450, 105)

    # Indicacoes das calcadas
    desenhar_texto("INICIO", FONTE_PEQUENA, VERDE_ESCURO, 70, 560)
    desenhar_texto("ATRAVESSE COM SEGURANCA", FONTE_PEQUENA, PRETO, 450, 610)

    # Semaforo maior na calcada inferior
    pygame.draw.rect(TELA, PRETO, (715, 500, 80, 100), border_radius=12)

    # Luz verde
    pygame.draw.circle(
        TELA,
        VERDE if sinal_verde else (35, 65, 35),
        (755, 530),
        19
    )

    # Luz vermelha
    pygame.draw.circle(
        TELA,
        (70, 30, 30) if sinal_verde else VERMELHO,
        (755, 570),
        19
    )

    # Poste
    pygame.draw.rect(TELA, PRETO, (750, 600, 10, 15))


def desenhar_texto_sinal():
    texto_sinal = "PODE" if sinal_verde else "ESPERE"
    cor_sinal = VERDE_ESCURO if sinal_verde else VERMELHO

    texto = FONTE_PEQUENA.render(texto_sinal, True, cor_sinal)
    texto_rect = texto.get_rect(center=(800, 610))

    TELA.blit(texto, texto_rect)


def desenhar_carros():
    for carro in carros:
        r = carro["rect"]
        pygame.draw.rect(TELA, carro["cor"], r, border_radius=8)
        pygame.draw.rect(TELA, (185, 220, 235), (r.x + 13, r.y + 5, r.width - 26, 12), border_radius=4)
        pygame.draw.circle(TELA, PRETO, (r.x + 17, r.bottom - 2), 7)
        pygame.draw.circle(TELA, PRETO, (r.right - 17, r.bottom - 2), 7)


def desenhar_jogador():
    # Corpo e cabeca do estudante
    pygame.draw.circle(TELA, (235, 190, 145), (jogador.centerx, jogador.y + 8), 9)
    pygame.draw.rect(TELA, AZUL_ESCURO, (jogador.x + 5, jogador.y + 16, 20, 14), border_radius=5)
    pygame.draw.line(TELA, PRETO, (jogador.x + 10, jogador.bottom), (jogador.x + 8, jogador.bottom + 5), 3)
    pygame.draw.line(TELA, PRETO, (jogador.x + 20, jogador.bottom), (jogador.x + 22, jogador.bottom + 5), 3)


def desenhar_interface():
    pygame.draw.rect(TELA, (25, 35, 50), (0, 0, LARGURA, 70))
    desenhar_texto(f"Pontuacao: {pontuacao}", FONTE, BRANCO, 25, 18, False)
    desenhar_texto(f"Vidas: {vidas}", FONTE, BRANCO, 250, 18, False)
    desenhar_texto(f"Fase: {fase_atual}/3", FONTE, AMARELO, 430, 18, False)
    desenhar_texto("Objetivo: chegar a escola", FONTE_PEQUENA, BRANCO, 590, 24, False)

    if pygame.time.get_ticks() < tempo_mensagem:
        pygame.draw.rect(TELA, (25, 35, 50), (70, 75, 760, 38), border_radius=8)
        desenhar_texto(mensagem, FONTE_PEQUENA, cor_mensagem, 450, 94)


def atualizar_sinal():
    global sinal_verde, tempo_sinal

    agora = pygame.time.get_ticks()
    duracao_sinal = CONFIG_FASES[fase_atual]["duracao_sinal"]

    if agora - tempo_sinal >= duracao_sinal:
        sinal_verde = not sinal_verde
        tempo_sinal = agora

        if sinal_verde:
            mostrar_mensagem("Sinal verde! Ainda observe os veiculos.", (150, 255, 150))
        else:
            mostrar_mensagem("Sinal vermelho! Aguarde na calcada.", (255, 150, 150))


def atualizar_carros():
    for carro in carros:
        carro["rect"].x += int(carro["velocidade"] * carro["sentido"])

        if carro["sentido"] == 1 and carro["rect"].left > LARGURA:
            carro["rect"].right = 0
        elif carro["sentido"] == -1 and carro["rect"].right < 0:
            carro["rect"].left = LARGURA


def aplicar_penalidade(texto):
    global pontuacao, penalidade_aplicada

    if not penalidade_aplicada:
        pontuacao -= 25
        mostrar_mensagem(texto, (255, 190, 90))
        penalidade_aplicada = True


def atualizar_jogador(teclas):
    global entrou_na_pista, travessia_segura

    dx = 0
    dy = 0

    if teclas[pygame.K_LEFT]:
        dx -= VELOCIDADE_JOGADOR
    if teclas[pygame.K_RIGHT]:
        dx += VELOCIDADE_JOGADOR
    if teclas[pygame.K_UP]:
        dy -= VELOCIDADE_JOGADOR
    if teclas[pygame.K_DOWN]:
        dy += VELOCIDADE_JOGADOR

    jogador.x += dx
    jogador.y += dy

    # Impede que o personagem saia pelas laterais ou do cenario
    jogador.left = max(10, jogador.left)
    jogador.right = min(LARGURA - 10, jogador.right)
    jogador.top = max(75, jogador.top)
    jogador.bottom = min(620, jogador.bottom)

    # Ao entrar na pista, verifica faixa e sinal
    if jogador.colliderect(PISTA) and not entrou_na_pista:
        entrou_na_pista = True

        esta_na_faixa = FAIXA.left <= jogador.centerx <= FAIXA.right
        travessia_segura = sinal_verde and esta_na_faixa

        if not esta_na_faixa:
            aplicar_penalidade("Use a faixa de pedestres! -25 pontos")
        elif not sinal_verde:
            aplicar_penalidade("Sinal vermelho: espere para atravessar! -25 pontos")
        else:
            mostrar_mensagem("Boa! Atravesse com atencao aos carros.", (150, 255, 150))

    # Ao chegar na calcada superior, verifica o resultado da travessia
    if entrou_na_pista and jogador.top <= 200:
        finalizar_travessia()


def verificar_colisoes():
    global vidas, estado

    for carro in carros:
        if jogador.colliderect(carro["rect"]):
            vidas -= 1
            reiniciar_travessia()
            mostrar_mensagem("Cuidado! Voce foi atingido. -1 vida", (255, 150, 150))

            if vidas <= 0:
                estado = "derrota"
            break



def desenhar_tela_inicio():
    # Fundo principal
    TELA.fill((24, 65, 55))

    # Faixas decorativas no fundo
    pygame.draw.rect(TELA, (30, 78, 65), (0, 0, LARGURA, 115))
    pygame.draw.rect(TELA, (30, 78, 65), (0, 625, LARGURA, 25))

    # Elementos decorativos de transito
    pygame.draw.rect(TELA, (45, 45, 45), (25, 0, 65, 650))
    pygame.draw.rect(TELA, (45, 45, 45), (810, 0, 65, 650))

    for y in range(20, 650, 90):
        pygame.draw.rect(TELA, AMARELO, (52, y, 10, 40), border_radius=3)
        pygame.draw.rect(TELA, AMARELO, (837, y, 10, 40), border_radius=3)

    # Titulo
    desenhar_texto(
        "CAMINHO SEGURO",
        FONTE_TITULO,
        BRANCO,
        LARGURA // 2,
        85
    )

    desenhar_texto(
        "SUA SEGURANCA VEM EM PRIMEIRO LUGAR!",
        FONTE_PEQUENA,
        (255, 220, 100),
        LARGURA // 2,
        135
    )

    # Faixa de destaque
    pygame.draw.rect(
        TELA, (245, 190, 55),
        (170, 170, 560, 5),
        border_radius=3
    )

    # Cartao principal
    pygame.draw.rect(
        TELA, (15, 45, 42),
        (125, 205, 650, 320),
        border_radius=22
    )

    pygame.draw.rect(
        TELA, (245, 245, 235),
        (132, 212, 636, 306),
        border_radius=18
    )

    # Cabecalho do cartao
    pygame.draw.rect(
        TELA, (35, 105, 85),
        (132, 212, 636, 65),
        border_radius=18
    )
    pygame.draw.rect(
        TELA, (35, 105, 85),
        (132, 250, 636, 27)
    )

    desenhar_texto(
        "COMO JOGAR",
        FONTE_SUBTITULO,
        BRANCO,
        LARGURA // 2,
        245
    )

    # Instrucoes
    instrucoes = [
        ("01", "Use as SETAS para movimentar o estudante."),
        ("02", "Atravesse sempre pela faixa de pedestres."),
        ("03", "Espere o sinal verde antes de atravessar."),
        ("04", "Desvie dos carros e proteja suas 3 vidas.")
    ]

    y = 315

    for numero, instrucao in instrucoes:
        pygame.draw.circle(TELA, (35, 105, 85), (190, y), 19)

        desenhar_texto(
            numero,
            FONTE_PEQUENA,
            BRANCO,
            190,
            y
        )

        desenhar_texto(
            instrucao,
            FONTE_PEQUENA,
            (35, 45, 45),
            470,
            y
        )

        y += 48

    # Mensagem de objetivo
    desenhar_texto(
        "OBJETIVO: CHEGAR A ESCOLA COM SEGURANCA!",
        FONTE_PEQUENA,
        (35, 105, 85),
        LARGURA // 2,
        485
    )

    # Botao de inicio
    pygame.draw.rect(
        TELA, (20, 125, 75),
        (260, 545, 380, 55),
        border_radius=15
    )

    pygame.draw.rect(
        TELA, (75, 175, 110),
        (260, 545, 380, 5),
        border_radius=3
    )

    desenhar_texto(
        "PRESSIONE ENTER PARA COMECAR",
        FONTE_PEQUENA,
        BRANCO,
        LARGURA // 2,
        573
    )

    desenhar_texto(
        "ESC PARA SAIR",
        FONTE_PEQUENA,
        BRANCO,
        LARGURA // 2,
        620
    )



def desenhar_tela_final(vitoria):
    # Fundo principal
    TELA.fill((24, 65, 55) if vitoria else (75, 40, 40))

    # Faixas decorativas laterais
    pygame.draw.rect(TELA, (45, 45, 45), (25, 0, 65, 650))
    pygame.draw.rect(TELA, (45, 45, 45), (810, 0, 65, 650))

    for y in range(20, 650, 90):
        pygame.draw.rect(TELA, AMARELO, (52, y, 10, 40), border_radius=3)
        pygame.draw.rect(TELA, AMARELO, (837, y, 10, 40), border_radius=3)

    # Titulo principal
    titulo = "VOCE CHEGOU A ESCOLA!" if vitoria else "FIM DE JOGO"

    desenhar_texto(
        titulo,
        FONTE_TITULO,
        BRANCO,
        LARGURA // 2,
        95
    )

    # Painel central
    pygame.draw.rect(
        TELA, (15, 45, 42),
        (115, 155, 670, 340),
        border_radius=22
    )

    pygame.draw.rect(
        TELA, (245, 245, 235),
        (122, 162, 656, 326),
        border_radius=18
    )

    # Resultado da partida
    if vitoria:
        desenhar_texto(
            "MISSAO CONCLUIDA!",
            FONTE_SUBTITULO,
            (25, 135, 75),
            LARGURA // 2,
            210
        )

        desenhar_texto(
            "Parabens! Voce realizou tres travessias perfeitas.",
            FONTE_PEQUENA,
            (35, 45, 45),
            LARGURA // 2,
            265
        )

        desenhar_texto(
            "Voce demonstrou responsabilidade no transito!",
            FONTE_PEQUENA,
            (35, 105, 85),
            LARGURA // 2,
            305
        )

    else:
        desenhar_texto(
            "ATENCAO! VOCE NAO CONCLUIU A MISSAO.",
            FONTE_SUBTITULO,
            (190, 55, 45),
            LARGURA // 2,
            220
        )

        desenhar_texto(
            "Suas vidas acabaram durante o percurso.",
            FONTE_PEQUENA,
            (35, 45, 45),
            LARGURA // 2,
            275
        )

        desenhar_texto(
            "Lembre-se: respeite o sinal e use a faixa!",
            FONTE_PEQUENA,
            (170, 65, 45),
            LARGURA // 2,
            315
        )

    # Cartao de pontuacao
    pygame.draw.rect(
        TELA, (35, 105, 85),
        (245, 355, 410, 90),
        border_radius=15
    )

    desenhar_texto(
        "PONTUACAO FINAL",
        FONTE_PEQUENA,
        BRANCO,
        LARGURA // 2,
        380
    )

    desenhar_texto(
        str(pontuacao),
        FONTE_TITULO,
        AMARELO,
        LARGURA // 2,
        417
    )

    # Botao de jogar novamente
    pygame.draw.rect(
        TELA, (20, 125, 75),
        (245, 525, 410, 55),
        border_radius=15
    )

    pygame.draw.rect(
        TELA, (75, 175, 110),
        (245, 525, 410, 5),
        border_radius=3
    )

    desenhar_texto(
        "ENTER - JOGAR NOVAMENTE",
        FONTE_PEQUENA,
        BRANCO,
        LARGURA // 2,
        553
    )

    desenhar_texto(
        "ESC - SAIR DO JOGO",
        FONTE_PEQUENA,
        BRANCO,
        LARGURA // 2,
        620
    )


# ---------------------- GAME LOOP ----------------------
executando = True

while executando:
    RELOGIO.tick(FPS)

    # INPUT: eventos e comandos do jogador
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False

        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                executando = False

            elif evento.key == pygame.K_RETURN:
                if estado in ("inicio", "vitoria", "derrota"):
                    reiniciar_jogo()

    # UPDATE: atualiza as regras e os objetos
    if estado == "jogando":
        teclas = pygame.key.get_pressed()
        atualizar_sinal()
        atualizar_carros()
        atualizar_jogador(teclas)

        if estado == "jogando":
            verificar_colisoes()

    # DRAW: desenha a tela conforme o estado atual
    if estado == "inicio":
        desenhar_tela_inicio()

    elif estado == "jogando":
        desenhar_cenario()
        desenhar_carros()
        desenhar_texto_sinal()
        desenhar_jogador()
        desenhar_interface()

    elif estado == "vitoria":
        desenhar_tela_final(True)

    elif estado == "derrota":
        desenhar_tela_final(False)

    pygame.display.flip()

pygame.quit()
sys.exit()
