import itertools
import random

class Poker:
    def __init__(self, hand, board=None):
        """
        hand : list de 2 cartes -> ex: ["KH", "8S"]
        board : list de 0 à 5 cartes -> ex: ["2D", "3H", "4C"]
        """
        self.hand = hand
        self.board = board if board else []

    def card_reveal(self, card):
        """Ajoute une carte révélée au board"""
        if card not in self.board and card not in self.hand:
            self.board.append(card)

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
        value_map = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                     'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        value_names = {'2': 'Twos', '3': 'Threes', '4': 'Fours', '5': 'Fives', '6': 'Sixes',
                       '7': 'Sevens', '8': 'Eights', '9': 'Nines', 'T': 'Tens', 'J': 'Jacks',
                       'Q': 'Queens', 'K': 'Kings', 'A': 'Aces'}
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
    
    def probability(self, n_simulations=1000):
        """
        Simule des parties aléatoires pour estimer la probabilité de victoire.
        (Monte Carlo simulation)
        """
        all_cards = [r+s for r in "23456789TJQKA" for s in "HDCS"]
        used_cards = set(self.hand + self.board)
        deck = [c for c in all_cards if c not in used_cards]

        wins = 0
        for _ in range(n_simulations):
            # tirer une main adverse
            opp_hand = random.sample(deck, 2)
            # tirer les cartes manquantes du board
            missing = 5 - len(self.board)
            new_board = self.board + random.sample([c for c in deck if c not in opp_hand], missing)

            # TODO: comparer force de main (hand_rank) vs opp
            # pour l’instant : tirage au sort
            if random.random() > 0.5:
                wins += 1

        return wins / n_simulations

    def recommendation(self):
        """Donne une recommandation basique en fonction de la probabilité de gain"""
        p = self.probability()
        if p < 0.2:
            return "Fold"
        elif p < 0.4:
            return "Check"
        elif p < 0.6:
            return "Call"
        elif p < 0.8:
            return "Raise"
        else:
            return "All-in"


p1 = Poker(["KH", "8S"], ["2D", "3H", "4C", "KD"])
print(p1.hand_rank())       # pour l’instant : main brute
print(p1.probability())     # estimation Monte Carlo
print(p1.recommendation())  # suggestion
