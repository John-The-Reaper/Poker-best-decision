import numpy as np

class best_choice():
    def __init__(self, stack): 
        self.stack = stack
        self.win_chance = 0.6
    
    def action(self, amount_to_call, position, optimal_choice, optimal_bet_amount, win_chance):
        
        if optimal_choice == "check":
            return {"check": True}

        elif optimal_choice == "call":
            return {"call": amount_to_call}
   
        elif optimal_choice == "call":
            return {"bet": round(optimal_bet_amount,0)}

        else:
            return {"fold": True}
