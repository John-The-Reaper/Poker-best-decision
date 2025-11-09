from collections import Counter

def hand_rank( hand, board):
        """
        Retourne la meilleure combinaison possible avec hand + board en lui attribuant une valeur numérique (1-9)
        """
        value_list = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]

        cards = hand + board
        if len(cards) < 5: # Comme la fonction est utilisée à la fin
            return (1, cards)

        value_map = {v: i+2 for i, v in enumerate(value_list)}
        suits = [card[0] for card in cards]
        values = [card[1] for card in cards]
        num_values = [value_map[v] for v in values]
        num_values.sort(reverse=True)

        value_counts = Counter(values)
        suit_counts = Counter(suits)

        # Straight Flush (9)
        if max(suit_counts.values()) >= 5:
            for suit in suit_counts:
                if suit_counts[suit] >= 5:
                    suit_num_values = sorted([value_map[card[1]] for card in cards if card[0] == suit], reverse=True)
                    for i in range(len(suit_num_values) - 4):
                        if suit_num_values[i] - suit_num_values[i + 4] == 4 and len(set(suit_num_values[i:i+5])) == 5:
                            high_card = value_list[suit_num_values[i] - 2]
                            return (9, f"Straight Flush, {high_card} high")
                    if set([14, 5, 4, 3, 2]).issubset(set(suit_num_values)):
                        return (9, "Wheel Straight Flush (A-5)")

        # Four of a kind (8)
        for value, count in value_counts.items():
            if count == 4:
                return (8, f"Four of a kind {value}")

        # Full House (7)
        if 3 in value_counts.values() and 2 in value_counts.values():
            return (7, "Full House")

        # Flush (6)
        if max(suit_counts.values()) >= 5:
            return (6, "Flush")

        # Straight (5)
        unique_values = sorted(set(num_values), reverse=True)
        for i in range(len(unique_values) - 4):
            if unique_values[i] - unique_values[i + 4] == 4 and len(set(unique_values[i:i+5])) == 5:
                return (5, "Straight")
        if set([14, 5, 4, 3, 2]).issubset(set(num_values)):
            return (5, "Wheel Straight (A-5)")

        # Three of a kind (4)
        if 3 in value_counts.values():
            return (4, "Three of a kind")

        # Two Pair (3)
        if len([k for k, v in value_counts.items() if v == 2]) >= 2:
            return (3, "Two pair")

        # One Pair (2)
        if 2 in value_counts.values():
            return (2, "One pair")

        # High card (1)
        return (1, "High card")
