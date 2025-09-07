"""

-- Jeu


2
3
4
5
6
7
8
9
T
J
Q
K
A

Heart
Diamond
Club
Spade

-- Actions

Fold
Check
Call
Raise
All-in

"""

class poker:
    def __init__(self, hand, river):
        self.hand = hand # main du joueur
        self.river = river # Cartes retournée, change le nom de la variable aussi

    def card_reveal(self, value, tyoe):
        # Modifie le nom des arguments
        # Le but de cette fonction est de révéler la carte et de l'ajuter à la main
        pass
    
    def hand_rank(self):
        # Renvoie la main la plus forte (possédée par le joueur)
        pass

    def probability(self):
        # Calcule la probabilité de gagner en fonction de la main et des cartes révélées
        # Renvoie un pourcentage (Sous forme de float)
        pass
    
    def recommendedation(self):
        # Donne une recommandation d'action en fonction de la main, de la rivière et de la probabilité
        """
        Fold
        Check
        Call
        Raise
        All-in
        """
        pass

1 = poker({'k':'H', '8':'S'}, {'2':'D', '3':'H', '4':'C', '5':'S', '6':'H'})