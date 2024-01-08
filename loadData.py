import datetime
import importlib
import urllib.request
import praw
import xmltodict
import pickle
import Corpus, Author, Document, DocumentGenerator

importlib.reload(Author)
importlib.reload(Corpus)
importlib.reload(Document)
importlib.reload(DocumentGenerator)
# # Reload the modules to ensure that the latest changes are used

# global variables
doc_repository = {}
author_repository = {}
doc_index = 1



reddit = praw.Reddit(client_id='tIn-EBuYy_lRYNLp6g_HVQ', client_secret='Y_77xj7yIgUY6ucEdIfzqjmYz_PxGw', user_agent='romain')
ml_posts = reddit.subreddit('MachineLearning').hot(limit=1000) # Retrieve hot posts from the ML subreddit

valid_docs_count = 0

for post in ml_posts:
    if valid_docs_count < 50:
        
        post_timestamp = datetime.datetime.utcfromtimestamp(post.created)
        post.selftext.replace("\r\n", " ")
        if len(post.selftext.strip()) > 60 and post.author:
            valid_docs_count += 1
            reddit_doc = DocumentGenerator.DocumentGenerator.factory(post.title, post.author.name, post_timestamp, post.url, post.selftext, "Reddit")

            doc_repository[doc_index] = reddit_doc
            doc_index += 1

            # Process comments
            comments = []
            post.comments.replace_more(limit=None)
            for comment in post.comments.list():
                comments.append(comment)
            reddit_doc.setNbComments(len(comments))

            # Process authors
            existing_author = author_repository.get(post.author.name)
            if existing_author:
                existing_author.add(reddit_doc)
            else:
                author = Author.Author(post.author.name, 0, [])
                author.add(reddit_doc)
                author_repository[post.author.name] = author
    else:
        break


query = "machinelearning"
arxiv_url = 'http://export.arxiv.org/api/query?search_query=all:'+ query +'&start=0&max_results='+str(valid_docs_count)
response = urllib.request.urlopen(arxiv_url)
xml_content = response.read().decode('utf-8')
parsed_xml = xmltodict.parse(xml_content)

for entry in parsed_xml['feed']['entry']:
    published_date = datetime.datetime.strptime(entry.get('published'), "%Y-%m-%dT%H:%M:%SZ")
    summary = entry.get('summary').replace("\r\n", " ")
    doc_link = entry.get('link')[0].get('@href')
    authors = entry.get('author')

    if isinstance(authors, dict):
        authors = [authors]

    author_names = [a.get('name') for a in authors]
    arxiv_doc = DocumentGenerator.DocumentGenerator.factory(entry.get('title'), author_names[0], published_date, doc_link, summary, "Arxiv")
    arxiv_doc.setCoauthors(author_names)
    doc_repository[doc_index] = arxiv_doc
    doc_index += 1

    for name in author_names:
        existing_author = author_repository.get(name)
        if existing_author: 
            existing_author.add(arxiv_doc)
        else:
            new_author = Author.Author(name, 0, [])
            new_author.add(arxiv_doc)
            author_repository[name] = new_author


# Save data



with open("./data/id2doc.pkl", "wb") as file:
    pickle.dump(doc_repository, file)

with open("./data/id2author.pkl", "wb") as file:
    pickle.dump(author_repository, file)

