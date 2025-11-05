from matplotlib import pyplot as plt
#from Stats.py import Stats
#from Game.py import simulation

class GraphicalRendering:
  
  def __init__(self):
    self.simulation = Stats()
    self.data = simulation.game()
    pass

  def read_json(self, path:str):
    """
    Récupération des données présente grâce à la class Stats (ou via des la lecture des fichiers JSON
    """
    pass
    
  def players_data(self):
    """
    Traitement de donnée individuel des joueurs et sauvegarde dans un fichier JSON
    Returns : average_bet, win_rate, average_loss, average_win, 
    """
    pass

  def stack_evolution(self, players_name: list, players_data: dict):
    """
    Enregistre le graphique de l'évolution des staks des joueurs
    Format attendu : 
    {player_name : [stack1, stack2, stack3, ...], ...}
    """
    for player in players_name:
      plt.plot(players_data[player], label=player)
    plt.xlabel("Games Played")
    plt.ylabel("Stack")
    plt.title("Évolution des stacks des joueurs")
    plt.legend()
    plt.show()
    pass

