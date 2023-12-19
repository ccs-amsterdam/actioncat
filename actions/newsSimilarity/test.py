# adapted example code from https://huggingface.co/Blablablab/newsSimilarity
# runs during build to pre-load neccesary models into the image
import torch
import torch.nn
from transformers import AutoTokenizer, AutoModel
import numpy as np
from huggingface_hub import hf_hub_download
import os
import json

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
device = torch.device("cpu")
trainedModel = BiModel()
sDict = torch.load(MODEL_PATH, map_location=device)

#may need to run depending on pytorch version 
del sDict["model.embeddings.position_ids"]

#initialize tokenizer for all-mpnet-base-v2
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-mpnet-base-v2')

example_text = "This is a test"
example_inputs = tokenizer(example_text, max_length=384, padding="max_length", truncation=True, return_tensors="pt")

# Move to the same device as model
example_inputs = {k: v.to(device) for k, v in example_inputs.items()}

# Encode the example
with torch.no_grad():
    example_embedding = trainedModel.encode(example_inputs['input_ids'], example_inputs['attention_mask'])
    example_embedding = example_embedding.detach().cpu().numpy()

# Output the embedding
print("Embedding for 'This is a test':", example_embedding)
