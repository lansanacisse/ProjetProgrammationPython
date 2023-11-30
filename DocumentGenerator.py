from Document import RedditDocument, ArxivDocument

class DocumentGenerator:

    #    Classe permettant de créer des instances de documents (Pattern Factory)

    @staticmethod
    def factory(titre, auteur, date, url, texte, type):
        if type == "Reddit":
            return RedditDocument(titre, auteur, date, url, texte)
        if type == "Arxiv":
            return ArxivDocument(titre, auteur, date, url, texte)
        assert 0, "Bad document creation: " + type