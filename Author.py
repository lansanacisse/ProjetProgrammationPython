class Author:
    """_summary_ : classe représentant un auteur

    args:
        name (_string_): nom de l'auteur
        ndoc (_int_): nombre de documents publiés
        production (_string_): un dictionnaire des documents écrits par l’auteur
    """
    def __init__(self, name, ndoc, production):
        self.name = name
        self.ndoc = ndoc
        self.production = production

    def add(self, document):
        """_summary_ : ajoute un document à la production de l'auteur

        args:
            document (_string_): un document écrit par l’auteur
        """
        self.production.append(document)
        self.ndoc += 1

    def __str__(self) -> str:
        return ("Auteur : "+self.name+", Nombre de documents écrits : "+str(self.ndoc))