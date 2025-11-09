from Game import Game
import pprint

# === CONFIGURATION ===
NUM_PARTIES = 20       # nombre de parties à simuler
SAVE_PATH = "resultats_simulation.json"  # optionnel (None pour ne pas sauvegarder)

# === LANCEMENT DU TEST ===
print("=== DÉMARRAGE DE LA SIMULATION DE POKER ===")
game = Game(big_blind=50, small_blind=25, stack=1000)

# Lancer une simulation complète
stats = game.simulation(save_path=SAVE_PATH)

# === AFFICHAGE DES RÉSULTATS GLOBAUX ===
print("\n=== STATISTIQUES GLOBALES ===")
print(f"Nombre total de parties jouées : {stats['total_games']}")

for name, data in stats["player_stats"].items():
    print(f"{name:15s} | Stack final: {data['final_stack']:5.2f} | "
          f"Profit: {data['profit']:>+6.2f} | Victoires: {data['wins']}")

# === APERÇU DE QUELQUES PARTIES ===
print("\n=== EXEMPLES DE PARTIES ===")
for g in stats["game_history"][:min(5, len(stats["game_history"]))]:
    print(f"Partie #{g['game_number']} → Gagnant: {g['winner']}, Pot: {g['pot']}, Board: {g['board']}")

# === CLASSEMENT FINAL ===
print("\n=== CLASSEMENT FINAL ===")
ranking = sorted(
    [(n, p.stack) for n, p in zip(game.player_names, game.players)],
    key=lambda x: x[1],
    reverse=True
)
for rank, (name, stack) in enumerate(ranking, 1):
    profit = stack - game.initial_stack
    print(f"{rank}. {name:15s}: {stack:5.2f} jetons ({profit:+5.2f})")


print("\n✅ Test terminé !")
if SAVE_PATH:
    print(f"Résultats sauvegardés dans : {SAVE_PATH}")

