import itertools
import random
from collections import Counter

colors = ["diamonds", "hearts", "spades", "clubs"]
values = ["2","3","4","5","6","7","8","9","T","J","Q","K","A"]

# Constantes de classe pour éviter la redondance
VALUE_MAP = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    
VALUE_NAMES = {'2': 'Twos', '3': 'Threes', '4': 'Fours', '5': 'Fives', '6': 'Sixes',
                   '7': 'Sevens', '8': 'Eights', '9': 'Nines', 'T': 'Tens', 'J': 'Jacks',
                   'Q': 'Queens', 'K': 'Kings', 'A': 'Aces'}
    
ALL_CARDS = [r+s for r in "23456789TJQKA" for s in "HDCS"]

class Player:
    def __init__(self, stack, position, hands = []):
        self.hands = hands
        self.stack = stack
        self.position = position

    def bet(self, amount):
        """Le joueur mise une certaine somme"""
        assert amount <= self.stack, "Le joueur ne peut pas miser plus que son stack"
        self.stack -= amount
        
    def fold(self):
        """Le joueur se couche"""
        pass

    def call(self, amount):
        """Le joueur suit une mise"""
        assert amount <= self.stack, "Le joueur ne peut pas suivre plus que son stack"
        self.stack -= amount
    
    def win(self, pot):
        """Le joueur gagne une certaine somme"""
        self.stack += pot
        

class Dealer:
    def __init__(self, players_count = 6):
        self.players_count = players_count
        self.cards = [] # Paquet de cartes
        self.board = [] 

    def cards_init(self):
        """Initialise le paquet de cartes"""
        for color in colors:
            for value in values:
                card = (color,value)
                self.cards.append(card)

    def shuffle(self):
        random.shuffle(self.cards)
    
    def hands(self):
        """Distribue les mains aux joueurs"""
        hands = []
        self.cards_init()
        self.shuffle()

        for _ in range(self.players_count):
            hands.append(Player(10, 0, [self.cards.pop(), self.cards.pop()]))
        return hands
    
    def board(self, etape = 0):
        """Distribue le board, doit impérativement être appelé après hands()"""
        if etape == 0:
            # Flop
            self.board.append(self.cards.pop())
            self.board.append(self.cards.pop())
            self.board.append(self.cards.pop())
            self.cards.pop() # carte brûlée
        elif etape == 1:
            # Turn
            self.board.append(self.cards.pop())
            self.cards.pop() # carte brûlée

        elif etape == 2:
            # River
            self.board.append(self.cards.pop())
        return self.board

class Poker:
    def __init__(self):
        pass
    def pot(self):
        pass
    def round(self):
        """Gère un tour de jeu complet"""
        pass
    def winner(self):
        """Détermine le gagnant du pot"""
        pass


        def hand_rank(self):
            """
            Retourne la meilleure combinaison possible avec hand + board.
            Retourne un tuple (rang, description, cartes) où rang est un entier (1=plus faible, 9=plus fort)
            """
            cards = self.hand + self.board
            if len(cards) < 5:
                return (1, "High Card", cards)  # Pas assez de cartes pour une combinaison
    
            # Extraire valeurs et couleurs
            values = [card[0] for card in cards]
            suits = [card[1] for card in cards]
            num_values = [value_map[v] for v in values]
            num_values.sort(reverse=True)
    
            # Compter les occurrences des valeurs et couleurs
            value_counts = {}
            for v in values:
                value_counts[v] = value_counts.get(v, 0) + 1
            suit_counts = {}
            for s in suits:
                suit_counts[s] = suit_counts.get(s, 0) + 1
    
            # Vérifier les combinaisons, de la plus forte à la plus faible
            # Quinte Flush (9)
            if max(suit_counts.values()) >= 5:
                for suit in suit_counts:
                    if suit_counts[suit] >= 5:
                        suit_values = sorted([value_map[card[0]] for card in cards if card[1] == suit], reverse=True)
                        for i in range(len(suit_values) - 4):
                            if suit_values[i] - suit_values[i + 4] == 4 and len(set(suit_values[i:i+5])) == 5:
                                high_card = list(value_map.keys())[list(value_map.values()).index(suit_values[i])]
                                return (9, f"Straight Flush, {value_names[high_card]} high", [f"{v}{suit}" for v in suit_values[i:i+5]])
                            # Cas spécial : quinte flush à l'As (As bas)
                            if suit_values[:5] == [14, 5, 4, 3, 2]:
                                return (9, "Straight Flush, Five high", [f"{v}{suit}" for v in [14, 5, 4, 3, 2]])
    
            # Carré (8)
            for value, count in value_counts.items():
                if count == 4:
                    kicker = max([v for v in num_values if v != value_map[value]])
                    kicker_card = list(value_map.keys())[list(value_map.values()).index(kicker)]
                    return (8, f"Four of a Kind, {value_names[value]}", 
                            [f"{value}{s}" for s in suits if f"{value}{s}" in cards] + 
                            [f"{kicker_card}{s}" for s in suits if f"{kicker_card}{s}" in cards])
    
            # Full House (7)
            if 3 in value_counts.values() and 2 in value_counts.values():
                three = [k for k, v in value_counts.items() if v == 3][0]
                pair = [k for k, v in value_counts.items() if v == 2][0]
                return (7, f"Full House, {value_names[three]} over {value_names[pair]}", 
                        [f"{three}{s}" for s in suits if f"{three}{s}" in cards] +
                        [f"{pair}{s}" for s in suits if f"{pair}{s}" in cards])
    
            # Couleur (6)
            if max(suit_counts.values()) >= 5:
                suit = max(suit_counts, key=suit_counts.get)
                flush_cards = sorted([card for card in cards if card[1] == suit], 
                                   key=lambda x: value_map[x[0]], reverse=True)[:5]
                high_card = flush_cards[0][0]
                return (6, f"Flush, {value_names[high_card]} high", flush_cards)
    
            # Quinte (5)
            unique_values = sorted(set(num_values), reverse=True)
            for i in range(len(unique_values) - 4):
                if unique_values[i] - unique_values[i + 4] == 4 and len(set(unique_values[i:i+5])) == 5:
                    high_card = list(value_map.keys())[list(value_map.values()).index(unique_values[i])]
                    return (5, f"Straight, {value_names[high_card]} high", 
                            [f"{k}{s}" for k, v in value_map.items() for s in suits 
                             if v in unique_values[i:i+5] and f"{k}{s}" in cards])
            # Cas spécial : quinte à l'As (As bas)
            if set([14, 5, 4, 3, 2]).issubset(set(num_values)):
                return (5, "Straight, Five high", 
                        [f"{k}{s}" for k, v in value_map.items() for s in suits 
                         if v in [14, 5, 4, 3, 2] and f"{k}{s}" in cards])
    
            # Brelan (4)
            if 3 in value_counts.values():
                three = [k for k, v in value_counts.items() if v == 3][0]
                kickers = sorted([v for v in num_values if v != value_map[three]], reverse=True)[:2]
                kicker_cards = [k for k, v in value_map.items() if v in kickers]
                return (4, f"Three of a Kind, {value_names[three]}", 
                        [f"{three}{s}" for s in suits if f"{three}{s}" in cards] +
                        [f"{k}{s}" for k in kicker_cards for s in suits if f"{k}{s}" in cards])
    
            # Double Paire (3)
            pairs = [k for k, v in value_counts.items() if v == 2]
            if len(pairs) >= 2:
                pairs = sorted(pairs, key=lambda x: value_map[x], reverse=True)[:2]
                kicker = max([v for v in num_values if v not in [value_map[p] for p in pairs]])
                kicker_card = list(value_map.keys())[list(value_map.values()).index(kicker)]
                return (3, f"Two Pair, {value_names[pairs[0]]} and {value_names[pairs[1]]}", 
                        [f"{p}{s}" for p in pairs for s in suits if f"{p}{s}" in cards] +
                        [f"{kicker_card}{s}" for s in suits if f"{kicker_card}{s}" in cards])
    
            # Paire (2)
            if 2 in value_counts.values():
                pair = [k for k, v in value_counts.items() if v == 2][0]
                kickers = sorted([v for v in num_values if v != value_map[pair]], reverse=True)[:3]
                kicker_cards = [k for k, v in value_map.items() if v in kickers]
                return (2, f"Pair of {value_names[pair]}", 
                        [f"{pair}{s}" for s in suits if f"{pair}{s}" in cards] +
                        [f"{k}{s}" for k in kicker_cards for s in suits if f"{k}{s}" in cards])
    
            # Carte haute (1)
            high_cards = sorted(cards, key=lambda x: value_map[x[0]], reverse=True)[:5]
            high_card = high_cards[0][0]
            return (1, f"High Card, {value_names[high_card]}", high_cards)
    
    
