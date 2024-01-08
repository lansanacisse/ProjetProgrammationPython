from Document import RedditDocument, ArxivDocument

class DocumentGenerator:

    """
    @brief Classe permettant de créer des instances de documents (Pattern Factory)
    @return Une instance de document, selon le type passé en paramètre
    """

    @staticmethod
    def factory(titre, auteur, date, url, texte, type):
        """
        @brief Méthode permettant de créer une instance de document
        @param titre Titre du document
        @param auteur Auteur du document
        @param date Date de publication du document
        @param url URL du document
        @param texte Contenu du document
        """
        if type == "Reddit":
            return RedditDocument(titre, auteur, date, url, texte)
        if type == "Arxiv":
            return ArxivDocument(titre, auteur, date, url, texte)
        assert 0, "Bad document creation: " + type