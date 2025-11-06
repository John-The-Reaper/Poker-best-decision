from players.calling_station import Calling_station
from players.tag import Tag
from players.lag import Lag
from players.maniac import Maniac 
from players.nit import Nit

from Stats import Statistics
from deal import Deal
from collections import Counter
import json 

class Game:
    def __init__(self, big_blind=50, small_blind=25, stack=1000):
        """
        Initialisation de toutes les classes joueurs
        """
        self.big_blind = big_blind
        self.small_blind = small_blind  
        self.initial_stack = stack
        self.game_count = 0
        self.game_history = []
        
        # Valeurs pour hand_rank
        self.values = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        
        # Initialisation des joueurs
        self.calling_station = Calling_station(position=0, stack=stack)
        self.tag = Tag(position=1, stack=stack)
        self.lag = Lag(position=2, stack=stack)
        self.maniac = Maniac(position=3, stack=stack)
        self.nit = Nit(position=4, stack=stack)
        
        self.players = [self.calling_station, self.tag, self.lag, self.maniac, self.nit]
        self.player_names = ['calling_station', 'tag', 'lag', 'maniac', 'nit']

    def game(self):
        """
        Génère le déroulement complet de la partie et renvoie les données de la partie
        """
        dealer = Deal()
        dealer.cards_init()
        
        # Joueurs actifs avec des jetons
        active_players = [p for p in self.players if p.stack > 0]
        if len(active_players) < 2:
            return None
        
        # Distribution des mains - deal_player_hand() retourne [carte1, carte2]
        for player in active_players:
            player.hand = dealer.deal_player_hand()
        
        pot = 0
        board = []
        
        # Tracker les mises de chaque joueur dans le tour actuel
        current_bets = {id(p): 0 for p in active_players}
        
        # Blinds
        sb_player = active_players[0]
        bb_player = active_players[1] 
        
        sb_amount = min(self.small_blind, sb_player.stack)
        sb_player.stack -= sb_amount
        current_bets[id(sb_player)] = sb_amount
        pot += sb_amount
        
        bb_amount = min(self.big_blind, bb_player.stack)
        bb_player.stack -= bb_amount
        current_bets[id(bb_player)] = bb_amount
        pot += bb_amount
        
        # PREFLOP
        pot, active_players, current_bets = self._betting_round(
            active_players, pot, current_bets, board, 0
        )
        if len(active_players) == 1:
            return self._award_pot(active_players[0], pot, board)
        
        # FLOP
        board = dealer.deal_board()
        current_bets = {id(p): 0 for p in active_players}
        pot, active_players, current_bets = self._betting_round(
            active_players, pot, current_bets, board, 1
        )
        if len(active_players) == 1:
            return self._award_pot(active_players[0], pot, board)
        
        # TURN
        board = dealer.deal_board()
        current_bets = {id(p): 0 for p in active_players}
        pot, active_players, current_bets = self._betting_round(
            active_players, pot, current_bets, board, 2
        )
        if len(active_players) == 1:
            return self._award_pot(active_players[0], pot, board)
        
        # RIVER
        board = dealer.deal_board()
        current_bets = {id(p): 0 for p in active_players}
        pot, active_players, current_bets = self._betting_round(
            active_players, pot, current_bets, board, 3
        )
        if len(active_players) == 1:
            return self._award_pot(active_players[0], pot, board)
        
        # SHOWDOWN
        return self._showdown(active_players, pot, board)

    def _betting_round(self, active_players, pot, current_bets, board, state):
        """
        Gère un tour de mises
        """
        max_rounds = 10
        round_count = 0
        
        while round_count < max_rounds:
            round_count += 1
            someone_acted = False
            
            # Mise actuelle à égaler
            current_bet = max(current_bets.values()) if current_bets else 0
            
            for player in active_players[:]:
                if player.stack == 0:
                    continue
                
                # Montant que le joueur doit payer pour égaler
                amount_to_call = current_bet - current_bets[id(player)]
                
                # Obtenir l'action du joueur (sans calculer win_rate nous-mêmes)
                action = self._get_player_action(player, amount_to_call, board, state)
                
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
                        # Check impossible avec mise à suivre -> fold
                        active_players.remove(player)
                
                elif 'call' in action:
                    call_amount = min(amount_to_call, player.stack)
                    player.stack -= call_amount
                    current_bets[id(player)] += call_amount
                    pot += call_amount
                    someone_acted = True
                
                elif 'bet' in action or 'raise' in action:
                    bet_amount = action.get('bet', action.get('raise', 0))
                    # Le joueur doit d'abord égaler puis raiser
                    total_to_add = amount_to_call + bet_amount
                    actual_bet = min(total_to_add, player.stack)
                    
                    player.stack -= actual_bet
                    current_bets[id(player)] += actual_bet
                    pot += actual_bet
                    someone_acted = True
            
            # Vérifier si tout le monde a misé pareil
            bets_list = [current_bets[id(p)] for p in active_players if p.stack > 0]
            all_in_bets = [current_bets[id(p)] for p in active_players if p.stack == 0]
            
            if bets_list and len(set(bets_list)) <= 1 and someone_acted:
                break
        
        return pot, active_players, current_bets

    def _get_player_action(self, player, amount_to_call, board, state):
        """
        Obtient l'action d'un joueur
        """
        try:
            # Calling_station a une signature différente
            if isinstance(player, Calling_station):
                result = player.action(amount_to_call)
                if isinstance(result, str):
                    return {result: True}
                return result
            else:
                # Les autres joueurs
                return player.action(amount_to_call, board, state)
        except Exception as e:
            print(f"Erreur action joueur: {e}")
            return {'fold': True}

    def _award_pot(self, winner, pot, board):
        """
        Attribue le pot au gagnant
        """
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
        """
        Détermine le gagnant au showdown
        """
        best_rank = 0
        winners = []
        
        for player in active_players:
            rank, _ = self.hand_rank(player.hand, board)
            if rank > best_rank:
                best_rank = rank
                winners = [player]
            elif rank == best_rank:
                winners.append(player)
        
        # Distribuer le pot
        share = pot // len(winners)
        for winner in winners:
            winner.stack += share
        
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

    def simulation(self, n: int, save_path: str = None):
        """
        Génère une simulation de n parties
        """
        print(f"=== Simulation de {n} parties ===\n")
        
        for game_num in range(n):
            self.game_count = game_num + 1
            
            # Augmenter les blinds tous les 10 parties
            if game_num > 0 and game_num % 10 == 0:
                self.big_blind = int(self.big_blind * 1.5)
                self.small_blind = int(self.small_blind * 1.5)
                print(f"Blindes augmentées: SB={self.small_blind}, BB={self.big_blind}")
            
            if (game_num + 1) % 10 == 0:
                print(f"Parties jouées: {game_num + 1}/{n}")
            
            # Jouer une partie
            game_data = self.game()
            if game_data is None:
                print("Simulation terminée (pas assez de joueurs)")
                break
            
            # Rotation des positions
            for player in self.players:
                player.position = (player.position + 1) % 5
            
            # Vérifier si au moins 2 joueurs ont des jetons
            active_count = sum(1 for p in self.players if p.stack > 0)
            if active_count < 2:
                print(f"Simulation terminée après {game_num + 1} parties")
                break
        
        # Calculer les statistiques
        stats = self._calculate_stats()
        
        # Sauvegarder
        if save_path:
            self.save_json(stats, save_path)
            print(f"\nDonnées sauvegardées: {save_path}")
        
        # Afficher les résultats
        print("\n=== Résultats ===")
        print(f"Parties jouées: {len(self.game_history)}")
        self._print_ranking()
        
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

    def _print_ranking(self):
        """
        Affiche le classement
        """
        ranking = sorted(
            zip(self.player_names, self.players),
            key=lambda x: x[1].stack,
            reverse=True
        )
        
        print("\nClassement:")
        for rank, (name, player) in enumerate(ranking, 1):
            profit = player.stack - self.initial_stack
            print(f"  {rank}. {name:20s}: {player.stack:6d} jetons ({profit:+6d})")

    def save_json(self, data: dict, path: str):
        """
        Sauvegarde dans un fichier JSON
        """
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def hand_rank(self, hand, board):
        """
        Retourne la meilleure combinaison possible avec hand + board
        """
        cards = hand + board
        if len(cards) < 5:
            return (1, cards)

        value_map = {v: i+2 for i, v in enumerate(self.values)}
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


if __name__ == "__main__":
    game = Game(big_blind=50, small_blind=25, stack=1000)
    stats = game.simulation(n=20, save_path="simulation.json")