import pandas as pd
import numpy as np
import math
import re
import nltk
from nltk.corpus import stopwords
import string

# def singleton(cls):
#     instances = [None]
#     def wrapper(*args, **kwargs):
#         if instances[0] is None:
#             instances[0] = cls(*args, **kwargs)
#         return instances[0]
#     return wrapper

# @singleton
class Corpus:
    def __init__(self, nom, authors, id2doc):
        """
        @brief : Constructeur de la classe Corpus
        @param nom : nom du corpus
        @param authors : un dictionnaire des auteurs du corpus
        @param id2doc : un dictionnaire des documents du corpus
        """
        self.nom = nom
        self.authors = authors
        self.id2doc = id2doc
        self.ndoc = len(self.id2doc)
        self.naut = len(self.authors)

        self.voc = {}
        self.all = " ".join([i.getTexte().replace("\n", " ") for i in self.id2doc.values()])

        self.voc = self.vocab()
        self.dfTF = pd.DataFrame()
        self.dfTFIDF = pd.DataFrame()

    def __repr__(self):
        """
        @brief : Représentation de la classe Corpus
        """
        return f'Corpus {self.nom} with {self.ndoc} documents by {self.naut} authors'
    
    def getdfTfIdf(self):
        return self.dfTFIDF
    
    def getdfTf(self):
        return self.dfTF
    
    def getNom(self):
        return self.nom
    
    def getAuthors(self):
        return self.authors
    
    def getId2doc(self):
        return self.id2doc
    
    def getVoc(self):
        return self.voc
    
    def getNaut(self):
        return self.naut
    
    def getNdoc(self):
        return self.ndoc


    def save(self):
        """
        @brief : Sauvegarde le corpus dans un fichier csv
        """
        dico={"documents": [], "auteurs": [] }
        for doc in self.id2doc.values():
            dico["documents"].append(doc)
            dico["auteurs"].append(self.authors[doc.getAuteur()])
        df = pd.DataFrame.from_dict(dico)
        df.to_csv("{}.csv".format(self.nom))
    
    def load(self, titre = "out.csv"):
        """
        @brief : Charge le corpus depuis un fichier csv
        @param titre : titre du fichier csv
        """
        df = pd.read_csv(titre)
        self.setNom(titre[:-4])
        df["documents"].apply(self.addDocument)
        df["auteurs"].apply(self.addAuteur)

        
    
    def search(self, mot):
        """ 
        @brief : Recherche les passages contenant le mot-clef entré en paramètre
        @param mot : mot-clef à rechercher dans les documents
        @return : liste des passages contenant le mot-clef entré en paramètre
        """
        
        res = []
        for i in re.compile(r'\b{}\b'.format(str(mot)), re.IGNORECASE).finditer(self.all):
            p = i.span()
            res.append(self.all[p[0]-20:p[1]+20])
        return res
    
    def recherche(self, mot):
        """
        @brief : Recherche les passages contenant le mot-clef entré en paramètre
        @param mot : mot-clef à rechercher dans les documents
        @return : liste des passages contenant le mot-clef entré en paramètre
        """
        passages = []
        texte = self.all.split(". ")
        for i in texte:
            if re.search(mot, i):
                passages.append(i)
        return passages


    
    def concordance(self, mot):
        """ 
        @brief : Recherche les passages contenant le mot-clef entré en paramètre
        @param mot : mot-clef à rechercher dans les documents
        @return : dataframe des passages contenant le mot-clef entré en paramètre
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
        """
        @brief : Retourne le vocabulaire du corpus
        """
        voc = { k: list(set(self.nettoyer_texte(v.getTexte()).split())) for k,v in self.id2doc.items() }
        return voc
    
    def vocab(self):
        """
        @brief : Retourne le vocabulaire du corpus
        """
        mots = re.split(r"\s+", self.clean_text(self.all))
        res = {}
        i=0
        for value in sorted(set(mots)):
            if value!="":
                res[value] = {"id": i, "term-frequency":0, "document-frequency":0}
                i+=1
        return res
    
    def occurence(self):
        """
        @brief : Retourne les occurences des mots du corpus
        """
        tout = self.nettoyer_texte(self.all).split()
        voc = list(set(tout))
        occ = { k: tout.count(k) for k in voc }
        return occ
    
    # donne des stats à propos des docs :
    def stat(self):
        """
        @brief : Calcul les statistiques du Corpus
        @return: statistiques du Corpus sous forme de chaine de caractères
        """
        reddit = 0
        arxiv = 0
        mots, motsbis = 0, len(self.all)
        for doc in self.id2doc.values():
            texte = doc.getTexte()
            if doc.getType() == "Reddit":
                reddit += 1
                mots += len(texte.split())
                arxiv += 1
                motsbis += len(texte.split())
        return f"Les documents Reddit sont {reddit} et ont en moyenne {mots} mots. " \
            +f"Les documents ArXiv sont {arxiv} et ont en moyenne {motsbis} mots. "

    
    #nettoyer un texte passé en paramètre
    def nettoyer_texte(self, texte):
        """
        @param texte: texte à nettoyer
        @brief : Nettoie le texte passé en paramètre
        """
        # enlever les ponctuations
        compiler = re.compile("[%s]"%re.escape(string.punctuation))
        #mettre tout sur la même ligne et mettre en minuscule
        texte = texte.lower().replace("\n", " ")
        #enlever les ponctuations su texte
        texte = compiler.sub(" ", texte)
        #retirer les espacements inutile
        texte.replace("\t", " ")
        token = [t for t in texte.split() if t.isalpha()]
        #raciniser les mots
        stemmer = nltk.stem.SnowballStemmer("english")
        token = [stemmer.stem(mot) for mot in token]
        texte = " ".join(token)
        return texte
    

    def score(self, mot):
        """
        @param mot: mot clé
        @brief : Calcul le score du mot clé par rapport aux Documents du Corpus
        """
        mot = self.nettoyer_texte(mot).split()
        q = np.array([self.all.count(m) for m in self._mots])
        if sum (q) == 0:
            return 0
        
        mat = self.matdoc
        res = mat @ q
        res = res / (len(mat[0]) * sum(q))
        arg = np.argsort(res)
        return arg[-3:]

    def matrice(self):
        """
        @brief : Calcul la matrice tf-idf
        """
        mat_TF = {}
        valeurs = self.id2doc.values()

        for doc in valeurs:
            mat_TF[doc.getTitre()] = {}

            docText = doc.getTexte()
            chaineCleaned = self.clean_text(docText)
            splitedWords = re.split('\s+', chaineCleaned) # split la liste avec espaces

            deja_vu = []

            for word in self.voc.keys(): # initialisation
                mat_TF[doc.getTitre()][word] = 0

            for word in splitedWords:
                mat_TF[doc.getTitre()][word] = 0 
                if word in self.voc.keys(): # il est dans le vocabulaire
                    self.voc[word]['term-frequency'] += 1
                    if word not in deja_vu: # première fois que l'on tombe dessus dans le document
                        nbOccurence = splitedWords.count(word) # on compte directement tout les mêmes mots d'un texte
                        mat_TF[doc.getTitre()][word] = nbOccurence
                        deja_vu.append(word)
                        self.voc[word]['document-frequency'] += 1

        
        tf_idf = {}

        # calcul de la fréquence de chaque mot dans chaque document
        for doc in valeurs:
            chaineCleaned = self.clean_text(doc.getTexte())
            splitedWords = chaineCleaned.split() # split la liste avec espaces
            for word in splitedWords:
                if word in tf_idf:
                    tf_idf[word]['doc_count'] += 1
                else:
                    tf_idf[word] = {'doc_count': 1}

        # calcul de la fréquence de chaque mot dans tous les documents
        for word, scores in tf_idf.items():
            # tout les mots qui ne sont pas dans le
            # mettre à 0 les mots qui manquent au vocabulaire
            
            total_count = 0
            for doc in valeurs:
                texte_doc = doc.getTexte()
                if word in texte_doc:
                    total_count += 1
            # Assignation de la valeur calculée au dictionnaire tf_idf pour le mot spécifique
            tf_idf[word]['total_count'] = total_count

        # dictionnaire qui contiendra les mots et leur score idf
        idf_scores = {}

        # calcul du score idf pour chaque mot
        for word, scores in tf_idf.items():
            #print(scores['total_count'])
            if scores['total_count'] == 0:
                idf_scores[word] = 0
            else:
                idf_scores[word] = math.log(len(self.id2doc) / scores['total_count'])

        # création de la matrice tf-idf
        mat_TFIDF = {}
        for doc in self.id2doc.values():
            mat_TFIDF[doc.getTitre()] = {}
            chaineCleaned = self.clean_text(doc.getTexte())
            splitedWords = chaineCleaned.split() # split la liste avec espaces
            for word in self.voc.keys(): # initialisation
                mat_TFIDF[doc.getTitre()][word] = 0
            for word in splitedWords:
                tf = tf_idf[word]['doc_count'] / len(splitedWords)
                idf = idf_scores[word]
                mat_TFIDF[doc.getTitre()][word] = tf * idf

        self.dfTF = pd.DataFrame(mat_TF) 
        self.dfTFIDF = pd.DataFrame(mat_TFIDF) 



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
    

    def searchCosine(self, keywords):
        """
        @brief : Recherche les documents les plus similaires aux mots clés
        @param keywords: liste de mots clés
        @return: dictionnaire des documents triés par similarité décroissante
        """
        # Création du vecteur pour les mots-clés
        # 1 si le mot est dans les mots-clés, 0 sinon
        vecteur_mots_cles = np.array([1 if mot in keywords else 0 for mot in self.voc])

        # Génération des vecteurs pour chaque document
        vecteurs_documents = {}
        for document in self.id2doc.values():
            titre_doc = document.getTitre()
            texte_nettoye = self.clean_text(document.getTexte())
            mots_document = texte_nettoye.split()

            # Création du vecteur binaire pour le document
            vecteur_doc = [1 if mot in mots_document else 0 for mot in self.voc]
            vecteurs_documents[titre_doc] = vecteur_doc

        # Calcul de la similarité cosinus
        resultats_similarite = {}
        for titre, vecteur in vecteurs_documents.items():
            norme_vecteur_mot_cles = np.linalg.norm(vecteur_mots_cles)
            norme_vecteur_doc = np.linalg.norm(vecteur)

            if norme_vecteur_mot_cles * norme_vecteur_doc == 0:
                similarite_cosinus = 0
            else:
                similarite_cosinus = (vecteur_mots_cles @ np.array(vecteur)) / (norme_vecteur_mot_cles * norme_vecteur_doc)
            resultats_similarite[titre] = similarite_cosinus

        # Tri des résultats par similarité décroissante
        documents_tries_par_similarite = dict(sorted(resultats_similarite.items(), key=lambda x: x[1], reverse=True))

        return documents_tries_par_similarite


    
    def clean_text(self, text):
        """
        @brief : Nettoie le texte passé en paramètre
        @param text: texte à nettoyer
        @return: texte nettoyé
        """
        # Remove URLs from the text
        text_no_urls = re.sub(r'https?://\S+|www\.\S+', '', text)
        # Tokenize the text into words
        word_list = nltk.tokenize.word_tokenize(text_no_urls)
        # Convert all words to lower case
        lower_case_words = [word.lower() for word in word_list]
        # Compile a regular expression for punctuation
        punctuation_regex = re.compile('[%s]' % re.escape(string.punctuation))
        # Remove punctuation from each word
        words_no_punct = [punctuation_regex.sub('', word) for word in lower_case_words]
        # Remove non-alphabetic tokens
        alphabetic_words = [word for word in words_no_punct if word.isalpha()]
        # Remove stopwords
        english_stop_words = set(stopwords.words('english'))
        words_no_stop = [word for word in alphabetic_words if word not in english_stop_words]
        # Filter out single character tokens
        filtered_words = [word for word in words_no_stop if len(word) > 1]
        # Rejoin words into a cleaned text
        cleaned_text = ' '.join(filtered_words)
        return cleaned_text
        

    # matrice Document-Mot
    def matDocumentMot(self):
        mots = self._mots
        voc = self.vocabulary()
        mat = np.zeros((len(self.id2doc), len(mots)))
        for l in range(len(self.id2doc)):
            document = voc[l]
            for c, mot in enumerate(mots):
                mat[l][c] = document.count(mot)
        return mat
    

    
    def get_id2doc_DF(self):
        """
        @brief : Retourne le dictionnaire id2doc
        @return: dataframe contenant les attributs des documents du corpus
        """

        df = pd.DataFrame(columns=['Id','Nom','Auteur','Date','dateFr','URL','Text','Textabrv','Type'])
        i=1
        for doc in self.id2doc.values():
            row = [i,doc.getTitre(),doc.getAuteur(),doc.getDate().date(),doc.getDate().strftime("%d/%m/%y"),doc.getUrl(), doc.getTexte(), doc.getTexte()[:10]+'...',doc.getType()]
            df.loc[len(df)] = row
            i+=1
        return df
    

    