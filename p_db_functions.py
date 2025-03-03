from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
import time
import openai
from embeddings_data import *

def get_embedding(text, model="multilingual-e5-large"):
    response = openai.Embedding.create(input=[text], model=model)
    embedding = response["data"][0]["embedding"]
    return embedding

def query_pinecone(index, query, top_k=5):
    query_embedding = get_embedding(query)
    result = index.query(query_embedding, top_k=top_k, include_metadata=True)
    return result

def build_prompt(query, retrieved_docs):
    # Extract text from metadata of each match
    context = "\n".join([doc["metadata"].get("text", "") for doc in retrieved_docs["matches"]])
    prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
    return prompt