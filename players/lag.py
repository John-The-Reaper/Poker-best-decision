import numpy as np # <-- Correction 1 : Import de numpy
# from stats.py import stat

class Lag():
    def __init__(self, position, stack): 
        self.win_chance = 0.50
        self.position = position
        self.stack = stack

        #Parameters
        self.min_bet = 0.20
        self.max_bet = 1.00
        self.behavior_level = 0.40
        self.aggressiveness = 15.0

    def stack_percent(self, win_chance, board, state): #calcul le pourcentage de la stack que le joueur veux miser
        exponent_input = -self.aggressiveness * (win_chance - self.behavior_level)
        result = self.min_bet + (self.max_bet - self.min_bet) / (1 + np.exp(exponent_input))
        return round(result,2) #renvoie 2 chiffres après la virgule
    
    def action(self, amount_to_call, position):
        if position == "utg":
             position = 1.15
        elif position == "hijack":
             position = 1.18
        elif position == "button":
            position = 1.45
        elif position == "small_blind":
            position = 1.35
        elif position == "big_blind":
            position = 1.00
        elif position == "cutt_off":
            position = 1.25
        else:
            position = 1

        bot_bet = (self.stack_percent(self.win_chance) * self.stack)*position

        if amount_to_call == 0 and self.stack_percent(self.win_chance) < 0.1:
            return {"check": True}
        
        elif amount_to_call <= bot_bet >= amount_to_call * 1.1:
            return {"call": amount_to_call}

        elif amount_to_call < bot_bet:
            return {"bet": round(bot_bet,0)}

        elif amount_to_call > bot_bet:
            return {"fold": True}
        
        




#objet = Lag(win_chance=0.5, position = False, stack=100)
#print(objet.stack_percent(objet.win_chance))
