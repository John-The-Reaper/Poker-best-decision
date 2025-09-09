import itertools
import random
from collections import Counter

colors = ['D', 'H', 'S', 'C'] # les émojis peuvent avoir des pb ducoup faudra juste jeter un oeil pour mettre les emojis à l'affichage en fonction de la lettre qui sort
values = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]

# Constantes de classe pour éviter la redondance
VALUE_MAP = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
             'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

VALUE_NAMES = {'2': 'Twos', '3': 'Threes', '4': 'Fours', '5': 'Fives', '6': 'Sixes',
               '7': 'Sevens', '8': 'Eights', '9': 'Nines', 'T': 'Tens', 'J': 'Jacks',
               'Q': 'Queens', 'K': 'Kings', 'A': 'Aces'}

class Player:
    def __init__(self, stack, position, hands=None):
        self.hands = hands if hands is not None else []
        self.stack = stack
        self.position = position

    def bet(self, amount):
        """Le joueur mise une certaine somme"""
        assert amount <= self.stack, "Le joueur ne peut pas miser plus que son stack"
        self.stack -= amount
        return amount

    def fold(self):
        """Le joueur se couche"""
        pass

    def call(self, amount):
        """Le joueur suit une mise"""
        assert amount <= self.stack, "Le joueur ne peut pas suivre plus que son stack"
        self.stack -= amount
        return amount

    def win(self, pot):
        """Le joueur gagne une certaine somme"""
        self.stack += pot

class Dealer:
    def __init__(self, players_count=6):
        self.players_count = players_count
        self.cards = []
        self.board = []

    def cards_init(self):
        """Initialise le paquet de cartes"""
        self.cards = [(color, value) for color in colors for value in values]

    def shuffle(self):
        random.shuffle(self.cards)

    def hands(self):
        """Distribue les mains aux joueurs"""
        self.cards_init()
        self.shuffle()
        hands = []
        for i in range(self.players_count):
            hands.append(Player(1000, i, [self.cards.pop(), self.cards.pop()]))
        return hands

    def deal_board(self, etape=0):
        """Distribue le board, doit impérativement être appelé après hands()"""
        if len(self.cards) < (4 if etape == 0 else 2 if etape == 1 else 1):
            raise ValueError("Not enough cards in the deck to deal the board")
        if etape == 0:
            # Flop
            self.board = [self.cards.pop() for _ in range(3)]
            if self.cards:  # Burn a card if deck is not empty
                self.cards.pop()
        elif etape == 1:
            # Turn
            self.board.append(self.cards.pop())
            if self.cards:  # Burn a card if deck is not empty
                self.cards.pop()
        elif etape == 2:
            # River
            self.board.append(self.cards.pop())
        else:
            raise ValueError("Invalid stage: etape must be 0 (flop), 1 (turn), or 2 (river)")
        return self.board

class Poker:
    def __init__(self, players=None):
        self.players = players if players is not None else []
        self.pot = 0

    def add_to_pot(self, amount):
        """Ajoute une mise au pot"""
        self.pot += amount

    def pot(self):
        """Retourne la taille du pot (à implémenter pleinement)"""
        return self.pot

    def round(self):
        """Gère un tour de jeu complet (à implémenter)"""
        pass

    def winner(self,board): # marche dans l'idée je pense mais pas fais de test le pb vient de fhand rank qui est inconpatible avec elle pour l'instant du au tuple
        """Détermine le gagnant du pot (à implémenter)"""
        
        best_rank = 0
        winners = []

        for player in self.players:
            rank = self.hand_rank(player.hands,board)[0] # détermine un rank en fonction des cartes de la main du joueur et le board pour carrect dons l'état à cause du tuple

            if rank > best_rank:
                best_rank = rank
                winners = [player]

            elif rank == best_rank:
                winners.append(player)

        if len(winners) > 1:
            split = self.pot // len(winners) # split le pot en fonction du nombre de joueur mais manque de détail (ex: si on mise plus que l'adversaire on  doit recevoir autant de jeton miser facile à faire mais juste flemme il est tard ect) ( à revoir)
            for winner in winners:
                winner.win(split) 
            self.pot = 0

        return winners


    def hand_rank(self, hand, board): # la fonction est un peu trop pointu je pense il faut mieux là rendre plus simple avec juste un return  d'un valeur 1 à 9 en fonction de la valeur de la main et quand on aura bvesoin d'afficher deux pair ect il faudrait le faire après parce que sinon à utiliser ça devient très chiant
        """
        Retourne la meilleure combinaison possible avec hand + board.
        Retourne un tuple (rang, description, cartes) où rang est un entier (1=plus faible, 9=plus fort)
        """
        cards = hand + board
        if len(cards) < 5:
            return (1, cards)

        # Extraire valeurs et couleurs
        values = [card[1] for card in cards]  # card[1] = valeur
        suits = [card[0] for card in cards]   # card[0] = couleur
        num_values = [VALUE_MAP[v] for v in values]
        num_values.sort(reverse=True)

        # Compter les occurrences des valeurs et couleurs
        value_counts = Counter(values)
        suit_counts = Counter(suits)

        # Quinte Flush (9)
        if max(suit_counts.values()) >= 5:
            for suit in suit_counts:
                if suit_counts[suit] >= 5:
                    suit_values = sorted([VALUE_MAP[card[1]] for card in cards if card[0] == suit], reverse=True)
                    for i in range(len(suit_values) - 4):
                        if suit_values[i] - suit_values[i + 4] == 4 and len(set(suit_values[i:i+5])) == 5:
                            high_card = list(VALUE_MAP.keys())[list(VALUE_MAP.values()).index(suit_values[i])]
                            return (9, f"Straight Flush, {VALUE_NAMES[high_card]} high", 
                                    [(suit, v) for v in [list(VALUE_MAP.keys())[list(VALUE_MAP.values()).index(val)] 
                                                        for val in suit_values[i:i+5]]])
                        # Cas spécial : quinte flush à l'As (As bas)
                        if suit_values[:5] == [14, 5, 4, 3, 2]:
                            return (9, [(suit, v) for v in ['A', '5', '4', '3', '2']])

        # Carré (8)
        for value, count in value_counts.items():
            if count == 4:
                kicker = max([v for v in num_values if v != VALUE_MAP[value]])
                kicker_card = list(VALUE_MAP.keys())[list(VALUE_MAP.values()).index(kicker)]
                return (8, [(s, value) for s in colors if (s, value) in cards] + 
                        [(s, kicker_card) for s in colors if (s, kicker_card) in cards])

        # Full House (7)
        if 3 in value_counts.values() and 2 in value_counts.values():
            three = max([k for k, v in value_counts.items() if v == 3], key=lambda x: VALUE_MAP[x])
            pair = max([k for k, v in value_counts.items() if v == 2], key=lambda x: VALUE_MAP[x])
            return (7, [(s, three) for s in colors if (s, three) in cards] +
                    [(s, pair) for s in colors if (s, pair) in cards])

        # Couleur (6)
        if max(suit_counts.values()) >= 5:
            suit = max(suit_counts, key=suit_counts.get)
            flush_cards = sorted([card for card in cards if card[0] == suit], 
                               key=lambda x: VALUE_MAP[x[1]], reverse=True)[:5]
            high_card = flush_cards[0][1]
            return (6, flush_cards)

        # Quinte (5)
        unique_values = sorted(set(num_values), reverse=True)
        for i in range(len(unique_values) - 4):
            if unique_values[i] - unique_values[i + 4] == 4 and len(set(unique_values[i:i+5])) == 5:
                high_card = list(VALUE_MAP.keys())[list(VALUE_MAP.values()).index(unique_values[i])]
                return (5, [(s, k) for k, v in VALUE_MAP.items() for s in colors 
                         if v in unique_values[i:i+5] and (s, k) in cards])
        # Cas spécial : quinte à l'As (As bas)
        if set([14, 5, 4, 3, 2]).issubset(set(num_values)):
            return (5, [(s, k) for k, v in VALUE_MAP.items() for s in colors 
                     if v in [14, 5, 4, 3, 2] and (s, k) in cards])

        # Brelan (4)
        if 3 in value_counts.values():
            three = max([k for k, v in value_counts.items() if v == 3], key=lambda x: VALUE_MAP[x])
            kickers = sorted([v for v in num_values if v != VALUE_MAP[three]], reverse=True)[:2]
            kicker_cards = [k for k, v in VALUE_MAP.items() if v in kickers]
            return (4, [(s, three) for s in colors if (s, three) in cards] +
                    [(s, k) for k in kicker_cards for s in colors if (s, k) in cards])

        # Double Paire (3)
        pairs = [k for k, v in value_counts.items() if v == 2]
        if len(pairs) >= 2:
            pairs = sorted(pairs, key=lambda x: VALUE_MAP[x], reverse=True)[:2]
            kicker = max([v for v in num_values if v not in [VALUE_MAP[p] for p in pairs]])
            kicker_card = list(VALUE_MAP.keys())[list(VALUE_MAP.values()).index(kicker)]
            return (3, [(s, p) for p in pairs for s in colors if (s, p) in cards] +
                    [(s, kicker_card) for s in colors if (s, kicker_card) in cards])

        # Paire (2)
        if 2 in value_counts.values():
            pair = max([k for k, v in value_counts.items() if v == 2], key=lambda x: VALUE_MAP[x])
            kickers = sorted([v for v in num_values if v != VALUE_MAP[pair]], reverse=True)[:3]
            kicker_cards = [k for k, v in VALUE_MAP.items() if v in kickers]
            return (2, [(s, pair) for s in colors if (s, pair) in cards] +
                    [(s, k) for k in kicker_cards for s in colors if (s, k) in cards])

        # Carte haute (1)
        high_cards = sorted(cards, key=lambda x: VALUE_MAP[x[1]], reverse=True)[:5]
        high_card = high_cards[0][1]
        return (1, high_cards)
    

if __name__ == "__main__":
    # Test simple : joueur avec une paire d'As
    player_hand = [("hearts", "A"), ("clubs", "A")]  # deux As
    board = [("diamonds", "K"), ("spades", "7"), ("clubs", "2"),
             ("hearts", "9"), ("spades", "4")]       # board sans danger

    poker = Poker()
    rank = poker.hand_rank(player_hand, board)

    print("Main du joueur :", player_hand)
    print("Board :", board)
    print("Résultat :", rank)


