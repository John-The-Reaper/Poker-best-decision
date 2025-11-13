import numpy as np


class Nit():
    """Joueur Nit (Very Tight).
    
    Comportement :
    - Joue très peu de mains, seulement les meilleures (ultra tight)
    - Seuil comportemental très élevé (0.75) : mise fort uniquement avec nuts
    - Mise petite avec mains faibles, overbet massif avec nuts
    - Fold facilement face à l'agression
    """
    
    def __init__(self, stack): 
        self.stack = float(stack)

        # Paramètres de la fonction sigmoïde - AJUSTÉS pour mises plus raisonnables
        self.multiplicator_min = 0.10  # Ne bluffe presque jamais
        self.multiplicator_max = 1.20  # RÉDUIT de 1.60 - Overbet modéré avec nuts
        self.behavior_level = 0.75     # Seuil très élevé : ultra tight
        self.aggressiveness = 5.0      # Pente douce

    def multiplicator(self, win_chance): 
        """Calcule le multiplicateur de mise basé sur win_chance via sigmoïde."""
        exponent_input = -self.aggressiveness * (win_chance - self.behavior_level)
        result = self.multiplicator_min + (self.multiplicator_max - self.multiplicator_min) / (1 + float(np.exp(exponent_input)))
        return float(round(result, 2))

    def action(self, amount_to_call, position=None, optimal_choice=None, optimal_bet_amount=None, win_chance=None):
        """Décide de l'action à prendre.
        
        Args:
            amount_to_call: montant à payer
            position: position du joueur ("button", "utg", etc.)
            optimal_choice: recommandation optimale
            optimal_bet_amount: montant de mise optimal
            win_chance: probabilité de gagner (0..1)
            
        Returns:
            dict: action à exécuter
        """
        
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
            # Un Nit check plus souvent, mais bet quand il a une vraie main
            if optimal_choice == "check":
                return {"check": True}
            elif desired_total_bet_amount < 0.03 * self.stack:  # Nit check plus facilement
                return {"check": True}
            else:
                return {"bet": round(desired_total_bet_amount, 0)}
        else:
            # Mise à payer : fold, call ou raise
            
            # Un Nit fold facilement : si optimal recommande fold OU si le style est passif
            if optimal_choice == "fold" or style_factor < 0.8:
                # Exception : si on a un très bon style_factor (nuts), on reste
                if style_factor >= 1.3:
                    # On a les nuts, on call ou raise selon desired_total_bet_amount
                    if desired_total_bet_amount <= amount:
                        return {"call": min(amount, self.stack)}
                    else:
                        return {"raise": round(desired_total_bet_amount, 0)}
                else:
                    return {"fold": True}
            
            # Si le montant désiré est inférieur ou égal au call
            if desired_total_bet_amount <= amount:
                call_amount = min(amount, self.stack)
                return {"call": call_amount}
            
            # Si le montant désiré dépasse le call : raise
            else:
                return {"raise": round(desired_total_bet_amount, 0)}