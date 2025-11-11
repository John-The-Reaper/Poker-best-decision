import numpy as np

class best_choice():
    def __init__(self, stack): 
        self.stack = stack
        self.win_chance = 0.6
    
    def action(self, amount_to_call, position, optimal_choice, optimal_bet_amount, win_chance):
        
        if optimal_choice == "check":
            return {"check": True}

        elif optimal_choice == "call":
            # Retourne l'action et le montant total à CALLER
            return {"call": amount_to_call} 
   
        elif optimal_choice in ("bet", "raise"):
            # Retourne l'action et le montant TOTAL du BET/RAISE
            return {optimal_choice: round(optimal_bet_amount,0)}

        else: # fold
            return {"fold": True}