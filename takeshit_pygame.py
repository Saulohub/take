import pygame
import random
import sys
import math

# Inicialização do Pygame
pygame.init()

# Configurações da tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Packet Quest - A Jornada dos Dados")

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# Fonte
font = pygame.font.SysFont('Arial', 20)
title_font = pygame.font.SysFont('Arial', 36)

class Packet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.speed = 5
        self.color = GREEN
        self.target = None
        self.path = []
        self.progress = 0
        self.lost = False
        self.delivered = False
    
    def draw(self, screen):
        if not self.lost and not self.delivered:
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
            pygame.draw.circle(screen, BLACK, (self.x, self.y), self.radius, 2)
            
            # Desenhar número no pacote (simulando header)
            text = font.render("PKT", True, BLACK)
            text_rect = text.get_rect(center=(self.x, self.y))
            screen.blit(text, text_rect)
    
    def move(self):
        if self.target and not self.delivered and not self.lost:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = max(1, math.sqrt(dx*dx + dy*dy))
            
            if distance < 5:  # Chegou ao alvo
                if self.target.is_destination:
                    self.delivered = True
                else:
                    if self.path:
                        self.target = self.path.pop(0)
                    else:
                        self.lost = True
            else:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
                self.progress = min(1, self.progress + 0.001)

class Node:
    def __init__(self, x, y, name, is_router=False, is_source=False, is_destination=False):
        self.x = x
        self.y = y
        self.radius = 20
        self.name = name
        self.is_router = is_router
        self.is_source = is_source
        self.is_destination = is_destination
        self.connections = []
        self.congestion = 0
    
    def draw(self, screen):
        # Cor baseada no tipo de nó
        if self.is_source:
            color = CYAN
        elif self.is_destination:
            color = YELLOW
        elif self.is_router:
            color = BLUE
        else:
            color = WHITE
            
        pygame.draw.circle(screen, color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, BLACK, (self.x, self.y), self.radius, 2)
        
        # Desenhar nome do nó
        text = font.render(self.name, True, BLACK)
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)
        
        # Indicador de congestionamento
        if self.congestion > 0 and self.is_router:
            congestion_text = font.render(f"{self.congestion}%", True, RED)
            screen.blit(congestion_text, (self.x - 15, self.y + 25))

class Connection:
    def __init__(self, node1, node2, speed=1, reliability=100):
        self.node1 = node1
        self.node2 = node2
        self.speed = speed
        self.reliability = reliability  # 0-100%
        self.active = True
    
    def draw(self, screen):
        if self.active:
            color = GREEN if self.reliability > 80 else YELLOW if self.reliability > 50 else RED
            pygame.draw.line(screen, color, (self.node1.x, self.node1.y), 
                            (self.node2.x, self.node2.y), 2)
            
            # Desenhar indicador de velocidade
            mid_x = (self.node1.x + self.node2.x) // 2
            mid_y = (self.node1.y + self.node2.y) // 2
            speed_text = font.render(f"{self.speed}Mbps", True, WHITE)
            screen.blit(speed_text, (mid_x - 30, mid_y - 10))

class Firewall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.active = True
    
    def draw(self, screen):
        color = RED if self.active else (100, 100, 100)
        pygame.draw.rect(screen, color, (self.x - self.width//2, self.y - self.height//2, 
                         self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x - self.width//2, self.y - self.height//2, 
                         self.width, self.height), 2)
        
        # Desenhar ícone de firewall
        text = font.render("FW", True, WHITE)
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)

class Game:
    def __init__(self):
        self.nodes = []
        self.connections = []
        self.packets = []
        self.firewalls = []
        self.score = 0
        self.packets_sent = 0
        self.packets_lost = 0
        self.level = 1
        self.game_state = "menu"  # menu, playing, game_over
        self.create_network()
    
    def create_network(self):
        # Limpar rede existente
        self.nodes = []
        self.connections = []
        self.packets = []
        self.firewalls = []
        
        # Criar nós básicos para o nível 1
        source = Node(100, HEIGHT//2, "SRC", is_source=True)
        router1 = Node(300, HEIGHT//2 - 100, "R1", is_router=True)
        router2 = Node(300, HEIGHT//2 + 100, "R2", is_router=True)
        destination = Node(700, HEIGHT//2, "DST", is_destination=True)
        
        self.nodes.extend([source, router1, router2, destination])
        
        # Conexões básicas
        self.connections.append(Connection(source, router1, speed=10, reliability=90))
        self.connections.append(Connection(source, router2, speed=5, reliability=95))
        self.connections.append(Connection(router1, destination, speed=10, reliability=85))
        self.connections.append(Connection(router2, destination, speed=15, reliability=75))
        
        # Adicionar conexões às listas de nós
        for conn in self.connections:
            conn.node1.connections.append(conn.node2)
            conn.node2.connections.append(conn.node1)
        
        # Adicionar firewalls aleatórios em níveis mais altos
        if self.level > 1:
            for _ in range(min(self.level - 1, 3)):
                x = random.randint(200, 600)
                y = random.randint(100, HEIGHT-100)
                self.firewalls.append(Firewall(x, y))
    
    def send_packet(self, path):
        if path and len(path) > 1:
            packet = Packet(path[0].x, path[0].y)
            packet.path = path[1:]
            packet.target = packet.path.pop(0)
            self.packets.append(packet)
            self.packets_sent += 1
            
            # Simular congestionamento
            for node in path:
                if node.is_router:
                    node.congestion = min(100, node.congestion + 10)
    
    def update(self):
        # Atualizar pacotes
        for packet in self.packets[:]:
            packet.move()
            
            # Verificar se o pacote foi perdido (baseado na confiabilidade da conexão)
            if random.randint(1, 1000) < 2:  # 0.2% de chance por frame
                packet.lost = True
            
            # Verificar colisão com firewall
            for firewall in self.firewalls:
                if firewall.active and abs(packet.x - firewall.x) < 30 and abs(packet.y - firewall.y) < 30:
                    packet.lost = True
            
            # Remover pacotes entregues ou perdidos
            if packet.delivered:
                self.packets.remove(packet)
                self.score += 100
            elif packet.lost:
                self.packets.remove(packet)
                self.packets_lost += 1
        
        # Reduzir congestionamento ao longo do tempo
        for node in self.nodes:
            if node.is_router:
                node.congestion = max(0, node.congestion - 0.1)
    
    def draw(self, screen):
        screen.fill(BLACK)
        
        if self.game_state == "menu":
            self.draw_menu(screen)
        elif self.game_state == "playing":
            self.draw_game(screen)
        elif self.game_state == "game_over":
            self.draw_game_over(screen)
    
    def draw_menu(self, screen):
        title = title_font.render("Packet Quest", True, WHITE)
        subtitle = font.render("A Jornada dos Dados", True, CYAN)
        instruction1 = font.render("Pressione ESPAÇO para começar", True, WHITE)
        instruction2 = font.render("Use o mouse para selecionar a rota dos pacotes", True, WHITE)
        
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//3 + 50))
        screen.blit(instruction1, (WIDTH//2 - instruction1.get_width()//2, HEIGHT//2 + 50))
        screen.blit(instruction2, (WIDTH//2 - instruction2.get_width()//2, HEIGHT//2 + 80))
        
        # Desenhar exemplo de rede
        pygame.draw.circle(screen, CYAN, (WIDTH//4, HEIGHT*3//4), 15)
        pygame.draw.circle(screen, BLUE, (WIDTH//2, HEIGHT*3//4 - 50), 15)
        pygame.draw.circle(screen, BLUE, (WIDTH//2, HEIGHT*3//4 + 50), 15)
        pygame.draw.circle(screen, YELLOW, (WIDTH*3//4, HEIGHT*3//4), 15)
        
        pygame.draw.line(screen, GREEN, (WIDTH//4, HEIGHT*3//4), (WIDTH//2, HEIGHT*3//4 - 50), 2)
        pygame.draw.line(screen, GREEN, (WIDTH//4, HEIGHT*3//4), (WIDTH//2, HEIGHT*3//4 + 50), 2)
        pygame.draw.line(screen, GREEN, (WIDTH//2, HEIGHT*3//4 - 50), (WIDTH*3//4, HEIGHT*3//4), 2)
        pygame.draw.line(screen, GREEN, (WIDTH//2, HEIGHT*3//4 + 50), (WIDTH*3//4, HEIGHT*3//4), 2)
    
    def draw_game(self, screen):
        # Desenhar conexões
        for connection in self.connections:
            connection.draw(screen)
        
        # Desenhar firewalls
        for firewall in self.firewalls:
            firewall.draw(screen)
        
        # Desenhar nós
        for node in self.nodes:
            node.draw(screen)
        
        # Desenhar pacotes
        for packet in self.packets:
            packet.draw(screen)
        
        # Desenhar HUD
        score_text = font.render(f"Pontuação: {self.score}", True, WHITE)
        level_text = font.render(f"Nível: {self.level}", True, WHITE)
        stats_text = font.render(f"Pacotes: {self.packets_sent} Enviados | {self.packets_lost} Perdidos", True, WHITE)
        
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 40))
        screen.blit(stats_text, (10, 70))
        
        # Instruções
        if len(self.packets) < 3:  # Mostrar instruções quando há poucos pacotes
            instruction = font.render("Clique nos roteadores para criar uma rota do SRC ao DST", True, WHITE)
            screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, HEIGHT - 30))
    
    def draw_game_over(self, screen):
        title = title_font.render("Fim de Jogo", True, WHITE)
        score_text = font.render(f"Pontuação Final: {self.score}", True, WHITE)
        packets_text = font.render(f"Pacotes Entregues: {self.packets_sent - self.packets_lost}/{self.packets_sent}", True, WHITE)
        restart_text = font.render("Pressione R para reiniciar", True, WHITE)
        
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        screen.blit(packets_text, (WIDTH//2 - packets_text.get_width()//2, HEIGHT//2 + 40))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 100))
    
    def handle_click(self, pos):
        if self.game_state != "playing":
            return
        
        clicked_node = None
        for node in self.nodes:
            distance = math.sqrt((pos[0] - node.x)**2 + (pos[1] - node.y)**2)
            if distance <= node.radius:
                clicked_node = node
                break
        
        return clicked_node

def main():
    clock = pygame.time.Clock()
    game = Game()
    selected_path = []
    
    # Evento periódico para enviar pacotes automaticamente
    SEND_PACKET_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SEND_PACKET_EVENT, 2000)  # A cada 2 segundos
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game.game_state == "menu":
                    game.game_state = "playing"
                elif event.key == pygame.K_r and game.game_state == "game_over":
                    game = Game()
                    game.game_state = "playing"
                    selected_path = []
            
            elif event.type == pygame.MOUSEBUTTONDOWN and game.game_state == "playing":
                clicked_node = game.handle_click(event.pos)
                
                if clicked_node:
                    if not selected_path and clicked_node.is_source:
                        selected_path.append(clicked_node)
                    elif selected_path and clicked_node in selected_path[-1].connections:
                        selected_path.append(clicked_node)
                        
                        if clicked_node.is_destination:
                            game.send_packet(selected_path)
                            selected_path = []
            
            elif event.type == SEND_PACKET_EVENT and game.game_state == "playing":
                # Enviar pacote automático se o jogador estiver inativo
                if game.packets_sent < 5 or random.random() < 0.3:
                    source = next(node for node in game.nodes if node.is_source)
                    destination = next(node for node in game.nodes if node.is_destination)
                    
                    # Escolher caminho aleatório (jogador inativo)
                    path = [source]
                    current = source
                    
                    while current != destination and len(path) < 5:
                        if current.connections:
                            next_node = random.choice(current.connections)
                            if next_node not in path:
                                path.append(next_node)
                                current = next_node
                    
                    if path[-1] == destination:
                        game.send_packet(path)
        
        game.update()
        
        # Verificar condições de vitória/derrota
        if game.game_state == "playing":
            if game.score >= 1000 * game.level:  # Passar de nível
                game.level += 1
                game.create_network()
            elif game.packets_lost >= 10:  # Game over
                game.game_state = "game_over"
        
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

