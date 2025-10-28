from poker import Player,Deal
import json
class Stat:
    def __init__(self, players, board, main_character, pot, ranges, amount_to_call=0, stage=0, opponent_stats=None):
        """
        Initialise les données pour les calculs statistiques du poker.
        arg: players --> Liste des stacks et positions des adversaires (issus de la classe Player).
        arg: board --> Liste des cartes du board, ex. [("♥️", "A")].
        arg: main_character --> Joueur principal (objet Player).
        arg: pot --> Taille du pot (issu de la classe Dealer).
        arg: ranges --> Dictionnaire des ranges probables des adversaires, ex. {player: [(main, proba), ...]}.
        arg: amount_to_call --> Montant à payer pour suivre.
        arg: stage --> Étape de la partie (0=flop, 1=turn, 2=river).
        arg: opponent_stats --> Dictionnaire des statistiques adverses (VPIP, PFR, AF) pour les calculs.
        """
        self.players = [player for player in players if player.stack > 0]
        self.board = board
        self.main_character = main_character
        self.pot = pot
        self.ranges = ranges
        self.amount_to_call = amount_to_call
        self.stage = stage
        self.opponent_stats = opponent_stats

        with open("preflop_equity.json", "r") as f:
            self.initial_equity = json.load(f)
        


    def pot_odds(self):
        """
        Calcule l'équité minimale nécessaire (%) pour qu'un call soit rentable, basé sur la mise à payer et la taille du pot.
        Formule : amount_to_call / (pot + amount_to_call).
        """
        return self.amount_to_call / (self.pot + self.amount_to_call)
    
    def equity(self,player):
        """
        Calcule l'équité de la main du joueur principal contre les ranges adverses, en utilisant Monte-Carlo ou combinatoire.
        """
        if self.stage == 0:  #Preflop
            hand = self.hand_to_string(self.main_character.hands)
            if player in self.ranges and hand in self.initial_equity:
                total_equity = 0
                total_proba = 0
                for opp_hand, prob in self.ranges[player]:
                    opp_hand = self.hand_to_string(opp_hand)    
                    if opp_hand in self.initial_equity[hand]:
                        total_equityequity += self.initial_equity[hand][opp_hand] * prob
                        total_proba += prob
                        pass
            
        

    def EV_call(self,player):
        """
        Calcule l'espérance de valeur (EV) d'un call en jetons, sur le long terme.
        Formule : equity * (pot + amount_to_call) - (1 - equity) * amount_to_call.
        arg: equity --> Équité de la main principale contre la range adverse.
        """
        equity = self.equity(player)
        pot = self.poker.pot
        return equity * (pot + self.amount_to_call) - (1 - equity) * self.amount_to_call

    def EV_bet(self):
        """
        Calcule l'espérance de valeur d'un bet (ou bluff) en fonction du pot, de l'EV_call et de la fold equity.
        Formule : FE * pot + (1 - FE) * EV_call.
        """
        fe = self.estimate_fold_equity()
        
        return fe * self.pot + (1 - fe ) * self.EV_call()
    

    
    def EV_fold(self):
        """
        Calcule l'espérance de valeur d'un fold, généralement 0 car aucune perte/gain supplémentaire.
        """
        pass

    def MDF(self):
        """
        Calcule la Minimum Defense Frequency (MDF), fréquence minimale pour défendre contre un bluff.
        Formule : pot / (pot + bet).
        """
        return self.pot / (self.pot + self.amount_to_call)
    
    def outs(self,hand,board,value_hand):
        """
        Calcule le nombre de cartes (outs) améliorant la main du joueur principal.
        Retourne : Nombre d'outs (int) + list des outs (cartes) et probabilité de hit au turn/river.
        """
        outs_list = []  
        for card in Deal.card_init() - self.card_board():
            new_board = self.board().append(card).copy() # pour ne pas écraser self.board()
            new_score = self.evaluate(hand,new_board) # à implémenter dans une autre class
            if new_score > value_hand:
                outs_list.append(card)

        nb_outs = len(outs_list)
        cards_remaining = 52 - (2 + len(board))

        prob_turn = nb_outs/cards_remaining * 100
        prob_river = nb_outs/(cards_remaining-1)*100

        return (nb_outs,outs_list,prob_river,prob_turn)
    

    

    def Monte_Carlo(self,num_simulations, simulate_hand):
        """
        Effectue une simulation Monte-Carlo pour estimer l'équité ou autres probabilités via des tirages aléatoires de cartes.
        """
        win = 0  # bien test voire le recoder c'est juste le lien logique du programme 
        for i in range(num_simulations):
            if simulate_hand == self.outs(): 
                win += 1
        return win / num_simulations



    
    

    def estimate_fold_equity(self):
        """
        Estime la fold equity (probabilité que l'adversaire se couche)
        Args:
            player: Objet Player (adversaire)
            bet_size: Taille de la mise
        Returns:
            float: Fold equity (0 à 1)
        """
        pass
        


class RangeManager:
    """
    Gère les ranges des joueurs pour les calculs statistiques : stockage et réduction des combos probables.
    """
    def __init__(self, ranges):
        """
        Initialise avec les ranges des adversaires, ex. {player: [('AKs', 0.8), ...]}.
        """
        pass

    def apply_action(self, action, sizing, board):
        """
        Réduit la range d'un joueur selon son action (bet/call/raise/fold) et le sizing, en fonction du board.
        """
        pass

    def get_distribution(self):
        """
        Retourne la répartition actuelle des combos (ex. : probabilités pondérées).
        """
        pass

class EquityEngine:
    """
    Calcule l'équité d'une main ou range contre une autre pour les décisions basées sur l'EV.
    """
    def compute_equity(self, hero_range, villain_range, board):
        """
        Calcule l'équité via méthode combinatoire (exacte) ou Monte-Carlo (approximative).
        arg: hero_range --> Range ou main du joueur principal.
        arg: villain_range --> Range de l'adversaire.
        arg: board --> Cartes du board.
        """
        pass

class FoldEquityEstimator:
    """
    Estime la probabilité qu’un adversaire se couche face à un bet, pour les calculs d'EV.
    """
    def estimate_prior(self, pot, bet):
        """
        Calcule la fold equity via un prior théorique (MDF).
        Formule : 1 - (pot / (pot + bet)).
        """
        return 1 - (pot/ (pot + bet))

    def estimate_range_based(self, villain_range, board, sizing):
        """
        Estime la fold equity en comptant les combos qui foldent vs continuent dans la range adverse.
        """
        pass

class UncertaintyManager:
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

class SizingOptimizer:
    """
    Optimise la taille des mises en calculant l'EV pour différentes options.
    """
    def select_best_sizing(self, pot, hero_range, villain_range, board, fe_estimator):
        """
        Teste plusieurs tailles de mise (ex. : 1/3 pot, 1/2 pot, shove) et retourne celle avec le meilleur EV.
        """
        pass

class EVSimulator:
    """
    Calcule l'EV d'un call en tenant compte du pot futur et de l'équité.
    """
    def compute_ev_call(self, hero_range, villain_range, board, pot, bet):
        """
        Estime l'EV si l'adversaire call, en utilisant l'équité et le pot futur.
        arg: hero_range --> Range ou main du joueur principal.
        arg: villain_range --> Range de l'adversaire.
        arg: board --> Cartes du board.
        arg: pot --> Taille actuelle du pot.
        arg: bet --> Mise proposée.
        """
        pass

class MultiwayHandler:
    """
    Gère les calculs statistiques pour les pots multi-joueurs.
    """
    def combine_fe(self, fe_list):
        """
        Combine les fold equities individuelles pour une probabilité globale de fold.
        Formule : FE_global = 1 - ∏(1 - FE_i).
        arg: fe_list --> Liste des fold equities des adversaires.
        """
        pass

class Logger:
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


# idée  gestions de l'incertitude + dictionnaire des données avec un tableau



