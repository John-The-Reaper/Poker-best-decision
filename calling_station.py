import numpy as np
# from stats.py import stat

class Calling_station():
    def __init__(self, win_chance, position, stack, amount_to_call): 
        self.win_chance = win_chance
        self.position = position
        self.stack = stack
        self.amount_to_call = amount_to_call

        #Parameters
        self.min_bet = 0.1
        self.max_bet = 0.9
        self.behavior_level = 0.55
        self.aggressiveness = 12.0

    def stack_percent(self, win_chance): #calcul le pourcentage de la stack que le joueur veux miser
        exponent_input = -self.aggressiveness * (win_chance - self.behavior_level)
        result = self.min_bet + (self.max_bet - self.min_bet) / (1 + np.exp(exponent_input))
        return round(result,2) #renvoie 2 chiffres après la virgule
    
    def action(self):
        if self.amount_to_call <= self.stack:  # Call dès qu'il peut
            return "call"
        elif self.amount_to_call > self.stack: # fold si pas assez pour Call
            return "fold"


objet = Tag(win_chance=0.5, position = False, stack=100)
print(objet.stack_percent(objet.win_chance))
