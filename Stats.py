import random
import json
from deal import Deal
from utils import hand_rank
from collections import Counter

class Stat:
    def __init__(self, board, pot, amount_to_call, hand, stage, main_character=None, players=None, position_main_character=None, opponent_stats=None):
        """
        Récupère les données pour les calculs statistiques du poker sur les class Deal, Player, Game.
        arg: players --> Liste des stacks et positions des adversaires (issus de la ).
        arg: board --> Liste des cartes du board, ex. [('H', 'A'), ('D', 'K')].
        arg: main_character --> Joueur principal (objet Player).
        arg: pot --> Taille du pot (issu de la classe Game).
        arg: amount_to_call --> Montant à payer pour suivre.
        arg: hand --> Main du joueur principal (ex. [('H', 'A'), ('D', 'K')]).
        arg: stage --> Étape de la partie (0=preflop, 1=flop, 2=turn, 3=river).
        arg: opponent_stats --> Statistiques adverses pour les calculs (VPIP, PFR, AF).
        arg: position_main_character --> Position du joueur principal (ex. 'BTN', 'SB').
        arg: initial_equity --> Dictionnaire des équités préflop (chargé depuis un fichier JSON).
        """
        self.players = players
        self.board = board
        self.main_character = main_character
        self.pot = pot
        self.amount_to_call = amount_to_call
        self.hand = hand
        self.stage = stage
        self.opponent_stats = opponent_stats
        self.position_main_character = position_main_character

        """with open("preflop_equity.json", "r") as f:
            self.initial_equity = json.load(f)"""
        

    # -- Méthodes de calcul statistique -- #

    def pot_odds(self):
        """
        Calcule l'équité minimale nécessaire (%) pour qu'un call soit rentable, basé sur la mise à payer et la taille du pot.
        Formule : amount_to_call / (pot + amount_to_call).
        """
        if self.pot + self.amount_to_call == 0:
            return 0.0 # éviter division par zéro
        return self.amount_to_call / (self.pot + self.amount_to_call)

        

    def EV_call(self,opponent):
        """
        Calcule l'espérance de valeur (EV) d'un call en jetons, sur le long terme.
        Formule : equity * (pot + amount_to_call) - (1 - equity) * amount_to_call.
        arg: equity --> Équité de la main principale contre la range adverse.
        """
        equity = self.equity_range(opponent) # équité contre la range adverse
        pot = self.pot
        return equity * (pot + self.amount_to_call) - (1 - equity) * self.amount_to_call

    def EV_call_suivi(self,player):
        """
        calcule l'espérance de valeur (EV) d'un call en tenant en compte si on vous êtes payé.
        Formule : call_equity * (pot + amount_to_call) - (1 - call_equity) * amount_to_call.
        """
        call_equity = self.call_equity(player)
        pot = self.pot
        return call_equity * (pot + self.amount_to_call) - (1 - call_equity) * self.amount_to_call  
    
    def EV_bet(self, bet_size, opponent):
        """
        Calcule l'espérance de valeur (EV) d'un bet en jetons, en tenant compte de la fold equity.
        Formule : FE * ev_if_fold + (1 - FE) * ev_if_call.
        """
        fe = self.estimate_fold_equity(opponent)
        ev_if_fold = self.pot  # on gagne le pot
        ev_if_call = self.EV_call(opponent) - bet_size  # on mise bet_size
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
    
    
    
    def outs(self,hand,value_hand):
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
        known_cards = hand + card_board_now
        
        # Récupération de toutes les cartes depuis Deal
        deal = Deal()
        all_cards = deal.cards_init()
        available_cards = [card for card in all_cards if card not in known_cards]  # cartes disponibles qui sont inconnues (ni board ni hand) !!!!!!! remplacer self.hand

        # initialiser une instance de Game pour utiliser hand_rank


        for card in available_cards:
            new_board = card_board_now + [card] # pour ne pas écraser self.board()
            new_score = hand_rank(self.hand, new_board)[0] # recupère le rang de la main avec la nouvelle carte ajoutée au board
            
            
            if new_score > value_hand:
                outs_list.append(card)

        nb_outs = len(outs_list)
        cards_remaining = 52 - len(known_cards) # 2 cartes en main + cartes du board

        # probabilité de toucher au turn ou à la river ou rien si pas de cartes restantes
        if cards_remaining > 0:
            prob_miss_turn = (cards_remaining - nb_outs) / cards_remaining
            prob_miss_river = (cards_remaining - nb_outs - 1) / (cards_remaining - 1) if cards_remaining > 1 else 1
            prob_turn_or_river = (1 - prob_miss_turn * prob_miss_river) * 100
        else:
            prob_turn_or_river = 0

        return nb_outs, outs_list, round(prob_turn_or_river, 2)
    

    

    def Monte_Carlo(self,num_simulations,opp_hand):
       
        win = 0
        tie = 0

        card_board_now = self.board.copy() # carte du board actuel copy pour pas sup primer les cartes du board original
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

            # en évalue les mains des joueurs avec hand_rank
            hero_rank = hand_rank(self.hand, final_board)
            villain_rank = hand_rank(opp_hand, final_board)
            # on compare les résultats
            test_btw_hands = hero_rank[0]
            test_btw_opp = villain_rank[0]

            if test_btw_hands > test_btw_opp:
                win += 1
            elif test_btw_hands == test_btw_opp:
                tie += 1
        return  (win + tie) / num_simulations # en retourne l'équité estimée
    


    def equity_range(self, player,num_simulations=1000000):
        """
        Calcule l'équité de la main du joueur principal contre les ranges adverses, en utilisant Monte-Carlo ou combinatoire.
        """
        return self.Monte_Carlo(num_simulations, player)

        
    def call_equity(self, player):
        """
        Équité conditionnelle : seulement les mains qui calleraient.
        """
        return self.equity_range(player) # plus tard utilisation de range manager pour savoir quelles mains calleraient


    def estimate_fold_equity(self):
        """
        Estime la fold equity (probabilité que l'adversaire se couche)
        Args:
            player: Objet Player (adversaire)
            bet_size: Taille de la mise
        Returns:
            float: Fold equity (0 à 1)

        prior théorique basé sur MDF (Minimum Defense Frequency)
        formule : FE = 1 - MDF = 1 - (pot / (pot + bet)) -> bet / (pot + bet)
        """
        if self.pot + self.amount_to_call == 0:
            return 0.0 # éviter division par zéro
        return self.amount_to_call / (self.pot + self.amount_to_call)
        



    """
    Gère les ranges des joueurs pour les calculs statistiques : stockage et réduction des combos probables.
    """

    def apply_action(self, action, sizing, board):
        """
        Réduit la range d'un joueur selon son action (bet/call/raise/fold) et le sizing, en fonction du board.
        """
        

    def get_distribution(self):
        """
        Retourne la répartition actuelle des combos (ex. : probabilités pondérées).
        """
        pass

    def compute_equity(self, hero_range, villain_range, board):
        """
        Calcule l'équité d'une main ou range contre une autre pour les décisions basées sur l'EV.
        Calcule l'équité via méthode combinatoire (exacte) ou Monte-Carlo (approximative).
        arg: hero_range --> Range ou main du joueur principal.
        arg: villain_range --> Range de l'adversaire.
        arg: board --> Cartes du board.
        """
        pass

    """
    Fournit des intervalles de confiance pour les estimations statistiques (ex. : fold equity).
    """
    def compute_confidence_interval(self, alpha, beta):
        """
        Calcule un intervalle de confiance pour la fold equity via la variance de la loi Beta.
        arg: alpha --> Nombre d'observations de folds.
        arg: beta --> Nombre d'observations de non-folds.
        """
        pass

    def backoff_to_prior(self, fe_estimate, n_obs):
        """
        Retourne un prior (ex. : MDF) si le nombre d'observations est insuffisant.
        arg: fe_estimate --> Estimation actuelle de la fold equity.
        arg: n_obs --> Nombre d'observations.
        """
        pass


    """
    Optimise la taille des mises en calculant l'EV pour différentes options.
    """
    def select_best_sizing(self, pot, hero_range, villain_range, board, fe_estimator):
        """
        Teste plusieurs tailles de mise (ex. : 1/3 pot, 1/2 pot, shove) et retourne celle avec le meilleur EV.
        """
        pass


    """
    Calcule l'EV d'un call en tenant compte du pot futur et de l'équité.
    """
    def compute_ev_call(self, hero_range, villain_range, board, pot, bet):
        """
        Calcule l'EV d'un call en tenant compte du pot futur et de l'équité.
        Estime l'EV si l'adversaire call, en utilisant l'équité et le pot futur.
        arg: hero_range --> Range ou main du joueur principal.
        arg: villain_range --> Range de l'adversaire.
        arg: board --> Cartes du board.
        arg: pot --> Taille actuelle du pot.
        arg: bet --> Mise proposée.
        """
        pass

    def combine_fe(self, fe_list):
        """
        Combine les fold equities individuelles pour une probabilité globale de fold.
        Formule : FE_global = 1 - ∏(1 - FE_i).
        arg: fe_list --> Liste des fold equities des adversaires.
        """
        pass


    """
    Enregistre les calculs statistiques (FE, EV, équité) pour audit et analyse.
    """
    def log_decision(self, hand_id, context, metrics):
        """
        Sauvegarde les données statistiques calculées (JSON, fichier texte, etc.).
        arg: hand_id --> Identifiant unique de la main.
        arg: context --> Contexte du jeu (ex. : board, pot, ranges).
        arg: metrics --> Valeurs calculées (ex. : FE, EV, équité).
        """
        pass


    def win_chance_and_choice(self, hand, board, players, num_simulations=1000000):
    
        # Calculs avec les fonctiosn précédentes
        equity = self.equity_range(players,num_simulations)
        pot_odds = self.pot_odds()
        mdf = self.MDF()

        # Calculer les EV pour chaque action
        ev_fold = self.EV_fold()  # Toujours 0
        ev_call = self.EV_call(players)

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

            # Limiter au stack disponible
            if hasattr(self, 'stack'):
                bet_amount = min(bet_amount, self.stack)

            # Calculer l'EV de ce bet
            ev_bet = self.EV_bet(bet_amount, players)

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

        # Limiter au stack disponible
        if hasattr(self, 'stack'):
            optimal_sizing = min(optimal_sizing, self.stack)

        # Arrondir à l'entier le plus proche
        optimal_sizing = round(optimal_sizing)

        # Vérifier que le bet optimal a un meilleur EV que call
        ev_optimal = self.EV_bet(optimal_sizing, players)

        if ev_optimal > ev_call:
            action = 'bet' if self.amount_to_call == 0 else 'raise'
            return equity, action, optimal_sizing
        else:
            # Si bet n'est pas meilleur, on call
            return equity, 'call', self.amount_to_call
