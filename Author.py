class Author:
    """
    @class classe représentant un auteur
    """
    def __init__(self, name, ndoc, production):
        """
        @brief Constructeur de la classe Author
        @param name : nom de l'auteur
        @param ndoc : nombre de documents publiés
        @param production : un dictionnaire des documents écrits par l’auteur
        """
        self.name = name
        self.ndoc = ndoc
        self.production = production

    def add(self, document):
        """
        @brief Méthode permettant d'ajouter un document à la production de l'auteur
        @param
            document : un document écrit par l’auteur
        """
        self.production.append(document)
        self.ndoc += 1

    def __str__(self) -> str:
        return ("Auteur : "+self.name+", Nombre de documents écrits : "+str(self.ndoc))