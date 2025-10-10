from random import shuffle

class Deal:    
    def __init__(self):
        self.cards = self.cards_init()
        self.board = []
        self.colors = ['D', 'H', 'S', 'C']  # Diamond: carreau , Heart: coeur, Spade: pique, Club: trèfle
        self.values = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
    
    def cards_init(self):
        """
        Initialisation du paquet de carte 
        """
        self.cards = [(color, value) for color in colors for value in values]
        shuffle(self.cards)

    def distribuer(self):
        """
        Distribue les mains aléatoirement aux joueurs via les class et les retire du jeu
        -- # -- FONCTION A FAIRE UNE FOIS QUE LES CLASS JOUEURS SONT INITIALISES -- # -- 
        """
        pass

    def board(self, ):
        """
        Gère les différentes étapes de la partie qui concerne le board : flop, turn, river
        """
        pass
