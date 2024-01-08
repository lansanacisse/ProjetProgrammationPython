class Document:
    def __init__(self, titre, auteur, date, url, texte):
        """
        @param titre: titre du document
        @param auteur: auteur du document
        @param date: date de publication du document
        @param url: url du document
        @param texte: texte du document
        """
        self.titre = titre
        self.auteur = auteur
        self.date = date
        self.url = url
        self.texte = texte

    def affichage(self):
        return "Titre: " + self.titre + "\nAuteur: " + self.auteur + "\nDate: " + self.date + "\nUrl: " + self.url + "\nTexte: " + self.texte
    
    def __str__(self) -> str:
        return ("Titre du document : "+self.titre)
    
    def getType(self):
        pass

    # guetters 
    def getTitre(self):
        return self.titre
    
    def getAuteur(self):
        return self.auteur
    
    def getDate(self):
        return self.date
    
    def getUrl(self):
        return self.url
    
    def getTexte(self):
        return self.texte
    
    

class RedditDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, type="Reddit"):
        """
        @param titre: titre du document
        @param auteur: auteur du document
        @param date: date de publication du document
        @param url: url du document
        @param texte: texte du document
        @param type: type du document
        """
        super().__init__(titre, auteur, date, url, texte)
        self.type = type
        self.nbComment = 0 #nombre de commentaires

    def getType(self):
        return self.type

    def setNbComments(self, nbComment):
        self.nbComment = nbComment
    
    def __str__(self) -> str:
        return ("Titre du document Reddit : "+self.titre)

class ArxivDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, type="Arxiv"):
        """
        @param titre: titre du document
        @param auteur: auteur du document
        @param date: date de publication du document
        @param url: url du document
        @param texte: texte du document
        @param type: type du document
        """
        super().__init__(titre, auteur, date, url, texte)
        self.type = type
        self.coauthors = []  #liste des coauteurs

    def getType(self):
        return self.type

    def setCoauthors(self, coauthors):
        self.coauthors = coauthors
    
    def __str__(self) -> str:
        return ("Titre du document Arxiv : "+self.titre)
