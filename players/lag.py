import numpy as np
import Game from ../Game.py

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

    
    def action(self, amount_to_call, position, optimal_choice, optimal_bet_amount, win_chance):
        style_factor = self.multiplicator(win_chance) 
        #Avantage position impactant style_factor :
        if position == "button":
            style_factor *= 1.15  # Très agressif en position (+ 15%)
        elif position == "cutt_off":
            style_factor *= 1.10  # Agressif (+ 10%)
        elif position == "hijack":
            style_factor *= 1.05  # Légèrement agressif (+ 5%)
        elif position == "utg":
            style_factor *= 0.90  # Très passif hors position (- 10%)
        elif position == "small_blind":
            style_factor *= 0.95  # Passif (- 5%)
        else: # "big_blind" (neutre)
            style_factor *= 1.00
        
        desired_bet_amount = optimal_bet_amount * style_factor
        
        if desired_bet_amount > self.stack: #le joueur ne parie pas ce qu'il n'a pas
            desired_bet_amount = self.stack

        if amount_to_call == 0 and optimal_choice == "check":
            return {"check": True}

        elif desired_bet_amount <= amount_to_call <= optimal_bet_amount or optimal_bet_amount <= amount_to_call <= desired_bet_amount:
            self.stack -= amount_to_call
            return {"call": amount_to_call}
            
        elif amount_to_call < desired_bet_amount and amount_to_call < optimal_bet_amount:
            self.stack -= desired_bet_amount
            return {"bet": round(desired_bet_amount,0)}

        else:
            return {"fold": True}
