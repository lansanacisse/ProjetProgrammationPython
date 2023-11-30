import praw
#import pandas as pd
import datetime
from Document import *
from Author import *
from Corpus import *
import numpy as np
import urllib.request
import xmltodict
#import pickle


def showDictStruct(dict):
    def showDictStructRec(dict, indent):
        for key in dict:
            if type(dict[key]) == dict:
                print("-"*indent , key)
                showDictStructRec(dict[key], indent+2)
            else:
                print("-"*indent , key, ":", dict[key])
        showDictStructRec(dict, 1)


id2Doc = {}
id2Aut = {}
indice = 0

reddit = praw.Reddit(client_id='tIn-EBuYy_lRYNLp6g_HVQ', client_secret='Y_77xj7yIgUY6ucEdIfzqjmYz_PxGw', user_agent='romain')
subr = reddit.subreddit('MachineLearning')
textes_Reddit = []
#Parours 30 posts Reddit
for post in subr.hot(limit=30):
    texte = post.title
    texte = texte.replace("\n", " ")
    textes_Reddit.append(texte)
    #création des instances
    dReddit = RedditDocument(post.title, post.author, datetime.datetime.fromtimestamp(post.created), post.url, post.selftext)
    id2Doc[indice] = dReddit
    nom = post.author
    if nom in id2Aut:
        id2Aut[nom].add(dReddit)
    else:
        id2Aut[nom] = Author(nom, 1, [dReddit])

    indice += 1




textes_Arxiv = []
query = "machinelearning"
url = 'http://export.arxiv.org/api/query?search_query=all:' + query + '&start=0&max_results=100'
url_read = urllib.request.urlopen(url).read()
data = url_read.decode()
#Transformation en un objet json
dico = xmltodict.parse(data)
docs = dico['feed']['entry']
for d in docs:
    texte = d['title'] + ". " + d['summary']
    texte = texte.replace("\n", " ")
    textes_Arxiv.append(texte)
    #création des instances
    dArxiv = ArxivDocument(d["title"], d["author"], datetime.datetime.strptime(d["published"], "%Y-%m-%dT%H:%M:%SZ"), d.get('@href'), d["summary"])
    id2Doc[indice] = dArxiv
    authors= d["author"]
    try:
        auth = ", ".join([a["name"] for a in authors])  # On fait une liste d'auteurs, séparés par une virgule
    except:
        auth = authors["name"] 
    auteur= Author(auth, 1, {0:dArxiv})
    if auth not in id2Doc.keys():
        id2Aut[auth]=auteur
    else:
        id2Aut[auth].add(dArxiv)
    indice += 1

# corpus = textes_Reddit + textes_Arxiv

#creer une instance Corpus
corpus = Corpus("ML-corpus", id2Doc, id2Aut)


# #Longueur du corpus
# print("Longueur du corpus : " + str(len(corpus)))

# for doc in corpus:
#     # nombre de phrases
#     print("Nombre de phrases : " + str(len(doc.split("."))))
#     print("Nombre de mots : " + str(len(doc.split(" "))))


# #Nombre de phrases dans le corpus
# nb_phrases = [len(doc.split(".")) for doc in corpus]
# print("Moyenne du nombre de phrases : " + str(np.mean(nb_phrases)))
# #Nombre de mots dans le corpus et moyenne de mots
# nb_mots = [len(doc.split(" ")) for doc in corpus]
# print("Moyenne du nombre de mots : " + str(np.mean(nb_mots)))
# print("Nombre total de mots dans le corpus : " + str(np.sum(nb_mots)))


# corpus_plus100 = [doc for doc in corpus if len(doc)>100]

# chaine_unique = " ".join(corpus_plus100)
# print(f"Longueur chaine corpus { len(chaine_unique)}")



corpus.save("doc.pkl")
    
# deserialization
corpus_deserialized = corpus.load("doc.pkl")

print(corpus_deserialized)

# print(corpus_deserialized.documentsSortedByDate(corpus_deserialized.ndoc))

# print(corpus_deserialized.documentsSortedByAuthor(corpus_deserialized.naut))
