import numpy as np # <-- Correction 1 : Import de numpy
# from stats.py import stat

class Tag():
    def __init__(self, position, stack): 
        self.win_chance = 0.50
        self.position = position
        self.stack = stack

        #Parameters
        self.min_bet = 0.1
        self.max_bet = 0.9
        self.behavior_level = 0.55
        self.aggressiveness = 5.0

    def stack_percent(self, win_chance, board, state): #calcul le pourcentage de la stack que le joueur veux miser
        exponent_input = -self.aggressiveness * (win_chance - self.behavior_level)
        result = self.min_bet + (self.max_bet - self.min_bet) / (1 + np.exp(exponent_input))
        return round(result,2) #renvoie 2 chiffres après la virgule
    
    def action(self, amount_to_call, board, state):
        bot_bet = self.stack_percent(self.win_chance) * self.stack

        if amount_to_call == 0 and self.stack_percent(self.win_chance) < 0.1:
            return {"check": True}
        
        elif amount_to_call <= bot_bet >= amount_to_call * 1.1:
            return {"call": amount_to_call}

        elif amount_to_call < bot_bet:
            return {"bet": round(bot_bet,0)}

        elif amount_to_call > bot_bet:
            return {"fold": True}
        
        




#objet = Tag(win_chance=0.5, position = False, stack=100)
#print(objet.stack_percent(objet.win_chance))
