import pinecone

with open("p_key.txt", "r") as f:
    p_key = f.read().strip()
pinecone.init(api_key=p_key, environment="us-west1-gcp")

index_names = ["l1_index", "l2_index", "l3_index", "l4_index", "l5_index", "l6_index"]
for idx in index_names:
    if idx not in pinecone.list_indexes():
        pinecone.create_index(idx, dimension=1536, metric="cosine")

indeces = {idx: pinecone.Index(idx) for idx in index_names}

def get_embedding(text):
    

