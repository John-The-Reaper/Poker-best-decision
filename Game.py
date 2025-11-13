from players_class.calling_station import Calling_station
from players_class.tag import Tag
from players_class.lag import Lag
from players_class.maniac import Maniac
from players_class.nit import Nit
from players_class.best_choice import best_choice
from stats import Stat
from deal import Deal
from utils import hand_rank
import json

class Game:
    def __init__(self, big_blind=50, small_blind=25, stack=1000, num_simulations=2000):
        self.big_blind = big_blind
        self.small_blind = small_blind  
        self.initial_stack = stack
        self.num_simulations = num_simulations
        self.game_count = 0
        self.game_history = []

        self.values = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]

        self.calling_station = Calling_station(stack=stack)
        self.tag = Tag(stack=stack)
        self.lag = Lag(stack=stack)
        self.maniac = Maniac(stack=stack)
        self.nit = Nit(stack=stack)
        self.best_choice = best_choice(stack=stack)

        self.calling_station.position = 0
        self.tag.position = 1
        self.lag.position = 2
        self.maniac.position = 3
        self.nit.position = 4
        self.best_choice.position = 5

        self.players = [self.calling_station, self.tag, self.lag, self.maniac, self.nit, self.best_choice]
        self.player_names = ['calling_station', 'tag', 'lag', 'maniac', 'nit', 'best_choice']

    def game(self):
        """
        Exécute une main complète de poker pour l'instance de jeu.
        Fonctionnalités :
        - Initialise la donne et distribue les mains aux joueurs actifs.
        - Gère la publication des small/big blinds et met à jour les stacks et le pot.
        - Lance les tours d'enchères successifs : préflop, flop, turn, river.
        - Met à jour le board et les mises courantes à chaque tour.
        - Termine la main soit par abandon (un seul joueur restant) soit par abattage (showdown).
        Effets de bord :
        - Modifie les attributs des joueurs (hand, stack), le pot et le board.
        Returns:
        - Le résultat renvoyé par _award_pot ou _showdown, ou None si moins de deux joueurs actifs.
        """
        dealer = Deal()
        dealer.cards_init()
        
        active_players = [p for p in self.players if p.stack > 0]
        if len(active_players) < 2:
            return None

        for player in active_players:
            player.hand = dealer.deal_player_hand()
        
        pot = 0
        board = []
        current_bets = {id(p): 0 for p in active_players}
         
        sb_player = next((p for p in active_players if p.position == 1), active_players[0])
        bb_player = next((p for p in active_players if p.position == 2), (active_players[1] if len(active_players) > 1 else active_players[0]))
        
        sb_amount = int(min(self.small_blind, sb_player.stack))
        sb_player.stack = int(sb_player.stack - sb_amount)
        current_bets[id(sb_player)] = sb_amount
        pot = int(pot + sb_amount)
        
        bb_amount = int(min(self.big_blind, bb_player.stack))
        bb_player.stack = int(bb_player.stack - bb_amount)
        current_bets[id(bb_player)] = bb_amount
        pot = int(pot + bb_amount)
        
        # PREFLOP
        pot, active_players, current_bets = self._betting_round(active_players, pot, current_bets, board, 0)
        if len(active_players) == 1:
            return self._award_pot(active_players[0], pot, board)
        
        # FLOP
        board = dealer.deal_board()
        current_bets = {id(p): 0 for p in active_players}
        pot, active_players, current_bets = self._betting_round(active_players, pot, current_bets, board, 1)
        if len(active_players) == 1:
            return self._award_pot(active_players[0], pot, board)
        
        # TURN
        board = dealer.deal_board()
        current_bets = {id(p): 0 for p in active_players}
        pot, active_players, current_bets = self._betting_round(active_players, pot, current_bets, board, 2)
        if len(active_players) == 1:
            return self._award_pot(active_players[0], pot, board)
        
        # RIVER
        board = dealer.deal_board()
        current_bets = {id(p): 0 for p in active_players}
        pot, active_players, current_bets = self._betting_round(active_players, pot, current_bets, board, 3)
        if len(active_players) == 1:
            return self._award_pot(active_players[0], pot, board)
        
        return self._showdown(active_players, pot, board)

    def _betting_round(self, active_players, pot, current_bets, board, state):
        """
        Gère un tour de mise complet
        """
        max_rounds = 10
        round_count = 0
        
        while round_count < max_rounds:
            round_count += 1
            someone_acted = False
            current_bet = max(current_bets.values()) if current_bets else 0

            for player in active_players[:]:
                if player.stack == 0:
                    continue
                
                # Montant que le joueur doit ajouter pour égaliser
                amount_to_call = current_bet - current_bets[id(player)]
                
                # Obtenir les statistiques
                equity, optimal_bet, optimal_choice = self.get_stats(
                    player_hand=player.hand,
                    board=board,
                    pot=pot,
                    amount_to_call=amount_to_call
                )
                
                # Obtenir l'action du joueur
                action = self._get_player_action(player, amount_to_call, optimal_choice, optimal_bet, equity)
                print(action)

                # Traiter l'action
                if 'fold' in action:
                    active_players.remove(player)
                    someone_acted = True
                    if len(active_players) == 1:
                        return pot, active_players, current_bets

                elif 'check' in action:
                    if amount_to_call == 0:
                        someone_acted = True
                    else:
                        # Check impossible quand il faut call
                        active_players.remove(player)

                elif 'call' in action:
                    call_amount = int(min(action.get('call', amount_to_call), player.stack))
                    
                    # Retirer du stack ET ajouter au pot
                    player.stack = int(player.stack - call_amount)
                    pot = int(pot + call_amount)
                    current_bets[id(player)] = int(current_bets[id(player)] + call_amount)
                    someone_acted = True

                elif 'bet' in action:
                    # BET = premier à miser ce tour (amount_to_call devrait être 0)
                    bet_amount = int(action.get('bet', 0))
                    bet_amount = int(min(bet_amount, player.stack))
                    
                    # Retirer du stack ET ajouter au pot
                    player.stack = int(player.stack - bet_amount)
                    pot = int(pot + bet_amount)
                    current_bets[id(player)] = int(current_bets[id(player)] + bet_amount)
                    someone_acted = True
                
                elif 'raise' in action:
                    # RAISE = égaliser + montant additionnel
                    raise_amount = int(action.get('raise', 0))
                    total_to_add = int(amount_to_call + raise_amount)
                    total_to_add = int(min(total_to_add, player.stack))
                    
                    # Retirer du stack ET ajouter au pot
                    player.stack = int(player.stack - total_to_add)
                    pot = int(pot + total_to_add)
                    current_bets[id(player)] = int(current_bets[id(player)] + total_to_add)
                    someone_acted = True
            
            # Vérifier si tout le monde a misé la même chose
            bets_list = [current_bets[id(p)] for p in active_players if p.stack > 0]
            
            if bets_list and len(set(bets_list)) <= 1 and someone_acted:
                break
        
        return pot, active_players, current_bets

    def _get_position_name(self, position):
        position_names = {
            0: "button",
            1: "small_blind",
            2: "big_blind",
            3: "utg",
            4: "cutt_off",
            5: "hijack"
        }
        return position_names.get(position, position)

    def _get_player_action(self, player, amount_to_call, optimal_choice, optimal_bet, equity):
        """
        Récupère l'action d'un joueur
        """
        try:
            position_name = self._get_position_name(player.position)
            result = player.action(amount_to_call, position_name, optimal_choice, optimal_bet, equity)
            
            if isinstance(result, str):
                return {result: True}
            return result
        except Exception as e:
            return {'fold': True}

    def _award_pot(self, winner, pot, board):
        winner.stack += pot
        winner_name = self.player_names[self.players.index(winner)]
        
        game_data = {
            'game_number': self.game_count,
            'winner': winner_name,
            'pot': pot,
            'board': board,
            'final_stacks': {name: p.stack for name, p in zip(self.player_names, self.players)}
        }
        
        self.game_history.append(game_data)
        return game_data

    def _showdown(self, active_players, pot, board):
        if board is None:
            board = []
        
        best_rank = 0
        winners = []
        
        for player in active_players:
            rank, _ = hand_rank(player.hand, board)
            if rank > best_rank:
                best_rank = rank
                winners = [player]
            elif rank == best_rank:
                winners.append(player)
        
        share = pot // len(winners)
        remainder = pot % len(winners)
        
        for i, winner in enumerate(winners):
            winner.stack += share + (remainder if i == 0 else 0)
        
        winner_names = [self.player_names[self.players.index(w)] for w in winners]
        
        game_data = {
            'game_number': self.game_count,
            'winner': winner_names[0] if len(winners) == 1 else winner_names,
            'pot': pot,
            'board': board,
            'final_stacks': {name: p.stack for name, p in zip(self.player_names, self.players)}
        }
        
        self.game_history.append(game_data)
        return game_data
    
    def simulation(self, save_path: str = None):
        """
        Génère une simulation jusqu'à ce qu'un seul joueur ait tous les jetons
        
        Args:
            save_path: Chemin pour sauvegarder les stats (optionnel)
        
        Note: La simulation continue jusqu'à ce qu'un seul joueur reste.
        """
        total_start = sum(p.stack for p in self.players)
        
        game_num = 0
        while True:
            self.game_count = game_num + 1
            
            active_count = sum(1 for p in self.players if p.stack > 0)
            
            if active_count <= 1:
                winner = next((p for p in self.players if p.stack > 0), None)
                if winner:
                    winner_name = self.player_names[self.players.index(winner)]
                break
            
            # Augmenter les blinds tous les 10 parties
            if game_num > 0 and game_num % 10 == 0:
                self.big_blind = int(self.big_blind * 1.5)
                self.small_blind = int(self.small_blind * 1.5)
            
            # Jouer une partie
            game_data = self.game()
            if game_data is None:
                break
            
            # Rotation des positions
            for player in self.players:
                player.position = (player.position + 1) % 5
            
            game_num += 1
        
        # Calculer les statistiques
        stats = self._calculate_stats()
        
        # Sauvegarder
        if save_path:
            self.save_json(stats, save_path)
        
        return stats

    def _calculate_stats(self):
        """
        Calcule les statistiques de la simulation
        """
        stats = {
            'total_games': len(self.game_history),
            'player_stats': {},
            'game_history': self.game_history
        }
        
        for name, player in zip(self.player_names, self.players):
            wins = sum(1 for g in self.game_history 
                      if g.get('winner') == name or 
                      (isinstance(g.get('winner'), list) and name in g.get('winner')))
            
            stats['player_stats'][name] = {
                'final_stack': player.stack,
                'profit': player.stack - self.initial_stack,
                'wins': wins
            }
        
        return stats

    def save_json(self, data: dict, path: str):
        """
        Sauvegarde dans un fichier JSON
        """
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_stats(self, player_hand, board, pot, amount_to_call):
        """
        Crée un objet Stat pour un joueur
        
        Args:
            player_hand: Main du joueur
            board: Board actuel (peut être None ou vide)
            pot: Taille du pot
            amount_to_call: Montant à payer
            
        Returns:
            Stat: Objet Stat initialisé
        """
        if board is None:
            board = []

        stat = Stat(hand=player_hand, board=board, pot=pot, amount_to_call=amount_to_call)
        return stat.win_chance_and_choice(num_simulations=self.num_simulations)
