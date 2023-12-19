# adapted example code from https://huggingface.co/Blablablab/newsSimilarity
import torch
import torch.nn
import matplotlib.pyplot as plt
from transformers import AutoTokenizer, AutoModel
import numpy as np
from huggingface_hub import hf_hub_download
import os
import json
from amcat4py import AmcatClient
# for testing
# from dotenv import load_dotenv
# load_dotenv()

amcat4_host = os.environ.get("amcat4_host")
index = os.environ.get("index")
text_field = os.environ.get("text_field")
vector_field = os.environ.get("vector_field")
torch_device = os.environ.get("torch_device")
queries = os.environ.get("queries")
filters = os.environ.get("filters")
batch_size = os.environ.get("batch_size")

# should already exist since it is built into the image
MODEL_PATH = hf_hub_download(repo_id="Blablablab/newsSimilarity", filename="state_dict.tar", local_dir=".")

#declare model class, inheriting from nn.Module 
class BiModel(torch.nn.Module):
    def __init__(self):
        super(BiModel,self).__init__()
        self.model = AutoModel.from_pretrained('sentence-transformers/all-mpnet-base-v2').to(device).train()
        self.cos = torch.nn.CosineSimilarity(dim=1, eps=1e-4)    
    #pool token level embeddings 
    def mean_pooling(self, token_embeddings, attention_mask):
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    #Note that here we expect only one batch of input ids and attention masks
    def encode(self, input_ids, attention_mask):
        encoding = self.model(input_ids.squeeze(1), attention_mask=attention_mask.squeeze(1))[0]
        meanPooled = self.mean_pooling(encoding, attention_mask.squeeze(1))
        return meanPooled
    #NOTE: here we expect a list of two that we then unpack
    def forward(self, input_ids, attention_mask):
        input_ids_a = input_ids[0].to(device)
        input_ids_b = input_ids[1].to(device)
        attention_a = attention_mask[0].to(device)
        attention_b = attention_mask[1].to(device)
        #encode sentence and get mean pooled sentence representation
        encoding1 = self.model(input_ids_a, attention_mask=attention_a)[0] #all token embeddings
        encoding2 = self.model(input_ids_b, attention_mask=attention_b)[0]
        meanPooled1 = self.mean_pooling(encoding1, attention_a)
        meanPooled2 = self.mean_pooling(encoding2, attention_b)
        pred = self.cos(meanPooled1, meanPooled2)
        return pred

#set device as needed, initialize model, load weights 
device = torch.device(torch_device)
trainedModel = BiModel()
sDict = torch.load(MODEL_PATH, map_location=device)

#may need to run depending on pytorch version 
del sDict["model.embeddings.position_ids"]

#initialize tokenizer for all-mpnet-base-v2
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-mpnet-base-v2')

#initialize model
trainedModel.load_state_dict(sDict)

#trainedModel is now ready to use, load data

if filters:
    filters = json.loads(filters) 

if queries:
  queries = queries + f"AND NOT(_exists_:{vector_field})"
else:
  queries = f"NOT(_exists_:{vector_field})"

# log in
amcat = AmcatClient(amcat4_host)

# set field if it does not exist (does nothing if entities_field exists already)
# the reason for choosing text type: 
# https://stackoverflow.com/a/62358568/5028841
amcat.set_fields(index=index, body={vector_field: "text"}) 
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

  for item in text_data:
      id = item["_id"]
      print(f"\t...processing _id: {id}")
      item["toks"] = tokenizer(item[text_field], max_length=384, padding="max_length", truncation=True, return_tensors="pt")
      # Move to the same device as model
      item["toks"] = {k: v.to(device) for k, v in item["toks"].items()}
      with torch.no_grad(): # disables gradient computation
          item[vector_field] = trainedModel.encode(item["toks"]['input_ids'], item["toks"]['attention_mask'])
          # detach from GPU to prevent further gradient computation
          item[vector_field] = item[vector_field].detach().cpu().numpy() 
      item[vector_field] = item[vector_field].tolist()
      del item["_id"]
      del item["toks"]
      del item[text_field]
      amcat.update_document(index, doc_id = id, body = item)
 

##  guests can now query the named entities with e.g.:
# text_data_vec = list(amcat.query("state_of_the_union", fields=["_id", vector_field]))
# text_data_vec[0]
