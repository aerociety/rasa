import os
import json
from sentence_transformers import SentenceTransformer
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# Initialize ChromaDB client
chroma_client = chromadb.HttpClient()

# Define embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Directory containing recipe JSON files
recipes_dir = "../db/recipes_raw"


# Preprocess recipes into a single string for embedding
def preprocess_recipe(recipe):
    text = f"{recipe['title']} {', '.join(recipe.get('ingredients', []))} {', '.join(recipe.get('tags', []))} {recipe.get('cuisine', '')} {recipe.get('diet_type', '')} {recipe.get('instructions', '')}"
    return text


# Preprocess ingredients only
def preprocess_ingredients(recipe):
    return ", ".join(recipe.get('core_ingredients', []))


def generate_ada_embedding(text, model='text-embedding-3-small'):
    text = text.replace('\n', ' ')
    return client.embeddings.create(input=[text], model=model).data[0].embedding


# Read all JSON files from the directory and process
recipes = []
for filename in os.listdir(recipes_dir):
    if filename.endswith(".json"):
        file_path = os.path.join(recipes_dir, filename)
        with open(file_path, "r", encoding="utf-8") as file:
            recipe = json.load(file)
            recipe_text = preprocess_recipe(recipe)
            recipe_embedding = generate_ada_embedding(recipe_text)
            ingredient_embedding = generate_ada_embedding(preprocess_ingredients(recipe))
            recipes.append({
                "id": recipe.get("id", filename),  # Use file name as ID if 'id' is missing
                "title": recipe.get("title", "Unknown Title"),
                "ingredients": recipe.get("ingredients", []),
                "tags": recipe.get("tags", []),
                "cuisine": recipe.get("cuisine", "Unknown"),
                "diet_type": recipe.get("diet_type", "Unknown"),
                "time_to_eat": recipe.get("time_to_eat", "-"),
                "img_links": recipe.get("img_links", []),
                "instructions": recipe.get("instructions", ""),
                "source_url": recipe.get("source_url", ""),
                "embedding": recipe_embedding,
                "ingredient_embedding": ingredient_embedding
            })

# Create the main recipes collection
collection = chroma_client.get_or_create_collection(name="recipes", metadata={"hnsw:space": "cosine"})

# Create the ingredients-specific collection
ingredient_collection = chroma_client.get_or_create_collection(name="recipes_by_ingredients",
                                                               metadata={"hnsw:space": "cosine"})

# Insert recipes into the main collection
for recipe in recipes:
    collection.add(
        documents=[preprocess_recipe(recipe)],
        metadatas=[{
            "id": recipe["id"],
            "title": recipe["title"],
            "tags": ", ".join(recipe["tags"]),  # Convert list to comma-separated string
            "cuisine": recipe["cuisine"],
            "diet_type": recipe["diet_type"],
            "instructions": recipe["instructions"],
            "ingredients": ", ".join(recipe["ingredients"]),
            "img_links": ", ".join(recipe["img_links"]),
            "time_to_eat": recipe.get("time_to_eat", "-"),
            "source_url": recipe["source_url"]
        }],
        ids=[recipe["id"]],
        embeddings=[recipe["embedding"]]
    )

# Insert recipes into the ingredients-specific collection
for recipe in recipes:
    ingredient_collection.add(
        documents=[preprocess_ingredients(recipe)],
        metadatas=[{
            "id": recipe["id"],
            "title": recipe["title"],
            "tags": ", ".join(recipe["tags"]),  # Convert list to comma-separated string
            "cuisine": recipe["cuisine"],
            "diet_type": recipe["diet_type"],
            "instructions": recipe["instructions"],
            "ingredients": ", ".join(recipe["ingredients"]),
            "img_links": ", ".join(recipe["img_links"]),
            "time_to_eat": recipe.get("time_to_eat", "-"),
            "source_url": recipe["source_url"]
        }],
        ids=[recipe["id"]],
        embeddings=[recipe["ingredient_embedding"]]
    )

print(f"Inserted {len(recipes)} recipes into ChromaDB.")
