import numpy as np


class Maniac():
    def __init__(self, stack): 
        self.stack = float(stack)

        # Paramètres de la fonction sigmoïde - RÉDUITS pour mises plus raisonnables
        self.multiplicator_min = 0.90  # RÉDUIT de 1.20
        self.multiplicator_max = 1.30  # RÉDUIT de 2.00
        self.behavior_level = 0.10     # Seuil très bas : ultra loose
        self.aggressiveness = 5.0      # Pente douce

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
        
        # Limitation au stack
        desired_total_bet_amount = min(desired_total_bet_amount, self.stack)

        # Décision d'action
        if amount <= 0:
            # Aucune mise à payer : check ou bet
            # Un maniac préfère bet que check, sauf si vraiment forcé
            if desired_total_bet_amount < 0.02 * self.stack:
                return {"check": True}
            else:
                return {"bet": round(desired_total_bet_amount, 0)}
        else:
            # Mise à payer : fold, call ou raise
            
            # PROTECTION: Maniac plus libéral mais pas totalement fou
            if amount > 0.75 * self.stack and win < 0.55:
                return {"fold": True}
            
            if amount > 0.5 * self.stack and win < 0.35:
                return {"fold": True}
            
            # Un maniac fold très rarement : seulement si optimal dit fold ET style très passif
            if optimal_choice == "fold" and style_factor < 1.0:
                # Même dans ce cas, avec un minimum d'équité, il peut call
                if win > 0.15:
                    return {"call": min(amount, self.stack)}
                else:
                    return {"fold": True}
            
            # Si le montant désiré est inférieur ou égal au call
            if desired_total_bet_amount <= amount:
                call_amount = min(amount, self.stack)
                return {"call": call_amount}
            
            # Si le montant désiré dépasse le call : raise
            else:
                return {"raise": round(desired_total_bet_amount, 0)}
