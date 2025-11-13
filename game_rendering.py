import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Optional
import json
from pathlib import Path
from Game import Game


class GraphicalRendering:
    """
    Classe pour le rendu graphique des simulations de poker
    
    Fonctionnalités:
    - Évolution des stacks au cours du temps
    - Comparaison des performances des joueurs
    - Statistiques de victoires
    - Simulations multiples avec moyennes
    """
    
    def __init__(self, game: Optional[Game] = None):
        """
        Initialise le renderer graphique
        
        Args:
            game: Instance de Game (optionnel)
        """
        self.game = game
        self.colors = {
            'calling_station': '#FF6B6B',  # Rouge
            'tag': '#4ECDC4',              # Turquoise
            'lag': '#45B7D1',              # Bleu
            'maniac': '#FFA07A',           # Orange
            'nit': '#98D8C8',              # Vert menthe
            'best_choice': '#FFD93D'       # Jaune or
        }
        
        # Style matplotlib
        plt.style.use('seaborn-v0_8-darkgrid')
        
    def load_json(self, filepath: str) -> Dict:
        """
        Charge les résultats depuis un fichier JSON
        
        Args:
            filepath: Chemin vers le fichier JSON
            
        Returns:
            Dict contenant les données de simulation
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def plot_stack_evolution(self, data: Dict, save_path: Optional[str] = None):
        """
        Affiche l'évolution des stacks au cours des parties
        
        Args:
            data: Données de simulation (dict ou chemin vers JSON)
            save_path: Chemin pour sauvegarder le graphique (optionnel)
        """
        if isinstance(data, str):
            data = self.load_json(data)
        
        game_history = data.get('game_history', [])
        if not game_history:
            print("Pas de données d'historique à afficher")
            return
        
        # Extraire l'évolution des stacks
        players = list(game_history[0]['final_stacks'].keys())
        stack_evolution = {player: [] for player in players}
        game_numbers = []
        
        for game in game_history:
            game_numbers.append(game['game_number'])
            for player in players:
                stack_evolution[player].append(game['final_stacks'][player])
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(14, 8))
        
        for player in players:
            color = self.colors.get(player, '#000000')
            ax.plot(game_numbers, stack_evolution[player], 
                   label=player.replace('_', ' ').title(), 
                   color=color, linewidth=2.5, marker='o', markersize=3)
        
        ax.set_xlabel('Numéro de partie', fontsize=12, fontweight='bold')
        ax.set_ylabel('Stack (jetons)', fontsize=12, fontweight='bold')
        ax.set_title('Évolution des Stacks au cours de la Simulation', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='best', fontsize=10, framealpha=0.9)
        ax.grid(True, alpha=0.3)
        
        # Ajouter une ligne horizontale pour le stack initial
        initial_stack = data.get('player_stats', {}).get(players[0], {}).get('final_stack', 1000) - \
                       data.get('player_stats', {}).get(players[0], {}).get('profit', 0)
        ax.axhline(y=initial_stack, color='gray', linestyle='--', 
                  alpha=0.5, label=f'Stack initial ({initial_stack})')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Graphique sauvegardé: {save_path}")
        
        plt.show()
    
    def plot_final_results(self, data: Dict, save_path: Optional[str] = None):
        """
        Affiche les résultats finaux (stacks, profits, victoires)
        
        Args:
            data: Données de simulation
            save_path: Chemin pour sauvegarder le graphique (optionnel)
        """
        if isinstance(data, str):
            data = self.load_json(data)
        
        player_stats = data.get('player_stats', {})
        if not player_stats:
            print("Pas de statistiques de joueurs à afficher")
            return
        
        players = list(player_stats.keys())
        final_stacks = [player_stats[p]['final_stack'] for p in players]
        profits = [player_stats[p]['profit'] for p in players]
        wins = [player_stats[p]['wins'] for p in players]
        
        # Créer une figure avec 3 sous-graphiques
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        # 1. Stacks finaux
        colors = [self.colors.get(p, '#000000') for p in players]
        bars1 = axes[0].bar(range(len(players)), final_stacks, color=colors, alpha=0.8, edgecolor='black')
        axes[0].set_xlabel('Joueurs', fontsize=11, fontweight='bold')
        axes[0].set_ylabel('Stack Final (jetons)', fontsize=11, fontweight='bold')
        axes[0].set_title('Stacks Finaux', fontsize=13, fontweight='bold')
        axes[0].set_xticks(range(len(players)))
        axes[0].set_xticklabels([p.replace('_', '\n') for p in players], fontsize=9)
        axes[0].grid(axis='y', alpha=0.3)
        
        # Ajouter les valeurs sur les barres
        for bar in bars1:
            height = bar.get_height()
            axes[0].text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # 2. Profits/Pertes
        profit_colors = ['green' if p >= 0 else 'red' for p in profits]
        bars2 = axes[1].bar(range(len(players)), profits, color=profit_colors, alpha=0.7, edgecolor='black')
        axes[1].set_xlabel('Joueurs', fontsize=11, fontweight='bold')
        axes[1].set_ylabel('Profit/Perte (jetons)', fontsize=11, fontweight='bold')
        axes[1].set_title('Profits et Pertes', fontsize=13, fontweight='bold')
        axes[1].set_xticks(range(len(players)))
        axes[1].set_xticklabels([p.replace('_', '\n') for p in players], fontsize=9)
        axes[1].axhline(y=0, color='black', linestyle='-', linewidth=1.5)
        axes[1].grid(axis='y', alpha=0.3)
        
        # Ajouter les valeurs sur les barres
        for bar in bars2:
            height = bar.get_height()
            axes[1].text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height):+d}',
                        ha='center', va='bottom' if height >= 0 else 'top', 
                        fontsize=9, fontweight='bold')
        
        # 3. Nombre de victoires
        bars3 = axes[2].bar(range(len(players)), wins, color=colors, alpha=0.8, edgecolor='black')
        axes[2].set_xlabel('Joueurs', fontsize=11, fontweight='bold')
        axes[2].set_ylabel('Nombre de Victoires', fontsize=11, fontweight='bold')
        axes[2].set_title('Statistiques de Victoires', fontsize=13, fontweight='bold')
        axes[2].set_xticks(range(len(players)))
        axes[2].set_xticklabels([p.replace('_', '\n') for p in players], fontsize=9)
        axes[2].grid(axis='y', alpha=0.3)
        
        # Ajouter les valeurs et pourcentages sur les barres
        total_games = data.get('total_games', sum(wins))
        for bar, win_count in zip(bars3, wins):
            height = bar.get_height()
            percentage = (win_count / total_games * 100) if total_games > 0 else 0
            axes[2].text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}\n({percentage:.1f}%)',
                        ha='center', va='bottom', fontsize=8, fontweight='bold')
        
        plt.suptitle(f'Résultats de la Simulation ({total_games} parties)', 
                    fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Graphique sauvegardé: {save_path}")
        
        plt.show()
    
    def plot_win_rate_pie(self, data: Dict, save_path: Optional[str] = None):
        """
        Affiche un diagramme circulaire des taux de victoire
        
        Args:
            data: Données de simulation
            save_path: Chemin pour sauvegarder le graphique (optionnel)
        """
        if isinstance(data, str):
            data = self.load_json(data)
        
        player_stats = data.get('player_stats', {})
        if not player_stats:
            print("Pas de statistiques de joueurs à afficher")
            return
        
        players = list(player_stats.keys())
        wins = [player_stats[p]['wins'] for p in players]
        
        # Filtrer les joueurs avec 0 victoires pour le pie chart
        non_zero = [(p, w) for p, w in zip(players, wins) if w > 0]
        if not non_zero:
            print("Aucune victoire à afficher")
            return
        
        players_filtered, wins_filtered = zip(*non_zero)
        colors = [self.colors.get(p, '#000000') for p in players_filtered]
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        wedges, texts, autotexts = ax.pie(wins_filtered, 
                                          labels=[p.replace('_', ' ').title() for p in players_filtered],
                                          colors=colors,
                                          autopct='%1.1f%%',
                                          startangle=90,
                                          textprops={'fontsize': 11, 'fontweight': 'bold'},
                                          explode=[0.05 if w == max(wins_filtered) else 0 for w in wins_filtered])
        
        # Améliorer la lisibilité
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(12)
            autotext.set_fontweight('bold')
        
        total_games = data.get('total_games', sum(wins))
        ax.set_title(f'Répartition des Victoires\n({total_games} parties au total)', 
                    fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Graphique sauvegardé: {save_path}")
        
        plt.show()
    
    def run_multiple_simulations(self, n_simulations: int = 1000, 
                                initial_stack: int = 1000,
                                save_results: bool = True,
                                save_dir: str = "simulations"):
        """
        Lance plusieurs simulations et affiche les résultats moyens
        
        Args:
            n_simulations: Nombre de simulations à lancer
            initial_stack: Stack initial pour chaque joueur
            save_results: Sauvegarder les résultats individuels
            save_dir: Répertoire pour sauvegarder les résultats
        """
        if save_results:
            Path(save_dir).mkdir(exist_ok=True)
        
        print(f"\n{'='*60}")
        print(f"Lancement de {n_simulations} simulations")
        print(f"{'='*60}\n")
        
        all_results = []
        player_names = ['calling_station', 'tag', 'lag', 'maniac', 'nit', 'best_choice']
        
        # Accumulateurs pour les statistiques
        total_stacks = {name: [] for name in player_names}
        total_wins = {name: [] for name in player_names}
        total_games_played = []
        
        for sim_num in range(n_simulations):
            # Créer une nouvelle partie
            game = Game(stack=initial_stack)
            
            # Lancer la simulation
            results = game.simulation(save_path=None)
            all_results.append(results)
            
            # Sauvegarder si demandé
            if save_results:
                save_path = Path(save_dir) / f"simulation_{sim_num+1:03d}.json"
                game.save_json(results, str(save_path))
            
            # Accumuler les statistiques
            total_games_played.append(results['total_games'])
            for player_name in player_names:
                stats = results['player_stats'][player_name]
                total_stacks[player_name].append(stats['final_stack'])
                total_wins[player_name].append(stats['wins'])
            
            # Afficher la progression
            if (sim_num + 1) % 10 == 0:
                print(f"Progression: {sim_num + 1}/{n_simulations} simulations terminées")
        
        print(f"\n{'='*60}")
        print(f"Toutes les simulations sont terminées!")
        print(f"{'='*60}\n")
        
        # Calculer et afficher les statistiques
        self._display_aggregate_stats(total_stacks, total_wins, total_games_played, 
                                      initial_stack, n_simulations)
        
        # Créer les graphiques agrégés
        self._plot_aggregate_results(total_stacks, total_wins, n_simulations, initial_stack)
        
        return all_results
    
    def _display_aggregate_stats(self, total_stacks, total_wins, total_games_played, 
                                 initial_stack, n_simulations):
        """
        Affiche les statistiques agrégées des simulations multiples
        """
        print("📊 STATISTIQUES AGRÉGÉES\n")
        print(f"{'Joueur':<20} {'Stack Moyen':<15} {'Profit Moyen':<15} {'Victoires Moy.':<15} {'Taux Victoire':<15}")
        print("-" * 80)
        
        avg_games = np.mean(total_games_played)
        
        rankings = []
        for player_name in total_stacks.keys():
            avg_stack = np.mean(total_stacks[player_name])
            avg_profit = avg_stack - initial_stack
            avg_wins = np.mean(total_wins[player_name])
            win_rate = (avg_wins / avg_games * 100) if avg_games > 0 else 0
            
            rankings.append((player_name, avg_stack, avg_profit, avg_wins, win_rate))
        
        # Trier par stack moyen décroissant
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        for rank, (name, avg_stack, avg_profit, avg_wins, win_rate) in enumerate(rankings, 1):
            name_display = name.replace('_', ' ').title()
            print(f"{rank}. {name_display:<17} {avg_stack:<15.2f} {avg_profit:<+15.2f} {avg_wins:<15.2f} {win_rate:<15.1f}%")
        
        print("\n" + "-" * 80)
        print(f"Nombre moyen de parties par simulation: {avg_games:.1f}")
        print(f"Nombre total de simulations: {n_simulations}")
    
    def _plot_aggregate_results(self, total_stacks, total_wins, n_simulations, initial_stack):
        """
        Crée les graphiques pour les résultats agrégés
        """
        players = list(total_stacks.keys())
        
        # Calculer les moyennes et écarts-types
        avg_stacks = [np.mean(total_stacks[p]) for p in players]
        std_stacks = [np.std(total_stacks[p]) for p in players]
        avg_profits = [s - initial_stack for s in avg_stacks]
        std_profits = std_stacks  # Même écart-type
        avg_wins = [np.mean(total_wins[p]) for p in players]
        
        # Créer la figure
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        colors = [self.colors.get(p, '#000000') for p in players]
        x_pos = np.arange(len(players))
        
        # 1. Stack moyen avec écart-type
        axes[0, 0].bar(x_pos, avg_stacks, yerr=std_stacks, color=colors, 
                       alpha=0.8, edgecolor='black', capsize=5, error_kw={'linewidth': 2})
        axes[0, 0].set_xlabel('Joueurs', fontsize=11, fontweight='bold')
        axes[0, 0].set_ylabel('Stack Moyen (jetons)', fontsize=11, fontweight='bold')
        axes[0, 0].set_title(f'Stack Moyen après {n_simulations} Simulations', 
                            fontsize=13, fontweight='bold')
        axes[0, 0].set_xticks(x_pos)
        axes[0, 0].set_xticklabels([p.replace('_', '\n') for p in players], fontsize=9)
        axes[0, 0].axhline(y=initial_stack, color='gray', linestyle='--', label='Stack initial')
        axes[0, 0].legend()
        axes[0, 0].grid(axis='y', alpha=0.3)
        
        # 2. Profit moyen avec écart-type
        profit_colors = ['green' if p >= 0 else 'red' for p in avg_profits]
        axes[0, 1].bar(x_pos, avg_profits, yerr=std_profits, color=profit_colors, 
                       alpha=0.7, edgecolor='black', capsize=5, error_kw={'linewidth': 2})
        axes[0, 1].set_xlabel('Joueurs', fontsize=11, fontweight='bold')
        axes[0, 1].set_ylabel('Profit Moyen (jetons)', fontsize=11, fontweight='bold')
        axes[0, 1].set_title('Profit/Perte Moyen', fontsize=13, fontweight='bold')
        axes[0, 1].set_xticks(x_pos)
        axes[0, 1].set_xticklabels([p.replace('_', '\n') for p in players], fontsize=9)
        axes[0, 1].axhline(y=0, color='black', linestyle='-', linewidth=1.5)
        axes[0, 1].grid(axis='y', alpha=0.3)
        
        # 3. Distribution des stacks (boxplot)
        stack_data = [total_stacks[p] for p in players]
        bp = axes[1, 0].boxplot(stack_data, labels=[p.replace('_', '\n') for p in players],
                                patch_artist=True, showmeans=True)
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        axes[1, 0].set_xlabel('Joueurs', fontsize=11, fontweight='bold')
        axes[1, 0].set_ylabel('Stack (jetons)', fontsize=11, fontweight='bold')
        axes[1, 0].set_title('Distribution des Stacks', fontsize=13, fontweight='bold')
        axes[1, 0].grid(axis='y', alpha=0.3)
        axes[1, 0].tick_params(axis='x', labelsize=9)
        
        # 4. Victoires moyennes
        axes[1, 1].bar(x_pos, avg_wins, color=colors, alpha=0.8, edgecolor='black')
        axes[1, 1].set_xlabel('Joueurs', fontsize=11, fontweight='bold')
        axes[1, 1].set_ylabel('Victoires Moyennes', fontsize=11, fontweight='bold')
        axes[1, 1].set_title('Nombre Moyen de Victoires', fontsize=13, fontweight='bold')
        axes[1, 1].set_xticks(x_pos)
        axes[1, 1].set_xticklabels([p.replace('_', '\n') for p in players], fontsize=9)
        axes[1, 1].grid(axis='y', alpha=0.3)
        
        for i, v in enumerate(avg_wins):
            axes[1, 1].text(i, v, f'{v:.1f}', ha='center', va='bottom', 
                           fontsize=9, fontweight='bold')
        
        plt.suptitle(f'Analyse Agrégée de {n_simulations} Simulations', 
                    fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        plt.show()
    
    def plot_all_from_json(self, json_path: str, save_plots: bool = False, 
                          output_dir: str = "plots"):
        """
        Génère tous les graphiques à partir d'un fichier JSON
        
        Args:
            json_path: Chemin vers le fichier JSON
            save_plots: Sauvegarder les graphiques
            output_dir: Répertoire de sortie pour les graphiques
        """
        if save_plots:
            Path(output_dir).mkdir(exist_ok=True)
        
        data = self.load_json(json_path)
        
        print(f"\n{'='*60}")
        print(f"Génération des graphiques depuis: {json_path}")
        print(f"{'='*60}\n")
        
        # 1. Évolution des stacks
        print("📈 Graphique 1: Évolution des stacks...")
        save_path_1 = Path(output_dir) / "stack_evolution.png" if save_plots else None
        self.plot_stack_evolution(data, save_path_1)
        
        # 2. Résultats finaux
        print("📊 Graphique 2: Résultats finaux...")
        save_path_2 = Path(output_dir) / "final_results.png" if save_plots else None
        self.plot_final_results(data, save_path_2)
        
        # 3. Diagramme circulaire
        print("🥧 Graphique 3: Répartition des victoires...")
        save_path_3 = Path(output_dir) / "win_rate_pie.png" if save_plots else None
        self.plot_win_rate_pie(data, save_path_3)
        
        print(f"\n{'='*60}")
        print("Tous les graphiques ont été générés!")
        print(f"{'='*60}\n")


# Exemple d'utilisation
if __name__ == "__main__":
    # Initialiser le renderer
    renderer = GraphicalRendering()
    
    # Option 1: Charger et visualiser un JSON existant
    # print("Option 1: Visualisation d'un JSON existant")
    # renderer.plot_all_from_json("resultats_simulation.json", save_plots=True)
    
    # Option 2: Lancer une simulation et visualiser
    print("\nOption 2: Nouvelle simulation")
    game = Game(stack=1000, num_simulations=2500) 
    # Plus num_simulations est élevé, plus les calculs d'équité sont précis mais plus longs.
    renderer.game = game
    results = game.simulation(save_path="nouvelle_simulation.json")
    renderer.plot_all_from_json("nouvelle_simulation.json")
    
    # Option 3: Lancer 100 simulations et analyser
    # print("\nOption 3: 100 simulations")
    # renderer.run_multiple_simulations(n_simulations=100, initial_stack=1000)
