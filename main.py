import random
from deck import Deck, populate_deck
from player import Player, deal_cards


def find_cards_with_shared_factions(deck, card_name):
    """
    Найти карты, у которых есть пересечения по фракциям с заданной картой.
    """
    target_card = next((card for card in deck.cards if card.name == card_name), None)

    if not target_card:
        print(f"Card '{card_name}' not found in the deck.")
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


def display_table(table, active_factions):
    """
    Отображает текущее состояние стола в удобочитаемом формате и активные фракции.

    Аргументы:
    table (list): Стол, представляющий текущие сыгранные карты.
    active_factions (set): Набор активных фракций.
    """
    table_display = []
    for attack_card, defense_card in table:
        attack_str = attack_card.name_only() if attack_card else "None"
        defense_str = defense_card.name_only() if defense_card else "None"
        table_display.append(f"({attack_str}, {defense_str})")
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
    active_factions = set()
    print(f"\n{attacker.name}'s turn to attack.")

    # Показываем карты в руке атакующего игрока
    print(f"{attacker.name}'s hand:")
    for i, card in enumerate(attacker.hand):
        print(f"{i + 1}: {card}")

    # Выбор карт для атаки
    attack_indices = input("Select the card numbers to attack (separated by space): ").split()
    attack_indices = [int(index) - 1 for index in attack_indices]

    if any(index < 0 or index >= len(attacker.hand) for index in attack_indices):
        print("Invalid card number(s).")
        return False  # Возвращаем False, чтобы роли игроков не менялись

    attack_cards = [attacker.hand[index] for index in attack_indices]

    # Проверка на общие фракции
    if len(attack_cards) > 1:
        common_factions = set.intersection(*(card.faction_ids for card in attack_cards))
        if not common_factions:
            print("Invalid card combination.")
            return False  # Возвращаем False, чтобы роли игроков не менялись
        active_factions = common_factions
    else:
        active_factions = attack_cards[0].faction_ids

    # Удаление карт из руки атакующего
    for index in sorted(attack_indices, reverse=True):
        attacker.hand.pop(index)

    # Определение места для новых пар карт на столе
    for attack_card in attack_cards:
        for i in range(len(table)):
            if table[i] == (None, None):
                table[i] = (attack_card, None)
                break
        else:
            print("Table is full, cannot add more cards.")
            return False  # Возвращаем False, чтобы роли игроков не менялись

    display_table(table, active_factions)

    while True:
        # Показываем карты в руке защищающегося игрока
        print(f"\n{defender.name}'s hand:")
        for i, card in enumerate(defender.hand):
            print(f"{i + 1}: {card}")
        print("Enter 'p' to pass or select the card numbers to defend (separated by space):")

        # Выбор карт для защиты или pass
        defense_input = input("Select the card numbers or 'p': ")
        if defense_input.lower() == 'p':
            # Защищающийся пропускает, забирает карты со стола
            defender.hand.extend([card for pair in table for card in pair if card])
            table[:] = initialize_table()  # Очистка стола
            print(f"{defender.name} passes and takes all cards from the table.")
            return False  # Возвращаем False, чтобы роли игроков не менялись
        else:
            defense_indices = [int(index) - 1 for index in defense_input.split()]
            if any(index < 0 or index >= len(defender.hand) for index in defense_indices):
                print("Invalid card number(s).")
                continue

            defense_cards = [defender.hand[index] for index in defense_indices]

            # Проверка, что все карты защиты могут покрыть карты атаки
            valid_defense = True
            for i, (attack_card, defense_card) in enumerate(zip(attack_cards, defense_cards)):
                if defense_card.rank < attack_card.rank:
                    print("Вы не можете покрыть этой картой, выберите другую карту или возьмите карты со стола.")
                    valid_defense = False
                    break

            if not valid_defense:
                continue

            # Обновление пар карт на столе
            for i, defense_card in enumerate(defense_cards):
                for j in range(len(table)):
                    if table[j][0] == attack_cards[i] and table[j][1] is None:
                        table[j] = (attack_cards[i], defense_card)
                        defender.hand.remove(defense_card)
                        break

            for defense_card in defense_cards:
                active_factions.update(defense_card.faction_ids)
            break  # Выход из цикла после успешного выбора карт для защиты

    display_table(table, active_factions)

    # Атакующий завершает ход
    while True:
        finish_turn = input("Enter 'f' to finish your turn: ").lower()
        if finish_turn == 'f':
            # Перемещение карт со стола в стопку сброса
            for attack_card, defense_card in table:
                if attack_card:
                    deck.add_to_discard_pile(attack_card)
                if defense_card:
                    deck.add_to_discard_pile(defense_card)
            table[:] = initialize_table()  # Очистка стола
            active_factions.clear()  # Сброс активных фракций
            break
        else:
            print("Invalid input. Please enter 'f' to finish your turn.")

    # Проверка на победу
    if not attacker.hand:
        print(f"{attacker.name} wins!")
        return True
    if not defender.hand:
        print(f"{defender.name} wins!")
        return True

    return True  # Возвращаем True, чтобы роли игроков поменялись


def main():
    # Создаем колоду
    deck = Deck()

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
        if turn_result:
            # Проверка на победу после каждого хода
            if not first_player.hand:
                print(f"{first_player.name} wins!")
                break
            if not second_player.hand:
                print(f"{second_player.name} wins!")
                break

            # Смена ролей атакующего и защищающегося
            first_player, second_player = second_player, first_player


if __name__ == "__main__":
    main()
