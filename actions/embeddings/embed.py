import os
import json
from amcat4py import AmcatClient
import spacy

amcat4_host = os.environ.get("amcat4_host")
index = os.environ.get("index")
text_field = os.environ.get("text_field")
vector_field = os.environ.get("vector_field")
spacy_model = os.environ.get("spacy_model")
queries = os.environ.get("queries")
filters = os.environ.get("filters")
if filters:
    filters = json.loads(filters)


# log in
amcat = AmcatClient(amcat4_host)

# retrieve text data
text_data = list(amcat.query(index, fields=["_id", text_field], queries=queries, filters=filters))
print(f"{len(text_data)} texts to process...")

# Load the spacy model
# Load the spacy model
try:
  nlp = spacy.load(spacy_model)
except:
  spacy.cli.download(spacy_model)
  nlp = spacy.load(spacy_model)

# embed texts (this uses the mean of word embeddings of each text as 
# word vectors could be used to reproduce the original text)
for item in text_data:
    id = item["_id"]
    print(f"\t...processing _id: {id}")
    item[vector_field] = nlp(item[text_field]).vector.tolist()
    del item["_id"]
    del item[text_field]
    amcat.update_document(index, doc_id = id, body = item) 

##  guests can now query the embedding vectors with e.g.:
# text_data_vec = list(amcat.query("state_of_the_union", fields=["_id", "vector"]))
# text_data_vec[0]
