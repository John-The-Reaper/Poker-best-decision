from random import shuffle

class Deal:    
    def __init__(self):

        self.colors = ['D', 'H', 'S', 'C']  # Diamond: carreau , Heart: coeur, Spade: pique, Club: trèfle
        self.values = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        self.cards = self.cards_init()
        self.board = []
        self.state = 0
    
    def cards_init(self):
        """
        Initialisation du paquet de carte 
        """
        self.cards = [(color, value) for color in self.colors for value in self.values]
        shuffle(self.cards)
        return self.cards

    def deal_player_hand(self):
        """
        Distribue une main aléatoirement à un joueur et retire les cartes du jeu
        """
        main = [self.cards.pop() for _ in range(2)]
        return [main]

    def deal_board(self):
        """
        Gère les différentes étapes de la partie qui concerne le board : 1 : flop, 2 : turn, 3 :river
        Renvoie le board complet 
        """
        self.state += 1
        if self.state == 1:
            # Flop
            self.board = [self.cards.pop() for _ in range(3)]
            return self.board
        elif self.state == 2:
            # Après le flop on return forcément qu'une carte
            self.board.append(self.cards.pop())
            return [self.board]
        
        assert self.board < 4
