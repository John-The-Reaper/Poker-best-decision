import itertools
import random
from collections import Counter

colors = ['D', 'H', 'S', 'C']  # Diamond, Heart, Spade, Club
values = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]

VALUE_MAP = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
             'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

VALUE_NAMES = {'2': 'Twos', '3': 'Threes', '4': 'Fours', '5': 'Fives', '6': 'Sixes',
               '7': 'Sevens', '8': 'Eights', '9': 'Nines', 'T': 'Tens', 'J': 'Jacks',
               'Q': 'Queens', 'K': 'Kings', 'A': 'Aces'}


class Player:
    def __init__(self, stack, position, hand):
        self.hand = hand              # [(suit, value), (suit, value)]
        self.stack = stack
        self.position = position
        self.alive = True             # si le joueur s'est pas couché
        self.in_current_round = 0     # montant mis dans le pot cette street (pour gérer calls)
        self.total_contributed = 0    # montant total contribué sur la main

    def bet(self, amount):
        """Le joueur mise une certaine somme (renvoie ce qui est effectivement mis)."""
        amount = min(amount, self.stack)
        assert amount >= 0
        self.stack -= amount
        self.in_current_round += amount
        self.total_contributed += amount
        return amount

    def fold(self):
        """Le joueur se couche"""
        self.alive = False

    def call(self, amount_to_call):
        """Le joueur suit jusqu'à amount_to_call (en tenant compte de ce qu'il a déjà mis)."""
        need = max(0, amount_to_call - self.in_current_round)
        paid = self.bet(need)
        return paid

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

    def deal_board(self, etape=0):
        """Distribue le board; doit être appelé après avoir préparé le deck"""
        # On simule le burn et le flop/turn/river
        if etape == 0:
            # Flop : burn 1 (pop silence) puis 3 cartes
            if len(self.cards) < 4:
                raise ValueError("Not enough cards to deal flop")
            self.cards.pop()  # burn
            self.board = [self.cards.pop() for _ in range(3)]
        elif etape == 1:
            # Turn : burn 1, deal 1
            if len(self.cards) < 2:
                raise ValueError("Not enough cards to deal turn")
            self.cards.pop()
            self.board.append(self.cards.pop())
        elif etape == 2:
            # River : burn 1, deal 1
            if len(self.cards) < 2:
                raise ValueError("Not enough cards to deal river")
            self.cards.pop()
            self.board.append(self.cards.pop())
        else:
            raise ValueError("Invalid stage: etape must be 0 (flop), 1 (turn), or 2 (river)")
        return self.board


class Poker:
    def __init__(self, player):  # 'player' = notre Player (main connue)
        self.hero = player
        self.pot = 0
        self.players = []  # liste des Player (hero + adversaires)
        self.dealer = None
        # small_blind, big_blind = 10, 20  # valeurs par défaut et à ajouter
        """
        Ligne 122 à 144 :
        --> Retirer l'implémentation des joueurs et trouver un moyen de passer une liste de joueurs (ou on sera positionné comme dans la vraie partie)
        --> Faire en sorte que big blind et small blind soient passés en paramètres 
        """
        

    def add_to_pot(self, amount):
        self.pot += amount

    def get_pot(self):
        return self.pot

    def round(self, dealer: Dealer):
        """
        Simule une main complète (simplifiée) :
        - Initialise le deck (retire la main du hero pour éviter doublons)
        - Distribue 2 cartes aux adversaires
        - Simule blinds et une passe de mises par street (préflop/flop/turn/river)
        - Showdown entre joueurs restants
        """
        self.dealer = dealer
        # 1) Prépare le deck
        dealer.cards_init()
        # retire la main du hero du deck si fournie pour éviter doublons
        if self.hero.hand:
            for c in self.hero.hand:
                if c in dealer.cards:
                    dealer.cards.remove(c)
                else:
                    pass  # mismatch possible
        dealer.shuffle()

        # 2) Crée les adversaires
        opponents = []
        opp_count = max(1, dealer.players_count - 1)
        for i in range(opp_count):
            card1 = dealer.cards.pop()
            card2 = dealer.cards.pop()
            opp = Player(stack=1000, position=i + 1, hand=[card1, card2])
            opponents.append(opp)

        # Compose la liste complète de joueurs ; hero en position 0
        self.players = [self.hero] + opponents

        # reset contributions
        for p in self.players:
            p.in_current_round = 0
            p.total_contributed = 0
            p.alive = True

        # 3) Blinds (simplifié)
        small_blind = 10
        big_blind = 20
        sb_player = self.players[1] if len(self.players) > 1 else self.players[0]
        bb_player = self.players[2] if len(self.players) > 2 else (self.players[1] if len(self.players) > 1 else self.players[0])


        self.add_to_pot(sb_player.bet(small_blind))
        self.add_to_pot(bb_player.bet(big_blind))
        current_bet = big_blind
        print(f"Blinds: SB={small_blind} (P{sb_player.position}), BB={big_blind} (P{bb_player.position})")
        print(f"Pot après blinds: {self.pot}")

        # 4) Préflop
        print("=== Préflop ===")
        print(f"Hero: {self.hero.hand}")

        def betting_round(current_bet):
            """
            Tour de mise interactif :
            FO = Fold
            CH = Check
            CA = Call
            RA <montant> = Raise
            """
            for p in self.players:
                if not p.alive or p.stack <= 0:
                    continue

                print(f"\n--- Joueur {p.position} ---")
                print(f"Main: {p.hand if p is self.hero else '??'}")
                print(f"Board: {self.dealer.board}")
                print(f"Pot: {self.pot}, Mise à suivre: {current_bet}, Stack: {p.stack}, Contrib: {p.in_current_round}")

                action = input("Action (FO / CH / CA / RA <montant>): ").strip().upper()

                if action == "FO":
                    p.fold()
                    print(f"Joueur {p.position} se couche.")

                elif action == "CH":
                    if current_bet == p.in_current_round:
                        print(f"Joueur {p.position} check.")
                    else:
                        print("Check impossible, il y a une mise à suivre. -> Fold")
                        p.fold()

                elif action == "CA":
                    to_pay = current_bet - p.in_current_round
                    if to_pay > p.stack:
                        to_pay = p.stack
                    paid = p.call(to_pay)
                    self.add_to_pot(paid)
                    print(f"Joueur {p.position} call {paid}.")

                elif action.startswith("RA"):
                    try:
                        _, amount_str = action.split()
                        amount = int(amount_str)
                        need = current_bet - p.in_current_round
                        total = need + amount
                        if total > p.stack:
                            total = p.stack  # all-in si dépasse
                        paid = p.bet(total)
                        current_bet = p.in_current_round
                        self.add_to_pot(paid)
                        print(f"Joueur {p.position} raise à {p.in_current_round}.")
                    except:
                        print("Format raise invalide (ex: 'RA 50'). -> Fold")
                        p.fold()
                else:
                    print("Action inconnue -> Fold.")
                    p.fold()

            return current_bet

        # Préflop betting
        current_bet = betting_round(current_bet)

        # 5) Flop / Turn / River
        for etape in range(3):  # 0=flop,1=turn,2=river
            board = dealer.deal_board(etape)
            print(f"--- {'Flop' if etape==0 else 'Turn' if etape==1 else 'River'} ---")
            print("Board:", dealer.board)

            for p in self.players:
                p.in_current_round = 0
            current_bet = 0
            current_bet = betting_round(current_bet)

            alive_players = [p for p in self.players if p.alive]
            if len(alive_players) == 1:
                winner = alive_players[0]
                print(f"Tous les autres se sont couchés. P{winner.position} remporte {self.pot}.")
                winner.win(self.pot)
                self.pot = 0
                return

        # 6) Showdown
        alive_players = [p for p in self.players if p.alive]
        print("=== Showdown ===")
        for p in alive_players:
            print(f"Player {p.position} hand: {p.hand} -> rank: {self.hand_rank(p.hand, dealer.board)[0]}")

        best_rank = -1
        winners = []
        for p in alive_players:
            rank = self.hand_rank(p.hand, dealer.board)[0]
            if rank > best_rank:
                best_rank = rank
                winners = [p]
            elif rank == best_rank:
                winners.append(p)

        if len(winners) == 1:
            winners[0].win(self.pot)
            print(f"Player {winners[0].position} gagne le pot de {self.pot} (stack {winners[0].stack}).")
        else:
            share = self.pot // len(winners)
            for w in winners:
                w.win(share)
            print(f"Pot partagé entre {[w.position for w in winners]}, chacun reçoit {share}.")

        self.pot = 0
        return winners

    # ---------- hand_rank (copier/ton implémentation existante) ----------
    def hand_rank(self, hand, board):
        """
        Retourne la meilleure combinaison possible avec hand + board.
        Retourne un tuple (rang, description_or_cards)
        rang: 1=HighCard ... 9=StraightFlush
        """
        cards = hand + board
        if len(cards) < 5:
            return (1, cards)

        values = [card[1] for card in cards]
        suits = [card[0] for card in cards]
        num_values = [VALUE_MAP[v] for v in values]
        num_values.sort(reverse=True)

        value_counts = Counter(values)
        suit_counts = Counter(suits)

        # Straight Flush (9)
        if max(suit_counts.values()) >= 5:
            for suit in suit_counts:
                if suit_counts[suit] >= 5:
                    suit_values = sorted([VALUE_MAP[card[1]] for card in cards if card[0] == suit], reverse=True)
                    for i in range(len(suit_values) - 4):
                        if suit_values[i] - suit_values[i + 4] == 4 and len(set(suit_values[i:i+5])) == 5:
                            high_card = list(VALUE_MAP.keys())[list(VALUE_MAP.values()).index(suit_values[i])]
                            return (9, f"Straight Flush, {VALUE_NAMES[high_card]} high")
                    # wheel (A-5) flush
                    if suit_values[:5] == [14, 5, 4, 3, 2]:
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


if __name__ == "__main__":
    # Exemple d'utilisation :
    # On fixe la main du hero (connue)
    hero_hand = [('H', 'A'), ('S', 'A')]  # As de cœur + As de pique
    hero = Player(stack=1000, position=0, hand=hero_hand)

    dealer = Dealer(players_count=6)
    game = Poker(hero)
    winners = game.round(dealer)
