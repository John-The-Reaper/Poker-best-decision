def jeu():
    valeur = ["1","2","3","4","5","6","7","8","9","10","Valet","Dame","Roi"] # liste de 1 à 10 et des têtes
    couleur = ["Coeur","Careau","Trefle","Pique"]
    paquet=[]

    for posc in range(len(couleur)):
        for posv in range(len(valeur)):
            paquet.append([valeur[posv], couleur[posc]])

    print(paquet)

jeu()
