class Stat:
    def __init__(self,players,board,main_character,pot,ranges,amount_to_call = 0,stage = 0,opponent_stats = None):
        """
        arg: player --> liste les stack des adversaires + position provient de la classe player
        arg: board --> Liste de carte du board sous forme de liste ex ([("♥️", "A")])
        arg: main_character --> joueur avec lequel on joue (objet)
        arg: pot --> utiliser dans la class dealer 
        arg: ranges --> dico listant les cartes probable utiliser par l'adversaire dans cette main ex: {player: [(main, proba),..]}
        arg: amount_to_call --> montant à payer pour suivre
        arg: stage -->  moment de la partie: flopp,river ect avec des int
        arg: opponent_stats --> dico pour chaque joueur calculer le rapport d'agressivité/passivité de chaque personne (VPIP,PFR,AF,voir maths doc) 
        """
    
        self.players = players
        self.board = board
        self.main_character = main_character
        self.pot = pot
        self.ranges = ranges
        self.amount_to_call = amount_to_call
        self.stage = stage
        self.opponent_stats = opponent_stats

    def pot_odds(self): # voir sur test si il y a des conditions
        """
        équité minimale nécessaire pour que le call soit rentable (en %) en fonction de la mise à payer et de la valeur du pot
        Note: Par la suite on saura s'il faut jouer le coup ou nn dans la fonction equity
        """
        return self.amount_to_call / (self.pot + self.amount_to_call)

    def EV_call(self,equity):
        """
        calcul la valeur de rentabilité en jeton qu'un call pourrait t'apporter sur le long terme 
        donc si positif alors à long terme on est positif en jeton 
        """
        
        return equity * (self.pot + self.amount_to_call) - (1 - equity) * self.amount_to_call
    
    def EV_raise(self):
        pass

    def EV_fold(self):
        pass
        

    def MDF(self):
        pass

    def Monte_Carlo(self):
        pass

    def equity(self):
        pass

    def outs(self):
        pass

    
        


class PokerIA:
    def __init__(self):
        pass

    def decide(self):
        """
        fonction qui utilise la classe stat pour prendre des décisions et renvoie ce qu'il faut faire (fold,raise,call) 
        """
        pass

