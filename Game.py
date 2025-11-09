from players.calling_station import Calling_station
from players.tag import Tag
from players.lag import Lag
from players.maniac import Maniac 
from players.nit import Nit
from players.best_choice import best_choice
from Stats import Stat
from deal import Deal
from collections import Counter
import json

class Game:
    def __init__(self, big_blind=50, small_blind=25, stack=1000):
        self.big_blind = big_blind
        self.small_blind = small_blind  
        self.initial_stack = stack
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
        
        sb_amount = min(self.small_blind, sb_player.stack)
        sb_player.stack -= sb_amount
        current_bets[id(sb_player)] = sb_amount
        pot += sb_amount
        
        bb_amount = min(self.big_blind, bb_player.stack)
        bb_player.stack -= bb_amount
        current_bets[id(bb_player)] = bb_amount
        pot += bb_amount
        
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
        max_rounds = 10
        round_count = 0
        
        while round_count < max_rounds:
            round_count += 1
            someone_acted = False
            current_bet = max(current_bets.values()) if current_bets else 0

            for player in active_players[:]:
                if player.stack == 0:
                    continue
                
                amount_to_call = current_bet - current_bets[id(player)]
                equity, optimal_bet, optimal_choice = self.get_stats(
                    player_hand=player.hand,
                    board=board,
                    pot=pot,
                    amount_to_call=amount_to_call
                )
                action = self._get_player_action(player, amount_to_call, optimal_bet, optimal_choice)

                # 🩵 FIX : on récupère le montant sans re-retirer du stack (les joueurs l'ont déjà fait)
                if 'fold' in action:
                    active_players.remove(player)
                    someone_acted = True
                    if len(active_players) == 1:
                        return pot, active_players, current_bets

                elif 'check' in action:
                    if amount_to_call == 0:
                        someone_acted = True
                    else:
                        active_players.remove(player)

                elif 'call' in action:
                    call_amount = action.get('call', amount_to_call)
                    pot += call_amount  # on ajoute seulement au pot
                    current_bets[id(player)] += call_amount
                    someone_acted = True

                elif 'bet' in action or 'raise' in action:
                    bet_amount = action.get('bet', action.get('raise', 0))
                    total_to_add = amount_to_call + bet_amount
                    pot += total_to_add  # 🩵 uniquement ajout au pot
                    current_bets[id(player)] += total_to_add
                    someone_acted = True
            
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

    def _get_player_action(self, player, amount_to_call, optimal_bet, optimal_choice):
        try:
            position_name = self._get_position_name(player.position)
            result = player.action(amount_to_call, position_name, optimal_bet, optimal_choice)
            print(result)
            if isinstance(result, str):
                return {result: True}
            return result
        except Exception as e:
            print(f"Erreur action joueur pos={player.position}: {e}")
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
            rank, _ = self.hand_rank(player.hand, board)
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
        print(f"=== Simulation jusqu'à élimination complète ===")
        
        # Vérifier les jetons au départ
        total_start = sum(p.stack for p in self.players)
        print(f"Jetons au départ: {total_start}")
        print(f"Joueurs actifs: {len([p for p in self.players if p.stack > 0])}")
        
        game_num = 0
        while True:  # Boucle infinie jusqu'à élimination
            self.game_count = game_num + 1
            
            # Vérifier combien de joueurs ont encore des jetons
            active_count = sum(1 for p in self.players if p.stack > 0)
            
            # Si un seul joueur reste, la simulation est terminée
            if active_count <= 1:
                print(f"🏆 Simulation terminée après {game_num} parties!")
                winner = next((p for p in self.players if p.stack > 0), None)
                if winner:
                    winner_name = self.player_names[self.players.index(winner)]
                    print(f"🏆 GAGNANT: {winner_name} avec {winner.stack} jetons!")
                break
            
            # Augmenter les blinds tous les 10 parties
            if game_num > 0 and game_num % 10 == 0:
                self.big_blind = int(self.big_blind * 1.5)
                self.small_blind = int(self.small_blind * 1.5)
                print(f"Blindes augmentées: SB={self.small_blind}, BB={self.big_blind}")
            
            # Affichage de progression
            if (game_num + 1) % 10 == 0:
                remaining = sum(1 for p in self.players if p.stack > 0)
                print(f"Parties jouées: {game_num + 1} | Joueurs restants: {remaining}")
                
                # Vérifier conservation des jetons
                total_current = sum(p.stack for p in self.players)
                if total_current != total_start:
                    print(f"⚠️  ATTENTION: Jetons={total_current} (devrait être {total_start})")
            
            # Jouer une partie
            game_data = self.game()
            if game_data is None:
                print("Simulation terminée (pas assez de joueurs)")
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
            print(f"Données sauvegardées: {save_path}")
        
        # Afficher les résultats
        print("=== Résultats ===")
        print(f"Parties jouées: {len(self.game_history)}")
        
        # Vérifier conservation des jetons
        total_end = sum(p.stack for p in self.players)
        print(f"Jetons au départ: {total_start}")
        print(f"Jetons à la fin: {total_end}")
        if total_end != total_start:
            print(f"⚠️  PERTE DE {total_start - total_end} JETONS!")
        else:
            print("✅ Tous les jetons sont conservés")
        
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
            print(f"  {rank}. {name:20s}: {player.stack:2f} jetons ({profit:+.2f})")

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
        # Assurer que board n'est pas None
        if board is None:
            board = []

        stat = Stat(hand=player_hand, board=board, pot=pot, amount_to_call=amount_to_call)
        return stat.win_chance_and_choice()

    def hand_rank(self, hand, board):
        """
        Retourne la meilleure combinaison possible avec hand + board en lui attribuant une valeur numérique (1-9)
        """
       
        cards = hand + board
        if len(cards) < 5: # Comme la fonction est utilisée à la fin
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


