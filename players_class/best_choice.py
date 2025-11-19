import numpy as np


class best_choice():
    def __init__(self, stack): 
        self.stack = float(stack)
    
    def action(self, amount_to_call, position=None, optimal_choice=None, optimal_bet_amount=None, win_chance=None):
        
        # Validations
        try:
            amount = float(amount_to_call) if amount_to_call is not None else 0.0
        except Exception:
            amount = 0.0
            
        if amount < 0:
            amount = 0.0
            
        # Si pas de choix optimal spécifié, fold par défaut
        if optimal_choice is None:
            return {"fold": True}
        
        # Si stack épuisé
        if self.stack <= 0:
            return {"fold": True}
        
        # Exécution de l'action optimale
        if optimal_choice == "check":
            return {"check": True}

        elif optimal_choice == "call":
            # PROTECTION: Ne pas call plus de 40% du stack sans bonne équité
            if amount > 0.4 * self.stack:
                try:
                    equity = float(win_chance) if win_chance is not None else 0.3
                except Exception:
                    equity = 0.3
                if equity < 0.55:
                    return {"fold": True}
            
            # Limiter au stack disponible
            call_amount = min(amount, self.stack)
            return {"call": call_amount} 
   
        elif optimal_choice in ("bet", "raise"):
            # Validation et limitation du montant
            try:
                bet_amt = float(optimal_bet_amount) if optimal_bet_amount is not None else 0.0
            except Exception:
                bet_amt = 0.0
                
            if bet_amt < 0:
                bet_amt = 0.0
            
            # Limiter au stack
            bet_amt = min(bet_amt, self.stack)
            
            # Si le montant est trop petit, check ou call à la place
            if bet_amt < 0.01 * self.stack:
                if amount <= 0:
                    return {"check": True}
                else:
                    return {"call": min(amount, self.stack)}
            
            return {optimal_choice: round(bet_amt, 0)}

        else:  # fold ou toute autre valeur
            return {"fold": True}
