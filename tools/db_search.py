from chromadb import Client
from chromadb.config import Settings
import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()
# Connect to ChromaDB server
chroma_client = chromadb.HttpClient()
collection = chroma_client.get_collection(name="recipes")
ingredient_collection = chroma_client.get_collection(name="recipes_by_ingredients")


# Query by metadata
def query_by_metadata(tag, cuisine):
    results = collection.query(
        query_texts=[tag],
        where={"cuisine": cuisine}
    )
    print("Metadata Search Results:")
    for doc, meta in zip(results["documents"], results["metadatas"]):
        if meta:  # Ensure meta is not empty
            meta = meta[0]  # Access the first dictionary in the list
            print(f"Title: {meta['title']}, Cuisine: {meta['cuisine']}, URL: {meta['source_url']}")
        else:
            print("No metadata available for this document.")


def generate_ada_embedding(text, model='text-embedding-3-small'):
    text = text.replace('\n', ' ')
    return client.embeddings.create(input=[text], model=model).data[0].embedding


def query_by_ingredients(ingredient_query, n_results=3):
    # Generate embedding for the ingredient query
    ingredient_embedding = generate_ada_embedding(ingredient_query)

    # Perform similarity search
    results = ingredient_collection.query(
        query_embeddings=[ingredient_embedding],
        n_results=n_results
    )

    # Print the results
    print("Ingredient-Based Similarity Search Results:")
    for i, (doc, metas) in enumerate(zip(results["documents"], results["metadatas"])):
        if metas:  # Ensure metas is not empty
            meta = metas[0]  # Access the first metadata dictionary
            print(f"Result {i+1}:")
            print(f"Title: {meta['title']}")
            print(f"Cuisine: {meta['cuisine']}")
            print(f"URL: {meta['source_url']}")
            print("-" * 40)
        else:
            print(f"Result {i+1}: No metadata available.")


# Query by similarity
def query_by_similarity(query_text, n_results=3):
    # Initialize the embedding model

    # Generate the query embedding
    query_embedding = generate_ada_embedding(query_text)

    # Perform similarity search
    results = collection.query(
        query_embeddings=[query_embedding],  # Query using the embedding
        n_results=n_results  # Number of results to retrieve
    )

    # Print the results
    print("Similarity Search Results:")
    for i, (doc, metas) in enumerate(zip(results["documents"], results["metadatas"])):
        if metas:  # Ensure metas is not empty
            meta = metas[0]  # Access the first metadata dictionary
            print(f"Result {i+1}:")
            print(f"Title: {meta.get('title', 'Unknown')}")
            print(f"Cuisine: {meta.get('cuisine', 'Unknown')}")
            print(f"URL: {meta.get('source_url', 'Unknown')}")
            print("-" * 40)
        else:
            print(f"Result {i+1}: No metadata available.")


# Example Queries
# query_by_metadata(tag="Hauptspeise", cuisine="Italian")
query_by_ingredients("sugar", n_results=3)
