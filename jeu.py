from random import shuffle

class Deal:
    valeurs = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Valet", "Dame", "Roi"]
    couleurs = ["Coeur", "Careau", "Trefle", "Pique"]

    def __init__(self):
        self.paquet = self.creer_paquet()

    def creer_paquet(cls):
        paquet = []
        for couleur in cls.couleurs:
            for valeur in cls.valeurs:
                paquet.append([valeur, couleur])
        return paquet
    

    def melanger(self):
        from random import shuffle
        shuffle(self.paquet)



    def distribuer(self, n):
        pass

    def gestion_cards_on_board(self):
        pass


    def 






