try:
    import numpy as np
except Exception:
    import random as _random

    class _Random:
        @staticmethod
        def rand():
            return _random.random()

    class _NpFallback:
        random = _Random()

    np = _NpFallback()


class Calling_station():
    def __init__(self, stack):
        self.stack = float(stack)
        self.min_equity_to_call = 0.25
        self.max_stack_percent_to_call = 0.30
        self.small_call_threshold_percent = 0.02
        self.random_call_prob = 0.08
        self.all_in_min_equity = 0.70

    def action(self, amount_to_call, position=None, optimal_choice=None, optimal_bet_amount=None, win_chance=None):
        """Décide d'appeler, se coucher ou checker.

        Args:
            amount_to_call: montant requis pour rester dans le coup (>= 0)
            position, optimal_choice, optimal_bet_amount: paramètres présents pour compatibilité (optionnels)
            win_chance: probabilité (0..1) de gagner

        Returns:
            dict: une action parmi {"check": True}, {"call": amount}, {"fold": True}
        """

        # Normalisations et validations
        try:
            amount = float(amount_to_call)
        except Exception:
            amount = 0.0

        if win_chance is None:
            win = 0.0
        else:
            try:
                win = float(win_chance)
            except Exception:
                win = 0.0

        # bord cases
        if self.stack <= 0:
            return {"fold": True}

        if amount <= 0:
            return {"check": True}

        # petit call automatique : si l'effort est négligeable par rapport au stack
        if amount <= self.small_call_threshold_percent * self.stack:
            return {"call": amount}

        # Si l'appel exige tout (all-in adverse / on doit mettre >= stack)
        if amount >= self.stack:
            # n'appelle all-in que si équité très forte
            if win >= self.all_in_min_equity:
                return {"call": self.stack}
            else:
                return {"fold": True}

        # Pour les appels normaux, vérifier le pourcentage du stack
        percent = amount / self.stack

        # Si c'est raisonnable et l'équité est suffisante -> call
        if percent <= self.max_stack_percent_to_call and win >= self.min_equity_to_call:
            return {"call": amount}

        # Parfois, même s'il est légèrement en-dessous, il peut quand même caller (comportement de calling station)
        # Utilise numpy pour la RNG déjà présente dans le projet
        if win >= (self.min_equity_to_call * 0.7) and np.random.rand() < self.random_call_prob:
            return {"call": amount}

        return {"fold": True}
