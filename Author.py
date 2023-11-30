class Author:
    def __init__(self, name, ndoc, production):
        self.name = name
        self.ndoc = ndoc
        self.production = production

    def add(self, document):
        self.production.append(document)
        self.ndoc += 1

    def __str__(self) -> str:
        return ("Auteur : "+self.name+", Nombre de documents écrits : "+str(self.ndoc))