from deal import Deal

class Player():
    def __init__(self, name, stack, position):
        self.name = name
        self.stack = stack
        self.position = position

        dealer = Deal()
        self.hand = dealer.deal_player_hand()

    def make_decision(self, game):
        """
        Prend en paramètre les données de la partie pour pouvoir prendre une décision
        Renvoie l'action : call, raise, fold, all-in, check sous cette forme :
        return {"action": "fold", "amount": None}
        """
        pass
    
    def update_stack(self, amount):
        """
        Met à jour le stack du joueur en fonction de l'action prise
        """
        self.stack += amount
