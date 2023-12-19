import os
import json
from amcat4py import AmcatClient
import spacy
# for testing
#from dotenv import load_dotenv
#load_dotenv()


amcat4_host = os.environ.get("amcat4_host")
index = os.environ.get("index")
text_field = os.environ.get("text_field")
entities_field = os.environ.get("entities")
spacy_model = os.environ.get("spacy_model")
queries = os.environ.get("queries")
filters = os.environ.get("filters")
batch_size = os.environ.get("batch_size")
if filters:
    filters = json.loads(filters)

if queries:
  queries = queries + f"AND NOT(_exists_:{entities_field})"
else:
  queries = f"NOT(_exists_:{entities_field})"

# log in
amcat = AmcatClient(amcat4_host)

# set field if it does not exist (does nothing if entities_field exists already)
# the reason for choosing text type: 
# https://stackoverflow.com/a/62358568/5028841
amcat.set_fields(index=index, body={entities_field: "text"}) 
print(f"Starting to process texts...")

# iterate over empty entities fields until none are left
while True:
  # retrieve text data
  body = dict(filters=filters, 
               queries=queries, 
               fields=["_id", text_field],
               page=0, 
               per_page=batch_size)
  res = amcat._post("query", index=index, json=body, ignore_status=[404]).json()  
  
  if len(res['results']) == 0:
    print("No more texts to process...")
    break
  else:
    remaining = res["meta"]["total_count"] - len(res['results'])
    text_data = res['results']
    print(f"\t...retrieved {len(text_data)} texts to process. {remaining} left to do afterwards")
  
  # Load the spacy model
  try:
    nlp = spacy.load(spacy_model)
  except:
    spacy.cli.download(spacy_model)
    nlp = spacy.load(spacy_model)
  
  # do named entity recognition on all texts
  for item in text_data:
      id = item["_id"]
      print(f"\t...processing _id: {id}")
      doc = nlp(item[text_field])
      item[entities_field] = [(e.text, e.label_) for e in doc.ents]
      del item["_id"]
      del item[text_field]
      amcat.update_document(index, doc_id = id, body = item)
  
##  guests can now query the named entities with e.g.:
# text_data_vec = list(amcat.query("state_of_the_union", fields=["_id", "test"]))
# text_data_vec[0]
