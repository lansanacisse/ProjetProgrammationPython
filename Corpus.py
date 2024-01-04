import pandas as pd
#import pickle
import numpy as np
import math
import re
import nltk, string

def singleton(cls):
    instances = [None]
    def wrapper(*args, **kwargs):
        if instances[0] is None:
            instances[0] = cls(*args, **kwargs)
        return instances[0]
    return wrapper

#@singleton
class Corpus:
    def __init__(self, nom, authors, id2doc):
        """_summary_

        Args:
            nom (_type_): _description_
            authors (_type_): _description_
            id2doc (_type_): _description_
        """
        self.nom = nom
        self.authors = authors
        self.id2doc = id2doc
        self.ndoc = len(self.id2doc)
        self.naut = len(self.authors)
        self._mots= list(self.occurence().keys())
        self.all = " ".join([doc.texte for doc in self.id2doc.values()])
        self.matdoc = self.matDocumentMot()

    def __repr__(self):
        return f'Corpus {self.nom} with {self.ndoc} documents by {self.naut} authors'
    
    def documentsSortedByDate(self, num_docs):
        sorted_data = self.data.sort_values(by='date').head(num_docs)
        print(sorted_data)
    
    def documentsSortedByAuthor(self, num_docs):
        sorted_data = self.data.sort_values(by='author').head(num_docs)
        print(sorted_data)
    
    # def save(self, filepath):
    #     with open(filepath, "wb") as f:
    #         pickle.dump(self, f)
        

    # def load(cls, filepath):
    #     with open(filepath, "rb") as f:
    #         return pickle.load(f)

    def save(self):
       
        dico={"documents": [], "auteurs": [] }
        for doc in self._id2doc.values():
            dico["documents"].append(doc)
            dico["auteurs"].append(self._authors[doc.getAuteur()])
        df = pd.DataFrame.from_dict(dico)
        df.to_csv("{}.csv".format(self._nom))
    
    def load(self, titre = "out.csv"):
        df = pd.read_csv(titre)
        self.setNom(titre[:-4])
        df["documents"].apply(self.addDocument)
        df["auteurs"].apply(self.addAuteur)

        
    
    def search(self, mot):
        """ Cette fonction retourne les passages des documents contenant le mot-clef entré en paramètre

        Args:
            mot (_string_): mot-clef à rechercher dans les documents

        Returns:
            _list_:  Passage des documents contenant le mot-clef entré en paramètre
        """

        res = []
        for i in re.compile(r'\b{}\b'.format(str(mot)), re.IGNORECASE).finditer(self.all):
            p = i.span()
            res.append(self.all[p[0]-20:p[1]+20])
        return res
    

    
    def concordance(self, mot):
        """ Cette fonction construit concordancier pour uneexpression donnée

        Args:
            mot (_string_): mot-clef à rechercher dans les documents

        Returns:
            _df_: Passage des documents contenant le mot-clef entré en paramètre avec le contexte gauche et droit
        """
        liste= self.search(mot)
        dic = {"contexte gauche":[], "motif trouvé":[], "contexte droit":[]}
        for el in liste:
            dic["contexte gauche"].append("..."+el[:20])
            dic["motif trouvé"].append(el[20:-20])
            dic["contexte droit"].append(el[-20:]+"...")
        df = pd.DataFrame.from_dict(dic)
        return df


    def vocabulary(self):
        """ retourne le vocabulaire de chaque document

        Returns:
            _dict_:  vocabulaire de chaque document 
        """
        voc = { k: list(set(self.nettoyer_texte(v.getText()).split())) for k,v in self.id2doc.items() }
        return voc
    
    def occurence(self):
        """ retourne l'occurence de chaque mot dans le corpus

        Returns:
            _dict_:  occurence de chaque mot dans le corpus
        """
        all = self.nettoyer_texte(self.all).split()
        voc = list(set(all))
        occ = { k: all.count(k) for k in voc }
        return occ
    
    # donne des stats à propos des docs :
    def stat(self):
        reddit = 0
        arxiv = 0
        mots, motsbis = 0, len(self.all)
        for i in range(self.ndoc):
            doc = self.id2doc[i]
            texte = doc.getText()
            if doc.getType() == "Reddit":
                reddit += 1
                mots += len(texte.split())
                arxiv -= 1
                motsbis -= len(texte.split())
        return f"\nLes documents de type reddit sont {reddit} et ont en moyenne {mots} mots " \
            +f"\nLes documents de type arxiv sont {arxiv} et ont en moyenne {motsbis} mots "

    
    #nettoyer un texte passé en paramètre
    def nettoyer_texte(self, texte):
        compiler= re.compile("[%s]"%re.escape(string.punctuation))
        #mettre tout sur la même ligne et mettre en minuscule
        texte= texte.lower().replace("\n", " ")
        #enlever les ponctuations su texte
        texte= compiler.sub(" ", texte)
        #retirer les espacements inutile
        texte.replace("\t", " ")
        token=[t for t in texte.split() if t.isalpha()]
        #raciniser les mots
        stemmer = nltk.stem.SnowballStemmer("english")
        token=[stemmer.stem(mot) for mot in token]
        texte=" ".join(token)
        return texte
    

    def score(self, mot):
        mot = self.nettoyer_texte(mot).split()
        q = np.array([self.all.count(m) for m in self._mots])
        if sum (q) == 0:
            return 0
        
        mat = self.matdoc
        res = mat @ q
        res = res / (len(mat[0]) * sum(q))
        arg = np.argsort(res)
        return arg[-3:]


    # TF-IDF method
    def tf(self, i, mot, voc):
        doc= voc[i]
        nb= doc.count(mot)
        total= len(doc)
        if total==0:
            return 0
        return nb/total
    
    def idf(self, mot, voc):
        D = len(voc)
        d = 0
        for document in voc.values():
            if document.count(mot) > 0:
                d += 1
        return math.log(D/d)
    
    def mat_TFIDF(self):
        voc=self.vocabulary()
        n = self.ndoc
        mots = self._mots
        mat = np.zeros((n, len(mots)))
        for i in range(n):
            for j, c in enumerate(mots):
                mat[i][j] = self.tf(i, c, voc)*self.idf(c, voc)
        return mat
    

    def matDocumentMot(self):
        mots = self._mots
        voc = self.vocabulary()
        mat = np.zeros((len(self.id2doc), len(mots)))
        for l in range(len(self.id2doc)):
            document = voc[l]
            for c, mot in enumerate(mots):
                mat[l][c] = document.count(mot)
        return mat
    

    def occurenceMot(self):
        mat = self.matdoc
        result = []
        for i in range(len(mat)):
            nbDocu = 0
            nbTotal = 0
            mot = self._mots[i]
            for x in mat[:, i]:
                if x != 0:
                    nbDocu += 1
                nbTotal += x
            result.append((mot, nbDocu, nbTotal))
        return result
    

    