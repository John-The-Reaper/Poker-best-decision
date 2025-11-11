import numpy as np

class Maniac():
    def __init__(self, stack): 
        self.stack = stack

        self.multiplicator_min = 1.20
        self.multiplicator_max = 2.00
        self.behavior_level = 0.10
        self.aggressiveness = 5.0

    def multiplicator(self, win_chance): #calcul le pourcentage de la stack que le joueur veux miser
        exponent_input = -self.aggressiveness * (win_chance - self.behavior_level)
        result = self.multiplicator_min + (self.multiplicator_max - self.multiplicator_min) / (1 + float(np.exp(exponent_input)))
        
        # [CORRECTION] Caster en float standard pour éviter l'erreur de type
        return float(round(result,2))

    
    # Applicable à tag.py, nit.py, et maniac.py
    def action(self, amount_to_call, position, optimal_choice, optimal_bet_amount, win_chance):
        
        # 1. Calcul du style factor et application de la position
        style_factor = self.multiplicator(win_chance) 
        
        # Application des facteurs de position (inchangés)
        if position == "button":
            style_factor *= 1.15
        # ... (Autres positions)
        elif position == "utg":
            style_factor *= 0.90
        else: # "big_blind"
            style_factor *= 1.00 # S'assurer que tous les cas de position sont couverts ou que le else est suffisant.

        # Montant TOTAL de la mise désirée (basé sur l'optimal ajusté)
        desired_total_bet_amount = optimal_bet_amount * style_factor
        
        # Limitation au stack
        if desired_total_bet_amount > self.stack:
            desired_total_bet_amount = self.stack

        # --- Logique d'Action Corrigée ---
        
        # 1. Pas de mise à payer (Check/Bet)
        if amount_to_call == 0:
            if optimal_choice == "check" or desired_total_bet_amount < 0.05 * self.stack:
                return {"check": True}
            else:
                return {"bet": round(desired_total_bet_amount, 0)}

        # 2. Mise à payer (Fold/Call/Raise)
        else:
            # Si le montant désiré est inférieur ou égal au montant à call
            if desired_total_bet_amount <= amount_to_call:
                # Si le style est trop passif ou optimal_choice est fold, il fold
                if optimal_choice == "fold" and style_factor < 1.0:
                    return {"fold": True}
                else:
                    return {"call": amount_to_call}
            
            # S'il veut mettre plus que le call, c'est un raise
            elif desired_total_bet_amount > amount_to_call:
                # Montant TOTAL de la mise/relance
                return {"raise": round(desired_total_bet_amount, 0)}
            
            # Cas de sécurité
            else:
                return {"fold": True}