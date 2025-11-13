import random
import json
from deal import Deal
from utils import hand_rank
from collections import Counter

class Stat:
    def __init__(self, hand, board, pot, amount_to_call, players=None, main_character=None, stage=0, position_main_character=None):
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
    
    def get_equity(self, num_simulations=500):
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


    def win_chance_and_choice(self, num_simulations=2000):
        # --- Récupération des données ---
        equity = self.get_equity(num_simulations)
        pot_odds = self.pot_odds()
        mdf = self.MDF()
        player_stack = self.main_character.stack if self.main_character else 10000
        pot = self.pot
        to_call = self.amount_to_call
        
        # --- Calcul du stack-to-pot ratio (SPR) pour adapter l'agressivité ---
        spr = player_stack / max(pot, 1)
        
        # --- Bonus d'agressivité selon la position ---
        position_aggression = {
            'BTN': 0.15,  # Bouton très agressif
            'CO': 0.12,   # Cut-off agressif
            'MP': 0.08,   # Middle position modéré
            'UTG': 0.05,  # Under the gun conservateur
            'SB': 0.10,   # Small blind agressif
            'BB': 0.07    # Big blind défensif
        }.get(self.position_main_character, 0.10)
        
        # --- Adaptation selon le stage (plus agressif postflop) ---
        stage_aggression = [0.05, 0.12, 0.15, 0.18][min(self.stage, 3)]
        
        # --- Facteur d'agressivité total ---
        aggression_factor = position_aggression + stage_aggression
        
        # --- CAS 1 : PREMIER À PARLER (Initiative) ---
        if to_call == 0:
            # Main faible → mix check/bluff avec plus de bluffs
            if equity < 0.35:
                # Plus de bluffs si bonne position ou board dangereux
                bluff_frequency = 0.25 + aggression_factor
                
                if random.random() < bluff_frequency:
                    # Bluff sizing variable selon le stage
                    if self.stage == 0:  # Preflop
                        bet_size = int(pot * random.uniform(0.60, 0.85))
                    else:  # Postflop
                        bet_size = int(pot * random.uniform(0.50, 0.75))
                    return equity, 'bet', min(bet_size, player_stack)
                else:
                    return equity, 'check', 0
            
            # Main moyenne → plus de value bets, moins de checks
            elif equity < 0.60:
                # Bet fréquent pour protéger et extraire de la value
                bet_frequency = 0.65 + aggression_factor
                
                if random.random() < bet_frequency:
                    # Sizing adapté au SPR
                    if spr < 3:  # Stack court → gros bets
                        bet_size = int(pot * random.uniform(0.70, 0.95))
                    else:  # Stack profond → bets contrôlés
                        bet_size = int(pot * random.uniform(0.55, 0.75))
                    return equity, 'bet', min(bet_size, player_stack)
                else:
                    return equity, 'check', 0
            
            # Main forte → value bet presque toujours
            else:
                check_frequency = 0.05 if self.stage >= 2 else 0.02  # Très rare
                
                if random.random() < check_frequency:
                    return equity, 'check', 0
                
                # Sizing pour maximiser la value
                if spr < 2:  # All-in territory
                    bet_size = player_stack
                elif equity > 0.80:  # Main très forte → gros sizing mais raisonnable
                    bet_size = int(pot * random.uniform(0.60, 0.85))  # RÉDUIT de 0.80-1.20
                else:  # Main forte standard
                    bet_size = int(pot * random.uniform(0.50, 0.75))  # RÉDUIT de 0.65-0.90
                
                return equity, 'bet', min(bet_size, player_stack)
        
        # --- CAS 2 : FACE À UN BET (Réaction) ---
        else:
            # All-in forcé → décision EV pure avec légère tolérance
            if to_call >= player_stack:
                ev_call = self.EV_call(equity=equity)
                # Tolérance selon l'equity et le pot
                tolerance = 10 if equity > 0.35 else 5
                return equity, 'call' if ev_call >= -tolerance else 'fold', player_stack
            
            ev_call = self.EV_call(equity=equity)
            ev_fold = 0
            
            # --- FOLD évident si très mauvaise equity ---
            if equity < 0.20 and ev_call < -to_call * 0.5:
                return equity, 'fold', 0
            
            # --- BLUFF CATCHER : equity moyenne mais EV négatif ---
            if 0.35 < equity < 0.52 and ev_call < 0:
                # Call plus fréquent si bon pot odds ou position
                bluff_catch_freq = 0.30 + (pot_odds - equity) * 0.5 + aggression_factor
                bluff_catch_freq = max(0.15, min(0.65, bluff_catch_freq))
                
                if random.random() < bluff_catch_freq:
                    return equity, 'call', to_call
                else:
                    return equity, 'fold', 0
            
            # --- CALL RENTABLE → Évaluation des options (call/raise) ---
            if ev_call > 0:
                best_ev = ev_call
                best_action = 'call'
                best_amount = to_call
                
                # Fréquence de raise selon l'equity et la position
                if equity > 0.55:  # Bonne main
                    raise_frequency = 0.45 + aggression_factor
                elif equity > 0.45:  # Main correcte
                    raise_frequency = 0.25 + aggression_factor
                else:  # Main marginale
                    raise_frequency = 0.10 + aggression_factor
                
                # Test de plusieurs tailles de raise si on décide d'être agressif
                if random.random() < raise_frequency:
                    # Tailles de raise adaptées au contexte - CORRIGÉ pour mises plus raisonnables
                    if spr < 3:  # Stack court → raise all-in ou gros
                        raise_factors = [0.5, 0.75, 1.0]  # Pourcentage du POT, pas du pot + to_call
                    else:  # Stack profond → raise standards
                        raise_factors = [0.35, 0.5, 0.65]  # Sizing plus standards
                    
                    for factor in raise_factors:
                        # CORRECTION : raise basé sur le POT, pas sur pot + to_call
                        raise_size = int(to_call * 2.5 + pot * factor)  # Minimum 2.5x le call + % du pot
                        raise_size = min(raise_size, player_stack)
                        
                        if raise_size <= to_call * 2:
                            continue
                        
                        ev_raise = self.EV_bet(raise_size - to_call, equity=equity)
                        
                        # Bonus EV pour l'agressivité (pressure sur l'adversaire)
                        pressure_bonus = (equity - 0.50) * raise_size * 0.05
                        ev_raise += pressure_bonus
                        
                        if ev_raise > best_ev:
                            best_ev = ev_raise
                            best_action = 'bet'
                            best_amount = raise_size
                
                return equity, best_action, best_amount
            
            # --- CALL NON RENTABLE mais equity acceptable (semi-bluff defense) ---
            if 0.30 < equity < 0.45 and to_call < pot * 0.4:
                # Call occasionnel pour ne pas être exploitable
                defense_freq = 0.20 + aggression_factor * 0.5
                if random.random() < defense_freq:
                    return equity, 'call', to_call
            
            # --- FOLD par défaut ---
            return equity, 'fold', 0
