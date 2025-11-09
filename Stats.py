import random
import json
from Deal import Deal
from utils import hand_rank
from collections import Counter

class Stat:
    def __init__(self, hand, board, pot, amount_to_call, players=None, main_character=None, stage=0, position_main_character=None, opponent_stats=None):
        """
        Récupère les données pour les calculs statistiques du poker sur les class Deal, Player, Game.
        arg: hand --> Main du joueur principal (ex. [('H', 'A'), ('D', 'K')]).
        arg: board --> Liste des cartes du board, ex. [('H', 'A'), ('D', 'K')].
        arg: pot --> Taille du pot (issu de la classe Dealer).
        arg: amount_to_call --> Montant à payer pour suivre.
        arg: players --> Liste des joueurs (objets Player) - optionnel.
        arg: main_character --> Joueur principal (objet Player) - optionnel.
        arg: stage --> Étape de la partie (0=preflop, 1=flop, 2=turn, 3=river).
        arg: position_main_character --> Position du joueur principal (ex. 'BTN', 'SB').
        arg: opponent_stats --> Statistiques adverses pour les calculs (VPIP, PFR, AF).
        """
        self.hand = hand
        self.board = board 
        self.pot = pot
        self.amount_to_call = amount_to_call
        self.players = players if players is not None else [] 
        self.main_character = main_character
        self.stage = stage
        self.opponent_stats = opponent_stats
        self.position_main_character = position_main_character
        
        # Initialisation de opp_hand avec toutes les cartes possibles pour l'adversaire
        deal = Deal()
        card_board_now = self.board.copy()
        known_cards = self.hand + card_board_now
        self.opp_hand = [card for card in deal.cards_init() if card not in known_cards]  # Toutes les cartes possibles pour l'adversaire ( donc packet - carte du board - main du joueur principal)

        # Cache pour l'équité (évite de recalculer Monte Carlo plusieurs fois)
        self._equity_cache = None

        """with open("preflop_equity.json", "r") as f:
            self.initial_equity = json.load(f)"""
        
    def opp_hand_guess(self):
        """
        Estime la main du joueur adverse en fonction de ses moove et adapte la range en conséquence.
        Elle permet de réduire le opp_hand de chaques joueurs petit à petit
        return un  dictionnaire avec les mains probables et leurs fréquences.
        """
        pass

    # -- Méthodes de calcul statistique -- #

    def pot_odds(self):
        """
        Calcule l'équité minimale nécessaire (%) pour qu'un call soit rentable, basé sur la mise à payer et la taille du pot.
        Formule : amount_to_call / (pot + amount_to_call).
        """
        if self.pot + self.amount_to_call == 0:
            return 0.0 # éviter division par zéro
        return self.amount_to_call / (self.pot + self.amount_to_call)

    def EV_call(self, equity=None):
        """
        Calcule l'espérance de valeur (EV) d'un call en jetons, sur le long terme.
        Formule : equity * (pot + amount_to_call) - (1 - equity) * amount_to_call.
        arg: equity --> Équité de la main principale contre la range adverse (optionnel, calculé si non fourni).
        """
        if equity is None:
            equity = self.get_equity()
        pot = self.pot
        return equity * (pot + self.amount_to_call) - (1 - equity) * self.amount_to_call

    def EV_call_suivi(self, equity=None):
        """
        calcule l'espérance de valeur (EV) d'un call en tenant en compte si on vous êtes payé.
        Formule : call_equity * (pot + amount_to_call) - (1 - call_equity) * amount_to_call.
        """
        if equity is None:
            equity = self.call_equity()
        pot = self.pot
        return equity * (pot + self.amount_to_call) - (1 - equity) * self.amount_to_call  
    
    def EV_bet(self, bet_size, equity=None):
        """
        Calcule l'espérance de valeur (EV) d'un bet en jetons, en tenant compte de la fold equity.
        Formule : FE * ev_if_fold + (1 - FE) * ev_if_call.
        arg: equity --> Équité précalculée (optionnel, pour éviter de recalculer Monte Carlo).
        """
        fe = self.estimate_fold_equity()
        ev_if_fold = self.pot  # on gagne le pot
        ev_if_call = self.EV_call(equity=equity) - bet_size  # on mise bet_size
        return fe * ev_if_fold + (1 - fe) * ev_if_call
    
    def EV_fold(self):
        """
        Calcule l'espérance de valeur d'un fold,  0 car aucune perte/gain supplémentaire.
        """
        return 0

    def MDF(self):
        """
        Calcule la Minimum Defense Frequency (MDF), fréquence minimale pour défendre contre un bluff.
        Formule : pot / (pot + bet).
        """
        if self.pot + self.amount_to_call == 0:
            return 1.0
        return self.pot / (self.pot + self.amount_to_call)
    
    def estimate_fold_equity(self):
        """
        Estime la fold equity (probabilité que l'adversaire se couche).
        float: Fold equity (0 à 1)
        """
        # Pour l'instant, retourne un prior basé sur MDF
        return 1 - self.MDF()
    
    def outs(self):
        """
        Calcule le nombre de cartes (outs) améliorant la main du joueur principal.
        Retourne : Nombre d'outs (int) + list des outs (cartes) et probabilité de hit au turn/rive

        prob_river = nb_outs/(cards_remaining-1)*100
        prob_turn = nb_outs/cards_remaining * 100

        prob_turn_or_river = 1 - ((cards_remaining - nb_outs) / cards_remaining) *
                           ((cards_remaining - nb_outs - 1) / (cards_remaining - 1))
        """
        outs_list = []

        card_board_now = self.board.copy()  # carte du board actuel en copy pour pas sup
        known_cards = self.hand + card_board_now
        
        # Récupération de toutes les cartes depuis Deal
        deal = Deal()
        all_cards = deal.cards_init()
        available_cards = [card for card in all_cards if card not in known_cards]  # cartes disponibles qui sont inconnues (ni board ni hand)
        value_hand = hand_rank(self.hand, card_board_now)[0]  # valeur actuelle de la main

        for card in available_cards:
            new_board = card_board_now + [card]  # pour ne pas écraser self.board()
            new_score = hand_rank(self.hand, new_board)[0]  # recupère le rang de la main avec la nouvelle carte ajoutée au board
            
            if new_score > value_hand:
                outs_list.append(card)

        nb_outs = len(outs_list)
        cards_remaining = 52 - len(known_cards)  # 2 cartes en main + cartes du board

        # probabilité de toucher au turn ou à la river ou rien si pas de cartes restantes
        if cards_remaining > 0:
            prob_miss_turn = (cards_remaining - nb_outs) / cards_remaining
            prob_miss_river = (cards_remaining - nb_outs - 1) / (cards_remaining - 1) if cards_remaining > 1 else 1
            prob_turn_or_river = (1 - prob_miss_turn * prob_miss_river) * 100
        else:
            prob_turn_or_river = 0

        return nb_outs, outs_list, round(prob_turn_or_river, 2)
    
    def get_equity(self, num_simulations=10000):
        """
        Récupère l'équité (avec cache pour éviter de recalculer).
        Si l'équité a déjà été calculée, retourne la valeur en cache.
        Sinon, calcule via Monte Carlo et met en cache.
        """
        if self._equity_cache is None:
            self._equity_cache = self.Monte_Carlo(num_simulations)
        return self._equity_cache

    def Monte_Carlo(self, num_simulations):
        """
        Calcule l'équité via simulation Monte Carlo.
        arg: num_simulations --> Nombre de simulations à effectuer.
        return: Équité (float entre 0 et 1).
        """
        win = 0
        tie = 0

        card_board_now = self.board.copy()  # carte du board actuel copy pour pas sup primer les cartes du board original
        known_cards = self.hand + card_board_now

        # Récupération de toutes les cartes depuis Deal
        deal = Deal()
        all_cards = deal.cards_init()
        available_cards = [card for card in all_cards if card not in known_cards]  # cartes disponibles qui sont inconnues (ni board ni hand)

        for i in range(num_simulations):
            sim_available = available_cards.copy()
            random.shuffle(sim_available)  # mélange les cartes disponibles
            opp_hand = [sim_available.pop(), sim_available.pop()]  # en perdant deux cartes dans le pack pour simuler une main adverse et on supprime ces cartes du pack

            cards_needed = 5 - len(card_board_now)  # nombre de cartes à tirer pour compléter le board
            final_board = card_board_now + [sim_available.pop() for _ in range(cards_needed)]  # complète le board pour avoir les 5 cartes du board finale 
                                                                                               # (bien sur en se limitant au nombre de cartes déjà sur le board)

            # en évalue les mains 
            hero_rank = hand_rank(self.hand, final_board)
            villain_rank = hand_rank(opp_hand, final_board)

            # on compare les résultats
            test_btw_hands = hero_rank[0]
            test_btw_opp = villain_rank[0]

            if test_btw_hands > test_btw_opp:
                win += 1
            elif test_btw_hands == test_btw_opp:
                tie += 1
                
        return (win + tie / 2) / num_simulations  # en retourne l'équité estimée
    
    def call_equity(self):
        """
        Équité conditionnelle : seulement les mains qui calleraient.
        """
        # Pour l'instant, retourne l'équité Monte Carlo standard
        # À améliorer avec range manager
        return self.get_equity()

    """
    Gère les ranges des joueurs pour les calculs statistiques : stockage et réduction des combos probables.
    """

    def apply_action(self, action, sizing, board):
        """
        Réduit la range d'un joueur selon son action (bet/call/raise/fold) et le sizing, en fonction du board.
        """
        pass

    """
    Enregistre les calculs statistiques (FE, EV, équité) pour audit et analyse.
    """
    def log_decision(self):
        """
        Sauvegarde les données statistiques calculées (JSON, fichier texte, etc.).
        arg: hand_id --> Identifiant unique de la main.
        arg: context --> Contexte du jeu (ex. : board, pot, ranges).
        arg: metrics --> Valeurs calculées (ex. : FE, EV, équité).
        """
        pass

    def win_chance_and_choice(self, num_simulations=100000):
        """
        Calcule l'équité et détermine l'action optimale (fold/call/bet/raise) avec le sizing optimal.
        arg: num_simulations --> Nombre de simulations Monte Carlo (par défaut 100000 pour précision).
        return: (equity, action, sizing)
        """
        # Calcul de l'équité UNE SEULE FOIS avec un nombre élevé de simulations
        equity = self.Monte_Carlo(num_simulations)
        
        # Calculs avec les fonctions précédentes (en passant l'équité pour éviter recalcul)
        pot_odds = self.pot_odds()
        mdf = self.MDF()

        # Calculer les EV pour chaque action
        ev_fold = self.EV_fold()  # Toujours 0
        ev_call = self.EV_call(equity=equity)  # Passe l'équité précalculée

        # Si équité < pot odds, fold est optimal (call serait -EV)
        if equity < pot_odds:
            return equity, 'fold', 0

        # Si équité >= pot odds mais pas assez forte pour bet
        # Call si : pot_odds <= equity < (pot_odds + 0.15)
        if pot_odds <= equity < (pot_odds + 0.15):
            return equity, 'call', self.amount_to_call

        # Si équité forte, on cherche le sizing optimal
        # Tester différents sizings (% du pot)
        bet_sizings = [0.33, 0.5, 0.66, 0.75, 1.0, 1.5, 2.0]  # Ratios du pot
        best_ev = ev_call
        best_sizing = 0
        best_action = 'call'

        for sizing_ratio in bet_sizings:
            bet_amount = self.pot * sizing_ratio

            # Limiter au stack disponible si main_character existe
            if self.main_character and hasattr(self.main_character, 'stack'):
                bet_amount = min(bet_amount, self.main_character.stack)

            # Calculer l'EV de ce bet (en passant l'équité précalculée)
            ev_bet = self.EV_bet(bet_amount, equity=equity)

            # Si cet EV est meilleur, on le garde
            if ev_bet > best_ev:
                best_ev = ev_bet
                best_sizing = bet_amount
                best_action = 'bet' if self.amount_to_call == 0 else 'raise'

        # --- AJUSTEMENT SELON EQUITY vs MDF ---
        # Plus l'équité dépasse le MDF, plus on peut bet agressivement
        equity_over_mdf = equity - mdf

        if equity_over_mdf > 0.3:
            # Équité très forte (>30% au-dessus de MDF) : bet gros
            optimal_sizing = self.pot * min(1.5, 0.5 + equity_over_mdf * 2)

        elif equity_over_mdf > 0.2:
            # Équité forte (20-30% au-dessus) : bet pot
            optimal_sizing = self.pot * 1.0

        elif equity_over_mdf > 0.1:
            # Équité moyenne-forte (10-20% au-dessus) : bet 2/3 pot
            optimal_sizing = self.pot * 0.66

        else:
            # Équité juste au-dessus de MDF : bet petit (1/3 pot) ou call
            if best_action in ['bet', 'raise']:
                optimal_sizing = self.pot * 0.33
            else:
                return equity, 'call', self.amount_to_call

        # Limiter au stack disponible si main_character existe
        if self.main_character and hasattr(self.main_character, 'stack'):
            optimal_sizing = min(optimal_sizing, self.main_character.stack)

        # Arrondir à l'entier le plus proche
        optimal_sizing = round(optimal_sizing)

        # Vérifier que le bet optimal a un meilleur EV que call (en passant l'équité précalculée)
        ev_optimal = self.EV_bet(optimal_sizing, equity=equity)

        if ev_optimal > ev_call:
            action = 'bet' if self.amount_to_call == 0 else 'raise'
            return equity, action, optimal_sizing
        else:
            # Si bet n'est pas meilleur, on call
            return equity, 'call', self.amount_to_call
