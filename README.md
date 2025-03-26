Como Executar no VS Code
Pré-requisitos:

Tenha o Python instalado

Instale a biblioteca Pygame: pip install pygame

Execução:

Copie todo o código para um arquivo .py no VS Code (por exemplo, packet_quest.py)

Execute com o botão "Run" ou pelo terminal: python packet_quest.py

🕹️ Mecânicas do Jogo
Elementos do Jogo:
Nós:

SRC (Ciano): Origem dos pacotes

Roteadores (Azul): Nós intermediários

DST (Amarelo): Destino final

Conexões: Linhas entre nós com informações de velocidade e confiabilidade

Firewalls (Vermelho): Se um pacote colidir, ele é perdido

Pacotes (Verde): Circulam pela rede com o texto "PKT"

Sistema de Pontuação:
+100 pontos por pacote entregue

Game over se perder 10 pacotes

Passa de nível ao atingir 1000 × nível atual

💻 Como o Código Funciona
Estrutura Principal:
Inicialização:

python
Copy
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
Classes Principais:

Packet: Representa os pacotes de dados

Node: Representa os nós da rede (roteadores, origem, destino)

Connection: Ligações entre nós

Firewall: Obstáculos que podem destruir pacotes

Game: Classe principal que gerencia toda a lógica

Loop Principal:

python
Copy
while running:
    # Processa eventos
    # Atualiza estado do jogo
    # Desenha tudo na tela
Lógica de Movimento dos Pacotes:
Os pacotes seguem um caminho de nós usando vetores de direção:

python
Copy
dx = self.target.x - self.x
dy = self.target.y - self.y
distance = max(1, math.sqrt(dx*dx + dy*dy))
self.x += (dx / distance) * self.speed
self.y += (dy / distance) * self.speed
Sistema de Níveis:
Cada nível adiciona mais firewalls
