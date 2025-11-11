import numpy as np

class Calling_station():
    def __init__(self, stack): 
        self.stack = stack
        self.win_chance = 0.6

        #Parameters
        self.min_bet = 0.05
        self.max_bet = 0.20
        self.behavior_level = 0.50
        self.aggressiveness = 2.0

    def multiplicator(self, win_chance): #calcul le pourcentage de la stack que le joueur veux miser
        exponent_input = -self.aggressiveness * (win_chance - self.behavior_level)
        # [CORRECTIF] Ajout du float() ici pour être cohérent
        result = self.min_bet + (self.max_bet - self.min_bet) / (1 + float(np.exp(exponent_input))) 
        
        return float(round(result,2))
    
    def action(self, amount_to_call, position, optimal_choice, optimal_bet_amount, win_chance):
        
        # Le facteur de position est appliqué ici
        position_factor = 1.0
        if position == "utg":
            position_factor = 1.15
        elif position == "hijack":
            position_factor = 1.18
        elif position == "button":
            position_factor = 1.45
        elif position == "small_blind":
            position_factor = 1.35
        elif position == "big_blind":
            position_factor = 1.00 # Neutre
        elif position == "cutt_off":
            position_factor = 1.25

        # [CORRECTIF] Appel de 'multiplicator' au lieu de 'stack_percent'
        desired_total_bet_amount = (self.multiplicator(0.6) * self.stack) * position_factor

        # --- Logique d'Action Corrigée ---

        # 1. Pas de mise (Check/Bet)
        if amount_to_call == 0:
            # [CORRECTIF] Appel de 'multiplicator' au lieu de 'stack_percent'
            if self.multiplicator(0.6) < 0.1: 
                return {"check": True}
            else:
                bet_size = desired_total_bet_amount
                return {"bet": round(bet_size, 0)}

        # 2. Mise à payer (Fold/Call/Raise)
        else:
            if amount_to_call <= desired_total_bet_amount:
                if desired_total_bet_amount > amount_to_call * 2.5 and optimal_choice in ("bet", "raise"):
                    total_raise_amount = min(self.stack, amount_to_call * 2.5) 
                    return {"raise": round(total_raise_amount, 0)}
                else:
                    return {"call": amount_to_call}
            elif amount_to_call > desired_total_bet_amount:
                return {"fold": True}