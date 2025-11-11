import random
import json
from Deal import Deal
from utils import hand_rank
from collections import Counter
from datetime import datetime

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
        self.board = board if board is not None else []
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
        self.opp_hand = [card for card in deal.cards_init() if card not in known_cards]  # Toutes les cartes possibles pour l'adversaire (paquet - board - main)
        
        # Initialisation du range adverse (dictionnaire avec poids)
        self.opponent_range = self.init_full_range()

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

    # ==================== GESTION DES RANGES ====================
    
    def init_full_range(self):
        """
        Initialise une range complète avec toutes les mains possibles à partir de self.opp_hand.
        Retourne: dict avec structure {combo: poids}
        """
        full_range = {}
        
        # Utiliser self.opp_hand qui contient déjà les cartes disponibles
        for i, card1 in enumerate(self.opp_hand):
            for card2 in self.opp_hand[i+1:]:
                combo = tuple(sorted([card1, card2]))
                full_range[combo] = 1.0  # Poids initial de 1.0 pour chaque combo
        
        # Normaliser pour que la somme = 1.0
        total = len(full_range)
        if total > 0:
            full_range = {combo: 1.0/total for combo in full_range}
        
        return full_range
    
    def get_hand_category(self, hand):
        """
        Catégorise une main en fonction de sa force.
        Returns: str ('premium', 'strong', 'medium', 'weak', 'trash')
        """
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                      '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        card1, card2 = hand[0], hand[1]
        rank1, rank2 = card1[1], card2[1]
        suit1, suit2 = card1[0], card2[0]
        
        val1, val2 = rank_values[rank1], rank_values[rank2]
        is_pair = (rank1 == rank2)
        is_suited = (suit1 == suit2)
        
        # Paires premium
        if is_pair and val1 >= 10:  # TT+
            return 'premium'
        
        # Broadways premium
        if val1 >= 12 and val2 >= 12:  # AK, AQ, KQ
            return 'premium' if is_suited else 'strong'
        
        # Paires moyennes
        if is_pair and val1 >= 7:  # 77-99
            return 'strong'
        
        # Broadways moyennes
        if val1 >= 11 and val2 >= 10:  # AJ, KJ, QJ, AT, KT
            return 'strong' if is_suited else 'medium'
        
        # Suited connectors forts
        if is_suited and abs(val1 - val2) <= 1 and val1 >= 9:
            return 'medium'
        
        # Petites paires
        if is_pair:
            return 'medium'
        
        # Suited broadways faibles
        if is_suited and (val1 >= 11 or val2 >= 11):
            return 'medium'
        
        # Suited connectors moyens
        if is_suited and abs(val1 - val2) <= 2:
            return 'weak'
        
        return 'trash'
    
    def analyze_board_texture(self, board):
        """
        Analyse la texture du board pour déterminer les draws possibles.
        Returns: dict avec les caractéristiques du board
        """
        if len(board) < 3:
            return {'type': 'preflop', 'draw_heavy': False, 'paired': False, 'coordinated': False}
        
        ranks = [card[1] for card in board]
        suits = [card[0] for card in board]
        
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                      '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        # Vérifier si le board est pairé
        rank_counts = Counter(ranks)
        is_paired = any(count >= 2 for count in rank_counts.values())
        
        # Vérifier les flush draws (3+ cartes de la même couleur)
        suit_counts = Counter(suits)
        flush_draw_possible = any(count >= 3 for count in suit_counts.values())
        
        # Vérifier les straight draws (cartes connectées)
        values = sorted([rank_values[r] for r in ranks])
        straight_draw_possible = False
        
        for i in range(len(values) - 1):
            # Si 2 cartes consécutives ou écart de 2
            if values[i+1] - values[i] <= 2:
                straight_draw_possible = True
                break
        
        # Board coordonné = possibilité de straights ET/OU flushes
        is_coordinated = flush_draw_possible or straight_draw_possible
        
        # Board "draw heavy" = beaucoup de possibilités de draws
        draw_heavy = flush_draw_possible and straight_draw_possible
        
        # Board rainbow = 3+ couleurs différentes (peu de flush draw)
        is_rainbow = len(suit_counts) >= 3
        
        # Board sec = pas pairé, pas de draws
        is_dry = not is_paired and not is_coordinated
        
        return {
            'type': 'postflop',
            'paired': is_paired,
            'flush_draw': flush_draw_possible,
            'straight_draw': straight_draw_possible,
            'coordinated': is_coordinated,
            'draw_heavy': draw_heavy,
            'rainbow': is_rainbow,
            'dry': is_dry
        }
    
    def apply_action(self, action, sizing_ratio, board):
        """
        Réduit la range de l'adversaire en fonction de son action et du sizing.
        Met à jour self.opponent_range ET self.opp_hand en conséquence.
        
        Args:
            action: str ('bet', 'raise', 'call', 'check', 'fold')
            sizing_ratio: float - ratio par rapport au pot (ex: 0.5 = 50% pot, 1.0 = pot, 2.0 = 2x pot)
            board: list - cartes du board
        """
        if not self.opponent_range:
            return
        
        # Analyser la texture du board
        texture = self.analyze_board_texture(board)
        
        # Coefficients de réduction selon l'action et le sizing
        new_range = {}
        
        for combo, weight in self.opponent_range.items():
            hand_strength = self.get_hand_category(combo)
            new_weight = weight
            
            # ============ LOGIQUE DE RÉDUCTION SELON L'ACTION ============
            
            if action == 'fold':
                # L'adversaire fold = on ne garde que les mains très faibles
                if hand_strength in ['premium', 'strong', 'medium']:
                    new_weight *= 0.05  # Presque impossible qu'il fold ces mains
                else:
                    new_weight *= 0.95  # Très probable avec des mains faibles
            
            elif action == 'check':
                # Check = généralement pas de main premium
                if hand_strength == 'premium':
                    new_weight *= 0.2  # Moins probable de check avec premium
                elif hand_strength == 'strong':
                    new_weight *= 0.6  # Possible de slowplay
                else:
                    new_weight *= 1.2  # Plus probable avec mains moyennes/faibles
            
            elif action == 'call':
                # Call = range plus défensive, dépend du sizing
                if sizing_ratio < 0.4:  # Petit sizing
                    # Il peut call avec une range large
                    if hand_strength in ['premium', 'strong']:
                        new_weight *= 1.3
                    elif hand_strength == 'medium':
                        new_weight *= 1.5
                    else:
                        new_weight *= 0.8
                
                elif sizing_ratio < 0.75:  # Sizing moyen
                    if hand_strength in ['premium', 'strong']:
                        new_weight *= 1.4
                    elif hand_strength == 'medium':
                        new_weight *= 1.2
                    else:
                        new_weight *= 0.4
                
                else:  # Gros sizing (>75% pot)
                    # Range de call plus serrée
                    if hand_strength == 'premium':
                        new_weight *= 1.6
                    elif hand_strength == 'strong':
                        new_weight *= 1.3
                    elif hand_strength == 'medium':
                        new_weight *= 0.7
                    else:
                        new_weight *= 0.2
            
            elif action in ['bet', 'raise']:
                # Bet/Raise = range polarisée (value + bluffs)
                
                if sizing_ratio < 0.4:  # Petit bet (< 40% pot)
                    # Range plus large, peut bet/bluff avec beaucoup de mains
                    if hand_strength in ['premium', 'strong']:
                        new_weight *= 1.3  # Value betting
                    elif hand_strength == 'medium':
                        new_weight *= 1.4  # Beaucoup de bluffs/semi-bluffs
                    else:
                        new_weight *= 1.1  # Peut aussi bluff avec trash
                
                elif sizing_ratio < 0.75:  # Sizing moyen (40-75% pot)
                    # Range équilibrée value/bluff
                    if hand_strength == 'premium':
                        new_weight *= 1.6  # Forte value
                    elif hand_strength == 'strong':
                        new_weight *= 1.4
                    elif hand_strength == 'medium':
                        new_weight *= 1.2  # Semi-bluffs sur boards draw heavy
                        if texture['draw_heavy']:
                            new_weight *= 1.3
                    else:
                        new_weight *= 0.6
                
                elif sizing_ratio < 1.25:  # Gros bet (75-125% pot)
                    # Range très polarisée
                    if hand_strength == 'premium':
                        new_weight *= 2.0  # Nuts et quasi-nuts
                    elif hand_strength == 'strong':
                        new_weight *= 1.5
                    elif hand_strength == 'medium':
                        new_weight *= 0.5
                    else:
                        new_weight *= 0.8  # Quelques bluffs
                
                else:  # Overbet (>125% pot)
                    # Range hyper polarisée : nuts ou air
                    if hand_strength == 'premium':
                        new_weight *= 2.5  # Très forte value
                    elif hand_strength == 'strong':
                        new_weight *= 0.8
                    elif hand_strength == 'medium':
                        new_weight *= 0.3
                    else:
                        new_weight *= 1.2  # Pure bluffs
            
            # ============ AJUSTEMENTS SELON LA TEXTURE DU BOARD ============
            
            # Sur board pairé, moins de bluffs possibles
            if texture.get('paired') and action in ['bet', 'raise']:
                if hand_strength in ['weak', 'trash']:
                    new_weight *= 0.6
            
            # Sur board draw heavy, plus de semi-bluffs
            if texture.get('draw_heavy') and action in ['bet', 'raise']:
                if hand_strength == 'medium':
                    new_weight *= 1.3
            
            # Sur board sec, moins de protection nécessaire
            if texture.get('dry') and action == 'check':
                if hand_strength in ['premium', 'strong']:
                    new_weight *= 1.2  # Plus de slowplay possible
            
            # Limiter les poids entre 0 et un maximum raisonnable
            new_weight = max(0.01, min(new_weight, 3.0))
            
            new_range[combo] = new_weight
        
        # Normaliser les poids pour qu'ils somment à 1.0
        total_weight = sum(new_range.values())
        if total_weight > 0:
            self.opponent_range = {combo: w/total_weight for combo, w in new_range.items()}
        else:
            # Si tous les poids sont à 0, garder la range originale
            self.opponent_range = {combo: 1.0/len(new_range) for combo in new_range}
        
        # Mettre à jour self.opp_hand pour ne garder que les cartes des combos avec poids significatif
        # On garde les combos avec un poids > seuil (ex: 0.1% de la distribution)
        threshold = 0.001
        filtered_combos = {combo: w for combo, w in self.opponent_range.items() if w >= threshold}
        
        # Extraire toutes les cartes uniques des combos restants
        new_opp_hand_set = set()
        for combo in filtered_combos.keys():
            new_opp_hand_set.add(combo[0])
            new_opp_hand_set.add(combo[1])
        
        # Mettre à jour self.opp_hand (en gardant l'ordre si possible)
        self.opp_hand = [card for card in self.opp_hand if card in new_opp_hand_set]

    def log_decision(self, hand_id, decision_type="unknown", filename="poker_decisions.json"):
        """
        Sauvegarde les données statistiques calculées dans un fichier JSON.
        
        Args:
            hand_id: str - Identifiant unique de la main (ex: "game_5_hand_23")
            decision_type: str - Type de décision (ex: "preflop_call", "flop_raise", etc.)
            filename: str - Nom du fichier JSON où sauvegarder
        """
        # Calculer les métriques importantes
        equity = self.get_equity(num_simulations=5000)  # Moins de simulations pour le log
        pot_odds = self.pot_odds()
        mdf = self.MDF()
        fold_equity = self.estimate_fold_equity()
        ev_call = self.EV_call(equity=equity)
        ev_fold = self.EV_fold()
        
        # Calculer les outs si on n'est pas à la river
        if len(self.board) < 5:
            nb_outs, _, prob_outs = self.outs()
        else:
            nb_outs, prob_outs = 0, 0.0
        
        # Analyser la texture du board
        board_texture = self.analyze_board_texture(self.board)
        
        # Créer l'entrée de log
        log_entry = {
            "hand_id": hand_id,
            "timestamp": datetime.now().isoformat(),
            "decision_type": decision_type,
            "context": {
                "hand": [f"{card[0]}{card[1]}" for card in self.hand],
                "board": [f"{card[0]}{card[1]}" for card in self.board],
                "pot": self.pot,
                "amount_to_call": self.amount_to_call,
                "stage": self.stage,
                "position": self.position_main_character
            },
            "board_analysis": board_texture,
            "metrics": {
                "equity": round(equity, 4),
                "pot_odds": round(pot_odds, 4),
                "mdf": round(mdf, 4),
                "fold_equity": round(fold_equity, 4),
                "ev_call": round(ev_call, 2),
                "ev_fold": ev_fold,
                "outs": nb_outs,
                "outs_probability": prob_outs
            },
            "opponent_range_size": len(self.opponent_range),
            "opponent_possible_cards": len(self.opp_hand)
        }
        
        # Charger les données existantes ou créer un nouveau fichier
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    data = [data]  # Si c'est un dict, on le met dans une liste
        except (FileNotFoundError, json.JSONDecodeError):
            data = []
        
        # Ajouter la nouvelle entrée
        data.append(log_entry)
        
        # Sauvegarder dans le fichier
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return log_entry

    def win_chance_and_choice(self, num_simulations=100000):
        """
        Calcule l'équité et détermine l'action optimale (fold/call/check/bet/raise) avec le sizing optimal.
        arg: num_simulations --> Nombre de simulations Monte Carlo (par défaut 100000 pour précision).
        return: (equity, action, sizing)
        """
        # Calcul de l'équité UNE SEULE FOIS avec un nombre élevé de simulations
        equity = self.Monte_Carlo(num_simulations)
        
        # Calculs avec les fonctions précédentes (en passant l'équité pour éviter recalcul)
        pot_odds = self.pot_odds()
        mdf = self.MDF()
        
        # ============ CAS 1: ON EST PREMIER À PARLER (amount_to_call == 0) ============
        if self.amount_to_call == 0:
            # On peut check ou bet
            # Check est gratuit, bet coûte de l'argent mais peut faire folder l'adversaire ou build le pot
            
            # Si équité très faible (< 35%), on check
            if equity < 0.35:
                return equity, 'check', 0
            
            # Si équité moyenne (35-50%), on bet petit pour protection ou semi-bluff
            elif equity < 0.50:
                bet_sizing = self.pot * 0.33
                if self.main_character and hasattr(self.main_character, 'stack'):
                    bet_sizing = min(bet_sizing, self.main_character.stack)
                return equity, 'bet', round(bet_sizing)
            
            # Si équité bonne (50-65%), on bet moyen pour value
            elif equity < 0.65:
                bet_sizing = self.pot * 0.66
                if self.main_character and hasattr(self.main_character, 'stack'):
                    bet_sizing = min(bet_sizing, self.main_character.stack)
                return equity, 'bet', round(bet_sizing)
            
            # Si équité forte (65-80%), on bet pot pour value
            elif equity < 0.80:
                bet_sizing = self.pot * 1.0
                if self.main_character and hasattr(self.main_character, 'stack'):
                    bet_sizing = min(bet_sizing, self.main_character.stack)
                return equity, 'bet', round(bet_sizing)
            
            # Si équité très forte (>80%), on bet gros pour maximiser value
            else:
                bet_sizing = self.pot * 1.5
                if self.main_character and hasattr(self.main_character, 'stack'):
                    bet_sizing = min(bet_sizing, self.main_character.stack)
                return equity, 'bet', round(bet_sizing)
        
        # ============ CAS 2: ON DOIT CALL UN BET (amount_to_call > 0) ============
        else:
            # Calculer les EV pour chaque action
            ev_fold = self.EV_fold()  # Toujours 0
            ev_call = self.EV_call(equity=equity)  # Passe l'équité précalculée
            
            # Si équité < pot odds, fold est optimal (call serait -EV)
            if equity < pot_odds:
                return equity, 'fold', 0
            
            # Si équité juste au-dessus des pot odds mais pas assez forte pour raise
            # Call si : pot_odds <= equity < (pot_odds + 0.20)
            if pot_odds <= equity < (pot_odds + 0.20):
                return equity, 'call', self.amount_to_call
            
            # Si équité forte, on teste si un raise serait meilleur
            # Tester différents sizings de raise (% du pot)
            raise_sizings = [0.5, 0.75, 1.0, 1.5, 2.0]  # Ratios du pot
            best_ev = ev_call
            best_sizing = self.amount_to_call
            best_action = 'call'
            
            for sizing_ratio in raise_sizings:
                raise_amount = self.amount_to_call + (self.pot * sizing_ratio)
                
                # Limiter au stack disponible si main_character existe
                if self.main_character and hasattr(self.main_character, 'stack'):
                    raise_amount = min(raise_amount, self.main_character.stack)
                
                # Calculer l'EV de ce raise (en passant l'équité précalculée)
                ev_raise = self.EV_bet(raise_amount, equity=equity)
                
                # Si cet EV est meilleur, on le garde
                if ev_raise > best_ev:
                    best_ev = ev_raise
                    best_sizing = raise_amount
                    best_action = 'raise'
            
            # Stratégie basée sur l'équité pour déterminer le sizing optimal
            equity_over_pot_odds = equity - pot_odds
            
            if equity_over_pot_odds > 0.45:
                # Équité très forte (>45% au-dessus des pot odds) : raise gros
                optimal_raise = self.amount_to_call + (self.pot * 2.0)
            elif equity_over_pot_odds > 0.35:
                # Équité forte (35-45% au-dessus) : raise 1.5x pot
                optimal_raise = self.amount_to_call + (self.pot * 1.5)
            elif equity_over_pot_odds > 0.25:
                # Équité bonne (25-35% au-dessus) : raise pot
                optimal_raise = self.amount_to_call + (self.pot * 1.0)
            else:
                # Équité correcte mais pas assez pour raise agressif : call
                return equity, 'call', self.amount_to_call
            
            # Limiter au stack disponible si main_character existe
            if self.main_character and hasattr(self.main_character, 'stack'):
                optimal_raise = min(optimal_raise, self.main_character.stack)
            
            optimal_raise = round(optimal_raise)
            
            # Calculer l'EV de ce raise optimal
            ev_optimal = self.EV_bet(optimal_raise, equity=equity)
            
            # Retourner la meilleure action entre call, raise testé, et raise optimal
            if ev_optimal > best_ev and ev_optimal > ev_call:
                return equity, 'raise', optimal_raise
            elif best_action == 'raise' and best_ev > ev_call:
                return equity, 'raise', best_sizing
            else:
                return equity, 'call', self.amount_to_call