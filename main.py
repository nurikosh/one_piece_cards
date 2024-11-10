import random
from deck import Deck, populate_deck, Card
from player import Player, deal_cards
from faction_manager import FactionManager


def find_cards_with_shared_factions(deck, card_name):
    """
    Найти карты, у которых есть пересечения по фракциям с заданной картой.
    """
    target_card = next((card for card in deck.cards if card.name == card_name), None)

    if not target_card:
        print(f"Card '{card_name}' not found in the deck!")
        return

    matching_cards = []

    for card in deck.cards:
        if card == target_card:
            continue
        shared_factions = target_card.faction_ids & card.faction_ids
        if shared_factions:
            matching_cards.append((card, len(shared_factions)))

    matching_cards.sort(key=lambda x: x[1], reverse=True)

    if matching_cards:
        print(f"Cards with shared factions with '{target_card.name}':")
        for card, shared_count in matching_cards:
            print(f"{card.name} - Shared factions: {shared_count}")
    else:
        print(f"'{target_card.name}' has unique factions.")


def find_player_with_lowest_rank(players):
    """
    Определяет игрока с картой наименьшего рейтинга в руке.

    Аргументы:
    players (list): Список объектов класса Player.

    Возвращает:
    player_with_lowest_rank (Player): Игрок, у которого карта с наименьшим рейтингом.
    """
    player_with_lowest_rank = None
    lowest_rank = float('inf')

    for player in players:
        for card in player.hand:
            if card.rank < lowest_rank:
                lowest_rank = card.rank
                player_with_lowest_rank = player

    return player_with_lowest_rank


def initialize_table():
    """
    Инициализирует стол с пустыми парами (атакующая карта, защитная карта).

    Возвращает:
    table (tuple): Кортеж из 6 пар карт (или None) для стола.
    """
    return [(None, None) for _ in range(6)]


def display_table(table, faction_manager):
    """
    Отображает текущее состояние стола в удобочитаемом формате и активные фракции.
    """
    table_display = []
    for attack_card, defense_card in table:
        attack_str = attack_card.name_only() if attack_card else "None"
        defense_str = defense_card.name_only() if defense_card else "None"
        table_display.append(f"({attack_str}, {defense_str})")
    
    active_factions = faction_manager.get_active_factions()
    active_factions_str = ', '.join(str(faction) for faction in active_factions) if active_factions else 'None'
    
    print("Table now:", " | ".join(table_display))
    print("Active factions:", active_factions_str)


def play_turn(attacker, defender, table, deck):
    """
    Реализует один ход, когда атакующий и защищающийся игроки играют свои карты.

    Аргументы:
    attacker (Player): Игрок, который атакует.
    defender (Player): Игрок, который защищается.
    table (list): Стол, представляющий текущие сыгранные карты.
    """
    faction_manager = FactionManager()
    print(f"\n{attacker.name}'s turn to attack.")

    while True:
        # Показываем карты в руке атакующего игрока
        print(f"{attacker.name}'s hand:")
        for i, card in enumerate(attacker.hand):
            print(f"{i + 1}: {card}")

        # Выбор карт для атаки
        attack_indices = input("Select the card numbers to attack (separated by space) or 'f' to finish: ").split()
        
        if 'f' in attack_indices:
            if any(pair[0] is not None for pair in table):
                break  # Завершаем ход только если есть хотя бы одна карта на столе
            else:
                print("You must play at least one card!")
                continue

        try:
            attack_indices = [int(index) - 1 for index in attack_indices]
        except ValueError:
            print("Invalid input. Please enter numbers separated by spaces.")
            continue

        if any(index < 0 or index >= len(attacker.hand) for index in attack_indices):
            print("Invalid card number(s).")
            continue

        attack_cards = [attacker.hand[index] for index in attack_indices]

        # Проверка валидности комбинации карт через FactionManager
        if not faction_manager.validate_multiple_cards(attack_cards):
            print("Invalid card combination - cards must share at least one faction with active factions.")
            continue

        # Добавление карт на стол и в FactionManager
        for i, attack_card in enumerate(attack_cards):
            for j in range(len(table)):
                if table[j] == (None, None):
                    table[j] = (attack_card, None)
                    faction_manager.add_card_factions(attack_card, j * 2)
                    attacker.hand.remove(attack_card)
                    break

        display_table(table, faction_manager)

        # Защита
        while True:
            print(f"\n{defender.name}'s hand:")
            for i, card in enumerate(defender.hand):
                print(f"{i + 1}: {card}")
            print("Enter 'p' to pass or select the card numbers to defend (separated by space):")

            defense_input = input("Select the card numbers or 'p': ")
            if defense_input.lower() == 'p':
                # Логика пропуска хода
                cards_to_take = []
                for pair in table:
                    for card in pair:
                        if card:
                            new_card = Card(card.name, card.rank)
                            new_card.faction_ids = set(card.faction_ids)
                            cards_to_take.append(new_card)
                
                defender.hand.extend(cards_to_take)
                table[:] = initialize_table()
                faction_manager.clear()
                print(f"{defender.name} passes and takes all cards from the table.")
                
                # Проверка на победу
                if not attacker.hand:
                    print(f"{attacker.name} wins!")
                    return True  # Атакующий выигрывает
                return False  # Возвращаем False, чтобы роли игроков не менялись
            else:
                try:
                    defense_indices = [int(index) - 1 for index in defense_input.split()]
                except ValueError:
                    print("Invalid input. Please enter numbers separated by spaces.")
                    continue

                if any(index < 0 or index >= len(defender.hand) for index in defense_indices):
                    print("Invalid card number(s).")
                    continue

                defense_cards = [defender.hand[index] for index in defense_indices]

                # Проверка количества карт защиты
                attack_cards_on_table = [pair[0] for pair in table if pair[0] is not None and pair[1] is None]
                if len(defense_cards) != len(attack_cards_on_table):
                    print("You must cover all attack cards or take the cards from the table.")
                    continue

                # Проверка рангов и фракций
                valid_defense = True
                for attack_card, defense_card in zip(attack_cards_on_table, defense_cards):
                    if defense_card.rank <= attack_card.rank:
                        print(f"Card {defense_card.name} (rank {defense_card.rank}) cannot cover {attack_card.name} (rank {attack_card.rank})")
                        valid_defense = False
                        break

                if not valid_defense:
                    continue

                # Размещение карт защиты на столе и добавление их фракций
                for i, defense_card in enumerate(defense_cards):
                    for j in range(len(table)):
                        if table[j][0] is not None and table[j][1] is None:
                            table[j] = (table[j][0], defense_card)
                            faction_manager.add_card_factions(defense_card, j * 2 + 1)
                            defender.hand.remove(defense_card)
                            break

                display_table(table, faction_manager)
                break  # Выход из цикла защиты после успешного хода

    # Перемещение карт со стола в стопку сброса
    for attack_card, defense_card in table:
        if attack_card:
            deck.add_to_discard_pile(attack_card)
        if defense_card:
            deck.add_to_discard_pile(defense_card)
    table[:] = initialize_table()
    faction_manager.clear()

    # Проверка на победу после успешной защиты
    if not attacker.hand:
        print(f"{attacker.name} wins!")
        return True
    if not defender.hand:
        print(f"{defender.name} wins!")
        return True

    return True  # Возвращаем True, чтобы роли игроков поменялись


def main():
    # Создаем колоду и менеджер фракций
    deck = Deck()
    faction_manager = FactionManager()

    # Заполняем колоду картами
    populate_deck(deck)


    # Перемешиваем колоду
    random.shuffle(deck.cards)

    # Создаем игроков
    player1 = Player("Player 1")
    player2 = Player("Player 2")

    # Раздаем карты игрокам
    deal_cards(deck, [player1, player2])

    # Выводим игроков и их карты
    print("\nPlayers and their hands:")
    print(player1)
    print(player2)

    # Определяем, кто ходит первым
    first_player = find_player_with_lowest_rank([player1, player2])
    second_player = player1 if player2 == first_player else player2
    if first_player:
        print(f"\nПервым ходит {first_player.name}")

    # Инициализация стола
    table = initialize_table()

    # Игровой цикл
    while True:
        turn_result = play_turn(first_player, second_player, table, deck)
        
        # Проверка на победу после каждого хода
        if not first_player.hand:
            print(f"{first_player.name} wins!")
            break
        if not second_player.hand:
            print(f"{second_player.name} wins!")
            break

        if turn_result:
            # Смена ролей атакующего и защищающегося
            first_player, second_player = second_player, first_player


if __name__ == "__main__":
    main()
