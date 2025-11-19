import numpy as np


class Tag():
    def __init__(self, stack): 
        self.stack = float(stack)

        # Paramètres de la fonction sigmoïde
        self.multiplicator_min = 0.40
        self.multiplicator_max = 1.00
        self.behavior_level = 0.55
        self.aggressiveness = 12.0

    def multiplicator(self, win_chance): 
        """Calcule le multiplicateur de mise basé sur win_chance via sigmoïde."""
        exponent_input = -self.aggressiveness * (win_chance - self.behavior_level)
        result = self.multiplicator_min + (self.multiplicator_max - self.multiplicator_min) / (1 + float(np.exp(exponent_input)))
        return float(round(result, 2))

    def action(self, amount_to_call, position=None, optimal_choice=None, optimal_bet_amount=None, win_chance=None):
        
        # Validations
        try:
            amount = float(amount_to_call) if amount_to_call is not None else 0.0
        except Exception:
            amount = 0.0
            
        if amount < 0:
            amount = 0.0
            
        try:
            win = float(win_chance) if win_chance is not None else 0.5
        except Exception:
            win = 0.5
            
        try:
            opt_bet = float(optimal_bet_amount) if optimal_bet_amount is not None else 0.0
        except Exception:
            opt_bet = 0.0
            
        if self.stack <= 0:
            return {"fold": True}
        
        # Calcul du style_factor basé sur win_chance
        style_factor = self.multiplicator(win)
        
        # Ajustement selon la position
        if position == "button":
            style_factor *= 1.15
        elif position == "utg":
            style_factor *= 0.90
        # autres positions : pas d'ajustement
        
        # Calcul du montant de mise désiré
        desired_total_bet_amount = opt_bet * style_factor
        
        # LOGIQUE D'EXPLOITATION : Si optimal_choice recommande "call" mais que nous avons une main forte,
        # transformer en raise pour extraire de la valeur (contre calling stations notamment)
        if optimal_choice == "call" and win > 0.55 and amount > 0:
            aggressive_raise = amount * 3  # Relance standard 3x
            desired_total_bet_amount = max(desired_total_bet_amount, aggressive_raise)
            optimal_choice = "raise"
        
        # Limitation au stack
        desired_total_bet_amount = min(desired_total_bet_amount, self.stack)

        # Décision d'action
        if amount <= 0:
            # Aucune mise à payer : check ou bet
            # Ne check que si optimal dit check OU si la mise désirée est vraiment minuscule
            if optimal_choice == "check":
                return {"check": True}
            elif desired_total_bet_amount < 0.02 * self.stack:  # RÉDUIT de 0.05 à 0.02
                return {"check": True}
            else:
                return {"bet": round(desired_total_bet_amount, 0)}
        else:
            # Mise à payer : fold, call ou raise
            
            # PROTECTION: Ne jamais call plus de 50% du stack sans une très bonne équité
            if amount > 0.5 * self.stack and win < 0.65:
                return {"fold": True}
            
            # PROTECTION: Ne jamais call plus de 30% du stack sans équité décente  
            if amount > 0.3 * self.stack and win < 0.50:
                return {"fold": True}
            
            # Si le montant désiré est inférieur ou égal au call
            if desired_total_bet_amount <= amount:
                # Fold si optimal recommande fold
                if optimal_choice == "fold":
                    return {"fold": True}
                # Sinon call (sauf si stack insuffisant)
                call_amount = min(amount, self.stack)
                return {"call": call_amount}
            
            # Si le montant désiré dépasse le call : raise
            else:
                return {"raise": round(desired_total_bet_amount, 0)}
