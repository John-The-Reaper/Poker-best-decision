import numpy as np
# from stats.py import stat

class Calling_station():
    def __init__(self, position, stack): 
        self.win_chance = 0.50
        self.position = position
        self.stack = stack

        #Parameters
        self.min_bet = 0.1
        self.max_bet = 0.9
        self.behavior_level = 0.55
        self.aggressiveness = 12.0

    def stack_percent(self, win_chance, board, state): #calcul le pourcentage de la stack que le joueur veux miser
        exponent_input = -self.aggressiveness * (win_chance - self.behavior_level)
        result = self.min_bet + (self.max_bet - self.min_bet) / (1 + np.exp(exponent_input))
        return round(result,2) #renvoie 2 chiffres après la virgule
    
    def action(self, amount_to_call):
        if amount_to_call <= self.stack:  # Call dès qu'il peut
            self.stack -= amount_to_call
            return "call"
        elif amount_to_call > self.stack: # fold si pas assez pour Call
            return "fold"


#objet = calling_station(win_chance=0.5, position = False, stack=100)
#print(objet.stack_percent(objet.win_chance))
