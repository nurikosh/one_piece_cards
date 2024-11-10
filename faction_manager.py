# faction_manager.py

class FactionManager:
    def __init__(self):
        # Создаем 12 слотов (6 пар карт, каждая карта имеет свой слот)
        self.faction_slots = [{'active': set(), 'inactive': set()} for _ in range(12)]
        self.active_factions = set()  # Общий набор активных фракций

    def add_card_factions(self, card, slot_index):
        """
        Добавляет фракции карты в определенный слот и обновляет активные/неактивные фракции.
        
        Args:
            card: Объект карты
            slot_index: Индекс слота (0-11)
        """
        if 0 <= slot_index < 12:
            # Получаем все текущие активные фракции до добавления новой карты
            current_active = self.get_active_factions()
            
            # Добавляем фракции новой карты
            self.faction_slots[slot_index]['active'] = set(card.faction_ids)
            
            # Если уже есть активные фракции, обновляем статусы
            if current_active:
                for slot in self.faction_slots:
                    if slot['active']:
                        # Фракции, которые не пересекаются с новой картой, переходят в неактивные
                        non_matching = slot['active'] - card.faction_ids
                        slot['inactive'].update(non_matching)
                        slot['active'] = slot['active'] & card.faction_ids

            self.update_active_factions()

    def remove_card_factions(self, slot_index):
        """Удаляет фракции из определенного слота."""
        if 0 <= slot_index < 12:
            self.faction_slots[slot_index]['active'].clear()
            self.faction_slots[slot_index]['inactive'].clear()
            self.update_active_factions()

    def update_active_factions(self):
        """Обновляет общий набор активных фракций, исключая неактивные."""
        active_sets = []
        inactive_sets = []
        
        for slot in self.faction_slots:
            if slot['active']:
                active_sets.append(slot['active'])
            if slot['inactive']:
                inactive_sets.append(slot['inactive'])

        if active_sets:
            # Объединяем все активные фракции
            all_active = set.union(*active_sets)
            # Если есть неактивные фракции, исключаем их
            if inactive_sets:
                all_inactive = set.union(*inactive_sets)
                self.active_factions = all_active - all_inactive
            else:
                self.active_factions = all_active
        else:
            self.active_factions.clear()

    def get_active_factions(self):
        """Возвращает текущий набор активных фракций."""
        return self.active_factions

    def clear(self):
        """Очищает все слоты и активные фракции."""
        self.faction_slots = [{'active': set(), 'inactive': set()} for _ in range(12)]
        self.active_factions.clear()

    def validate_card_factions(self, card):
        """
        Проверяет, может ли карта быть сыграна с текущими активными фракциями.
        
        Args:
            card: Объект карты для проверки
        
        Returns:
            bool: True если карта может быть сыграна, False в противном случае
        """
        if not self.active_factions:
            return True
        return bool(card.faction_ids & self.active_factions)

    def validate_multiple_cards(self, cards):
        """
        Проверяет, могут ли несколько карт быть сыграны вместе.
        
        Args:
            cards: Список карт для проверки
        
        Returns:
            bool: True если карты могут быть сыграны вместе, False в противном случае
        """
        if not cards:
            return False
        if len(cards) == 1:
            return self.validate_card_factions(cards[0])
            
        # Находим общие фракции между всеми картами
        common_factions = set.intersection(*(card.faction_ids for card in cards))
        
        # Если нет активных фракций, достаточно иметь общие фракции между картами
        if not self.active_factions:
            return bool(common_factions)
            
        # Иначе должно быть пересечение с активными фракциями
        return bool(common_factions & self.active_factions) 