import pandas as pd
import pickle

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
        self.nom = nom
        self.authors = authors
        self.id2doc = id2doc
        self.ndoc = len(self.id2doc)
        self.naut = len(self.authors)
        self.data = pd.DataFrame(columns=['doc_id', 'title', 'author', 'date'])
    
    def __repr__(self):
        return f'Corpus {self.nom} with {self.ndoc} documents by {self.naut} authors'
    
    def documentsSortedByDate(self, num_docs):
        sorted_data = self.data.sort_values(by='date').head(num_docs)
        print(sorted_data)
    
    def documentsSortedByAuthor(self, num_docs):
        sorted_data = self.data.sort_values(by='author').head(num_docs)
        print(sorted_data)
    
    def save(self, filepath):
        with open(filepath, "wb") as f:
            pickle.dump(self, f)
        

    def load(cls, filepath):
        with open(filepath, "rb") as f:
            return pickle.load(f)


    