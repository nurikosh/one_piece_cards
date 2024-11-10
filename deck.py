# deck.py

from card import Card

class Deck:
    def __init__(self):
        self.cards = []
        self.discard_pile = []  # Стопка сброса

    def add_card(self, card):
        """Add card to the deck."""
        self.cards.append(card)

    def remove_card(self, card):
        """Remove card from the deck."""
        self.cards.remove(card)

    def add_to_discard_pile(self, card):
        """Add card to the discard pile."""
        self.discard_pile.append(card)

    def __str__(self):
        return '\n'.join(str(card) for card in self.cards)

    def display_discard_pile(self):
        """Display all cards in the discard pile."""
        if self.discard_pile:
            return '\n'.join(str(card) for card in self.discard_pile)
        else:
            return "Discard pile is empty."

# Function to create a card and add factions
def create_card(name, rank, factions):
    card = Card(name, rank)
    for faction in factions:
        card.add_faction(faction)
    return card

def populate_deck(deck):
    """Populate the deck with predefined cards."""
    cards_data = [
        ("Gol D Roger", 100, (1, 16)),
        ("Prime Whitebeard", 100, (2, 3)),
        ("Prime Monkey D Garp", 100, (6, 7, 8)),
        ("Marshall D Teach", 96, (2, 3, 4, 5, 24)),
        ("Monkey D Dragon", 96, (9, 7)),
        ("Prime Rayleigh", 95, (1,)),
        ("Shanks", 95, (1, 10, 3)),
        ("Akainu", 94, (6,)),
        ("Drakul Mihawk", 93, (4, 11)),
        ("Monkey D Luffy", 92, (12, 3, 5, 8)),
        ("Aokiji", 92, (6, 24)),
        ("Old Monkey D Garp", 91, (6, 7, 8)),
        ("Old Whitebeard", 91, (2, 3)),
        ("Kizaru", 90, (6,)),
        ("Old Rayleigh", 90, (1,)),
        ("Benn Beckman", 89, (10,)),
        ("Marco the Phoenix", 88, (2,)),
        ("Eustass \"Captain\" Kid", 87, (18, 5)),
        ("Trafalgar D Water Law", 87, (4, 5)),
        ("Roronoa Zoro", 86, (12, 5)),
        ("Lucky Roux", 85, (10,)),
        ("Sir Crocodile", 84, (4, 14, 11)),
        ("Boa Hancock", 83, (4, 13)),
        ("Winsmoke Sanji", 82, (12, 19)),
        ("Killer", 81, (18, 5)),
        ("Yasopp", 81, (10,)),
        ("Jinbei", 80, (12, 4, 15)),
        ("Donquixote Doflamingo", 79, (4,)),
        ("Portgas D Ace", 75, (2, 16, 8)),
        ("God Enel", 75, (17,)),
        ("Bartholomew Kuma", 75, (4, 9)),
        ("Urouge", 74, (5,)),
        ("X Drake", 73, (5, 6)),
        ("Smoker", 72, (6,)),
        ("Nico Robin", 71, (12, 14,)),
        ("Basil Hawkins", 71, (5,)),
        ("Cyborg Franky", 70, (12,)),
        ("Soul King Brook", 70, (12,)),
        ("Gecko Moria", 69, (4,)),
        ("Capone \"Gang\" Bege", 68, (5,)),
        ("Jewelry Bonney", 67, (5,)),
        ("Mr1 Daz Bonez", 66, (14, 11)),
        ("Rockstar", 65, (10,)),
        ("Clown Buggy", 64, (1, 4, 3, 11)),
        ("Tony Tony Chopper", 63, (12,)),
        ("Usopp", 62, (12,)),
        ("Nami", 61, (12, 22)),
        ("Scratchmen Apoo", 61, (5,)),
        ("Mr2 Bentham", 60, (14,)),
        ("Marguerite", 59, (13,)),
        ("Mr3 Galdino", 58, (14, 11)),
        ("Broggy", 57, (21,)),
        ("Dorry", 57, (21,)),
        ("Jango", 56, (20, 6)),
        ("Miss Double Finger", 55, (14,)),
        ("Arlong", 54, (15, 22)),
        ("Don Krieg", 53, (23,)),
        ("Kuro (Klahadore)", 52, (20,)),
        ("Zeff", 51, (23, 19)),
        ("Miss Golden Week", 50, (14,))
    ]

    for name, rank, factions in cards_data:
        deck.add_card(create_card(name, rank, factions))

# Create deck and populate it
deck = Deck()
populate_deck(deck)

# Print all cards in the deck
print(deck)