import pygame
import random
from deck import Deck, populate_deck
from player import Player, deal_cards
from card import Card
from factions import FACTIONS

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CARD_WIDTH, CARD_HEIGHT = 100, 150
BACKGROUND_COLOR = (34, 139, 34)  # Темно-зеленый цвет
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TABLE_AREA = pygame.Rect(50, SCREEN_HEIGHT//2 - CARD_HEIGHT//2, SCREEN_WIDTH-100, CARD_HEIGHT)

# Создание окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Card Game")

# Шрифты
try:
    font = pygame.font.Font(None, 24)
except Exception as e:
    print(f"Error loading font: {e}")
    pygame.quit()
    exit()

class GameState:
    def __init__(self):
        self.active_factions = set()
        self.current_attacker = None
        self.current_defender = None
        self.table = [(None, None) for _ in range(6)]
        self.phase = "ATTACK"  # "ATTACK" или "DEFENSE"

    def switch_players(self):
        self.current_attacker, self.current_defender = self.current_defender, self.current_attacker
        self.phase = "ATTACK"
        self.active_factions.clear()

class DraggableCard:
    def __init__(self, card, x, y, owner):
        self.card = card
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.dragging = False
        self.original_pos = (x, y)
        self.owner = owner  # Добавляем владельца карты

    def handle_event(self, event, game_state):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                # Проверяем, может ли игрок двигать карту
                if (game_state.phase == "ATTACK" and self.owner == game_state.current_attacker) or \
                   (game_state.phase == "DEFENSE" and self.owner == game_state.current_defender):
                    self.dragging = True
                    return True
        elif event.type == pygame.MOUSEBUTTONUP and self.dragging:
            self.dragging = False
            if TABLE_AREA.colliderect(self.rect):
                # Проверяем правила размещения карты
                if self.can_place_card(game_state):
                    return True
            self.rect.x, self.rect.y = self.original_pos
            return False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.rect.x = event.pos[0] - CARD_WIDTH//2
            self.rect.y = event.pos[1] - CARD_HEIGHT//2

    def can_place_card(self, game_state):
        if game_state.phase == "ATTACK":
            # Проверка правил для атакующей карты
            if not game_state.active_factions:
                return True
            return bool(self.card.faction_ids & game_state.active_factions)
        else:  # DEFENSE
            # Находим карту атаки, которую пытаемся покрыть
            for i, (attack_card, defense_card) in enumerate(game_state.table):
                if attack_card and not defense_card:
                    if self.card.rank > attack_card.rank:
                        return True
            return False

def draw_card(screen, card, x, y):
    """Рисует карту на экране."""
    pygame.draw.rect(screen, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT))
    
    # Отображение имени карты
    text_surface = font.render(f"{card.name}", True, BLACK)
    screen.blit(text_surface, (x + 5, y + 5))
    
    # Отображение ранга
    text_surface = font.render(f"Rank: {card.rank}", True, BLACK)
    screen.blit(text_surface, (x + 5, y + 25))
    
    # Отображение номеров фракций
    factions_text = ', '.join(str(fid) for fid in card.faction_ids)
    text_surface = font.render(f"Factions: {factions_text}", True, BLACK)
    screen.blit(text_surface, (x + 5, y + 45))

def draw_game_state(screen, font, game_state):
    # Отображение текущей фазы и активных фракций
    phase_text = f"Phase: {game_state.phase}"
    text_surface = font.render(phase_text, True, BLACK)
    screen.blit(text_surface, (10, 10))

    active_factions_text = f"Active Factions: {', '.join(map(str, game_state.active_factions))}"
    text_surface = font.render(active_factions_text, True, BLACK)
    screen.blit(text_surface, (10, 30))

    # Отображение текущих игроков
    attacker_text = f"Attacker: {game_state.current_attacker.name}"
    defender_text = f"Defender: {game_state.current_defender.name}"
    text_surface = font.render(attacker_text, True, BLACK)
    screen.blit(text_surface, (10, 50))
    text_surface = font.render(defender_text, True, BLACK)
    screen.blit(text_surface, (10, 70))

def main():
    try:
        # Инициализация игры
        deck = Deck()
        populate_deck(deck)
        random.shuffle(deck.cards)
        
        player1 = Player("Player 1")
        player2 = Player("Player 2")
        deal_cards(deck, [player1, player2])

        # Определение первого игрока
        game_state = GameState()
        game_state.current_attacker = min([player1, player2], 
                                        key=lambda p: min(card.rank for card in p.hand))
        game_state.current_defender = player2 if game_state.current_attacker == player1 else player1

        # Создание перетаскиваемых карт
        player1_cards = [DraggableCard(card, 50 + i * (CARD_WIDTH + 10), 50, player1) 
                        for i, card in enumerate(player1.hand)]
        player2_cards = [DraggableCard(card, 50 + i * (CARD_WIDTH + 10), 
                        SCREEN_HEIGHT - CARD_HEIGHT - 50, player2) 
                        for i, card in enumerate(player2.hand)]

        # Кнопка для завершения хода
        end_turn_button = pygame.Rect(SCREEN_WIDTH - 110, SCREEN_HEIGHT//2 - 25, 100, 50)

        running = True
        while running:
            screen.fill(BACKGROUND_COLOR)
            
            # Отрисовка игрового состояния
            draw_game_state(screen, font, game_state)
            
            # Отрисовка кнопки завершения хода
            pygame.draw.rect(screen, WHITE, end_turn_button)
            text_surface = font.render("End Turn", True, BLACK)
            screen.blit(text_surface, (end_turn_button.x + 10, end_turn_button.y + 15))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Обработка нажатия на кнопку завершения хода
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if end_turn_button.collidepoint(event.pos):
                        if game_state.phase == "ATTACK":
                            game_state.phase = "DEFENSE"
                        else:
                            game_state.switch_players()
                
                # Обработка перетаскивания карт
                for card in player1_cards + player2_cards:
                    if card.handle_event(event, game_state):
                        # Обработка размещения карты на столе
                        if game_state.phase == "ATTACK":
                            # Добавление карты на стол и обновление активных фракций
                            for i, (attack, defense) in enumerate(game_state.table):
                                if not attack:
                                    game_state.table[i] = (card.card, None)
                                    game_state.active_factions.update(card.card.faction_ids)
                                    if card in player1_cards:
                                        player1_cards.remove(card)
                                    else:
                                        player2_cards.remove(card)
                                    break
                        else:  # DEFENSE
                            # Добавление карты защиты
                            for i, (attack, defense) in enumerate(game_state.table):
                                if attack and not defense and card.card.rank > attack.rank:
                                    game_state.table[i] = (attack, card.card)
                                    if card in player1_cards:
                                        player1_cards.remove(card)
                                    else:
                                        player2_cards.remove(card)
                                    break

            # Отрисовка стола
            pygame.draw.rect(screen, (24, 129, 24), TABLE_AREA, 2)
            
            # Отрисовка карт на столе
            for i, (attack, defense) in enumerate(game_state.table):
                if attack:
                    draw_card(screen, attack, 
                            TABLE_AREA.x + i * (CARD_WIDTH + 10), 
                            TABLE_AREA.y)
                if defense:
                    draw_card(screen, defense, 
                            TABLE_AREA.x + i * (CARD_WIDTH + 10), 
                            TABLE_AREA.y + CARD_HEIGHT//2)

            # Отрисовка карт игроков
            for card in player1_cards:
                draw_card(screen, card.card, card.rect.x, card.rect.y)
            for card in player2_cards:
                draw_card(screen, card.card, card.rect.x, card.rect.y)

            # Проверка победных условий
            if not player1_cards:
                print("Player 1 wins!")
                running = False
            elif not player2_cards:
                print("Player 2 wins!")
                running = False

            pygame.display.flip()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()