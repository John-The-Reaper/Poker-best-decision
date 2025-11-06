from players.calling_station import Calling_station
from players.tag import Tag
from players.lag import Lag
from players.maniac import Maniac 
from players.nit import Nit
from Stats import Stat
from deal import Deal
from collections import Counter

import json 

class Game:
    def __init__(self, big_blind=50, small_blind=25, stack=1000):
        """
        Initalisation de toute les classes joueurs
        """
        self.dealer = Deal()
        self.players = [] # Tableau contenant les noms des joueurs
        self.state = self.dealer.state
        self.big_blind = big_blind
        self.small_blind = small_blind  
        self.pot = 0
        self.stak = stack

        # nom_du_player, big_blind, small_blind, self.stack, self.dealer.deal_player_hand()
        self.calling_station = Calling_station()
        self.tag = Tag()
        self.lag = Lag()
        self.maniac = Maniac()
        self.nit = Nit()

        self.board = [self.deal.deal_board()]

    def game(self):
        """
        Génère le déroulement complte de la partie et renvoie un dataframe des données de la partie
        Renvoie à la class Stat : 
        - self.board
        - self.player.hand
        - self.player.position
        - self.pot
        - self.state
        - amount_to_call 
        Reçoit : win_chance

        Renvoie aux joueurs : 
        - amount_to_call
        - win_rate # win rate pour la main en question
        Reçoit du joueur : {"action": amount} 
        --> Si Fold alors amount = None pareil pour check
        """    
        pass

    def simulation(n:int):
        """
        Génère une simulation de n game
        - Acutalise les positions des joueurs 
        - Augmente les blindes toute les 10 parties
        - Save les données de chque partie dans le json
        """
        

        pass

    def save_json(self, data: dict, path: str):
        """
        Sauvegarde des données de la partie dans un fichier JSON 
        ### Probablement pas nécessaire
        """
        with open(path, 'w') as json_file:
            json.dump(data, json_file)

    def hand_rank(self, hand, board):
        """
        Retourne la meilleure combinaison possible avec hand + board.
        Retourne un tuple (rang, description_or_cards)
        rang: 1=HighCard ... 9=StraightFlush
        
        """
        cards = hand + board
        if len(cards) < 5:
            return (1, cards)

        # Créer le mapping des valeurs à partir de self.values
        value_map = {v: i+2 for i, v in enumerate(self.values)}

        # Extraire couleurs et valeurs (format (color, value))
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
                            high_card = self.values[suit_num_values[i] - 2]
                            return (9, f"Straight Flush, {high_card} high")
                    # wheel (A-5) flush
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

  


