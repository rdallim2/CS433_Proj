from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
import time
import time
import openai
from embeddings_data import *

# Initialize Pinecone with your API key
with open("key.txt", "r") as f:
    openai.api_key = f.read().strip()

with open("p_key.txt", "r") as f:
    p_api_key = f.read().strip()

pc = Pinecone(api_key=p_api_key)

def get_embedding(text):
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

# Create index if it doesn't exist
index_names = ["l3-index", "l4-index", "l5-index"]
for idx in index_names:
    if idx not in pc.list_indexes().names():
        pc.create_index(
            idx, 
            dimension=1536,  # Make sure this matches the OpenAI embedding dimension
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )

# Wait for the index to be ready
for idx in index_names:
    while not pc.describe_index(idx).status['ready']:
        time.sleep(1)

    index = pc.Index(idx)

    # Prepare embeddings for batch upsert
    vectors = []
    data_name = str(idx[:2]) + "_data"
    data = globals().get(data_name, [])
    print(f"Data name: {data_name}")
    for d in data:
        embedding = get_embedding(d['text'])  # Generate embedding directly with OpenAI
        vectors.append({
            "id": d['id'],
            "values": embedding,
            "metadata": {"text": d['text']}
        })

    # Upsert vectors to Pinecone
    index.upsert(
        vectors=vectors,
        namespace="ns1"
    )

    print(f"Vectors uploaded to {idx}")
    print(index.describe_index_stats())
