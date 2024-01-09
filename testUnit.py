import unittest
from Document import *
from Author import Author
from Corpus import Corpus


class TestDocument(unittest.TestCase):

    def setUp(self):
        self.doc = Document("Titre", "Auteur", "01/01/2020", "http://example.com", "Texte du document")

    def test_constructor(self):
        self.assertEqual(self.doc.titre, "Titre")
        self.assertEqual(self.doc.auteur, "Auteur")
        self.assertEqual(self.doc.date, "01/01/2020")
        self.assertEqual(self.doc.url, "http://example.com")
        self.assertEqual(self.doc.texte, "Texte du document")

    def test_affichage(self):
        expected_output = "Titre: Titre\nAuteur: Auteur\nDate: 01/01/2020\nUrl: http://example.com\nTexte: Texte du document"
        self.assertEqual(self.doc.affichage(), expected_output)

    def test_str(self):
        self.assertEqual(str(self.doc), "Titre du document : Titre")

    def test_getters(self):
        self.assertEqual(self.doc.getTitre(), "Titre")
        self.assertEqual(self.doc.getAuteur(), "Auteur")


class TestRedditDocument(unittest.TestCase):
    
    def setUp(self):
        self.reddit_doc = RedditDocument("Titre Reddit", "Auteur Reddit", "02/02/2020", "http://reddit.com/example", "Texte du document Reddit")

    def test_constructor(self):
        self.assertIsInstance(self.reddit_doc, Document)
        self.assertEqual(self.reddit_doc.titre, "Titre Reddit")
        self.assertEqual(self.reddit_doc.auteur, "Auteur Reddit")
        self.assertEqual(self.reddit_doc.date, "02/02/2020")
        self.assertEqual(self.reddit_doc.url, "http://reddit.com/example")
        self.assertEqual(self.reddit_doc.texte, "Texte du document Reddit")
        self.assertEqual(self.reddit_doc.nbComment, 0)

    def test_getType(self):
        self.assertEqual(self.reddit_doc.getType(), "Reddit")

    def test_setNbComments(self):
        self.reddit_doc.setNbComments(10)
        self.assertEqual(self.reddit_doc.nbComment, 10)

    def test_str(self):
        self.assertEqual(str(self.reddit_doc), "Titre du document Reddit : Titre Reddit")

class TestArxivDocument(unittest.TestCase):
    
    def setUp(self):
        self.arxiv_doc = ArxivDocument("Titre Arxiv", "Auteur Arxiv", "03/03/2020", "http://arxiv.org/example", "Texte du document Arxiv")

    def test_constructor(self):
        self.assertIsInstance(self.arxiv_doc, Document)
        self.assertEqual(self.arxiv_doc.titre, "Titre Arxiv")
        self.assertEqual(self.arxiv_doc.auteur, "Auteur Arxiv")
        self.assertEqual(self.arxiv_doc.date, "03/03/2020")
        self.assertEqual(self.arxiv_doc.url, "http://arxiv.org/example")
        self.assertEqual(self.arxiv_doc.texte, "Texte du document Arxiv")
        self.assertEqual(self.arxiv_doc.coauthors, [])

    def test_getType(self):
        self.assertEqual(self.arxiv_doc.getType(), "Arxiv")

    def test_setCoauthors(self):
        coauthors = ["Coauteur 1", "Coauteur 2"]
        self.arxiv_doc.setCoauthors(coauthors)
        self.assertEqual(self.arxiv_doc.coauthors, coauthors)

    def test_str(self):
        self.assertEqual(str(self.arxiv_doc), "Titre du document Arxiv : Titre Arxiv")





class TestAuthor(unittest.TestCase):

    def setUp(self):
        self.author = Author("Nom", 0, [])

    def test_add_document(self):
        doc = Document("Titre", "Auteur", "01/01/2020", "http://example.com", "Texte du document")
        self.author.add(doc)
        self.assertEqual(self.author.ndoc, 1)
        self.assertIn(doc, self.author.production)

    def test_str(self):
        self.assertEqual(str(self.author), "Auteur : Nom, Nombre de documents écrits : 0")

class TestCorpus(unittest.TestCase):

    def setUp(self):
        # Création d'auteurs et de documents de test
        self.author1 = Author("Auteur 1", 0, [])
        self.author2 = Author("Auteur 2", 0, [])
        self.doc1 = Document("Titre 1", "Auteur 1", "04/04/2020", "http://example1.com", "Texte du document 1")
        self.doc2 = Document("Titre 2", "Auteur 2", "05/05/2020", "http://example2.com", "Texte du document 2")

        # Ajout des documents à la production des auteurs
        self.author1.add(self.doc1)
        self.author2.add(self.doc2)

        # Création d'un Corpus de test
        authors = {"Auteur 1": self.author1, "Auteur 2": self.author2}
        id2doc = {1: self.doc1, 2: self.doc2}
        self.corpus = Corpus("TestCorpus", authors, id2doc)

    def test_constructor(self):
        self.assertEqual(self.corpus.nom, "TestCorpus")
        self.assertEqual(self.corpus.ndoc, 2)
        self.assertEqual(self.corpus.naut, 2)

    def test_getters(self):
        self.assertEqual(self.corpus.getNom(), "TestCorpus")
        self.assertEqual(self.corpus.getNdoc(), 2)
        self.assertEqual(self.corpus.getNaut(), 2)
        self.assertEqual(self.corpus.getAuthors(), {"Auteur 1": self.author1, "Auteur 2": self.author2})
        self.assertEqual(self.corpus.getId2doc(), {1: self.doc1, 2: self.doc2})



if __name__ == '__main__':
    unittest.main()