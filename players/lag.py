import numpy as np

class Lag():
    def __init__(self, stack): 
        self.stack = stack
        self.win_chance = 0.6

        #Parameters
        self.multiplicator_min = 0.85
        self.multiplicator_max = 1.10
        self.behavior_level = 0.40
        self.aggressiveness = 15.0

    def multiplicator(self, win_chance): #calcul le pourcentage de la stack que le joueur veux miser
        exponent_input = -self.aggressiveness * (win_chance - self.behavior_level)
        result = self.multiplicator_min + (self.multiplicator_max - self.multiplicator_min) / (1 + np.exp(exponent_input))
        return round(result,2) #renvoie 2 chiffres après la virgule

    
    def action(self, amount_to_call, position, optimal_bet_amount, optimal_choice):
        return print(amount_to_call, position, optimal_bet_amount, optimal_choice)
