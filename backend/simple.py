from chromadb.api.types import IncludeEnum
from fastapi import FastAPI, Query
from typing import List, Optional
from uuid import UUID
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# Load envs and setup openai client
load_dotenv()
client = OpenAI()

# Initialize FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add the origin(s) that are allowed to access your backend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Initialize ChromaDB client
chroma_client = chromadb.HttpClient()

# Connect to collections
recipes_collection = chroma_client.get_collection(name="recipes")
ingredients_collection = chroma_client.get_collection(name="recipes_by_ingredients")


# Dummy function to simulate embedding generation
def generate_ada_embedding(text: str, model='text-embedding-3-small'):
    text = text.replace('\n', ' ')
    return client.embeddings.create(input=[text], model=model).data[0].embedding


def generate_zero_vector(dim: int):
    return [0.0] * dim


def extract_recipes(results):
    recipes = []
    for i in range(len(results["ids"][0])):
        # Extract metadata dynamically
        metadata = results["metadatas"][0][i]
        recipe = {"id": results["ids"][0][i], "distance": results["distances"][0][i]}

        # Add all metadata fields dynamically
        recipe.update(metadata)

        recipes.append(recipe)
    return recipes


def build_filters(
        diet_type: Optional[str] = None,
        cuisine: Optional[str] = None,
        min_time_to_eat: Optional[int] = None,
        max_time_to_eat: Optional[int] = None
):
    conditions = []
    if diet_type:
        conditions.append({"diet_type": {"$eq": diet_type}})
    if cuisine:
        conditions.append({"cuisine": {"$eq": cuisine}})
    if min_time_to_eat is not None:
        conditions.append({"time_to_eat": {"$gte": min_time_to_eat}})
    if max_time_to_eat is not None:
        conditions.append({"time_to_eat": {"$lte": max_time_to_eat}})

    # Combine conditions using $and if there are multiple conditions
    if len(conditions) > 1:
        return {"$and": conditions}
    elif conditions:
        return conditions[0]  # Single condition, no need for $and
    else:
        return None  # No filters


@app.get("/diet_types")
def get_diet_types():
    # Generate a zero vector with the correct dimensionality
    zero_vector = generate_zero_vector(1536)  # Adjust to your collection's dimensionality

    # Perform the query using the zero vector as a placeholder
    results = recipes_collection.query(
        query_embeddings=[zero_vector],  # Placeholder embedding
        n_results=recipes_collection.count()  # Retrieve all documents
    )

    # Extract distinct diet types
    if "metadatas" in results:
        diet_types = set(
            meta.get("diet_type", "Unknown")
            for metas in results["metadatas"]
            for meta in metas if meta
        )
        return list(diet_types)

    # Return empty list if no data found
    return []


@app.get("/cuisines")
def get_cuisines():
    # Generate a zero vector with the correct dimensionality
    zero_vector = generate_zero_vector(1536)  # Adjust to match your collection's dimensionality

    # Perform the query using the zero vector as a placeholder
    results = recipes_collection.query(
        query_embeddings=[zero_vector],  # Use a zero vector as a placeholder embedding
        n_results=recipes_collection.count()  # Retrieve all documents
    )

    # Extract unique cuisines from the metadata
    if "metadatas" in results:
        cuisines = set(
            meta.get("cuisine", "Unknown")
            for metas in results["metadatas"]
            for meta in metas if meta
        )
        return list(cuisines)

    # Return an empty list if no data is found
    return []


@app.get("/recipes/{recipe_id}")
def get_recipe_by_id(recipe_id: UUID):
    # Generate a zero vector with the correct dimensionality
    zero_vector = generate_zero_vector(1536)  # Adjust to match your collection's dimensionality

    # Perform the query using the zero vector as a placeholder
    results = recipes_collection.query(
        query_embeddings=[zero_vector],  # Use the zero vector
        where={"id": str(recipe_id)},  # Filter by recipe ID
        n_results=1  # Limit results to 1
    )

    # Check if any documents are found
    if results["documents"]:
        return {"recipe": results["documents"][0], "metadata": results["metadatas"][0]}

    # Return an error if no recipe is found
    return {"error": "Recipe not found"}


@app.get("/recipes")
def get_recipes_paginated(
        page: int = Query(1, ge=1),  # Page number, default is 1
        limit: int = Query(10, ge=1),  # Number of recipes per page, default is 10
        diet_type: Optional[str] = None,
        cuisine: Optional[str] = None,
        min_time_to_eat: Optional[int] = Query(None, ge=0),
        max_time_to_eat: Optional[int] = Query(None, ge=0)
):
    # Build filters
    filters = build_filters(diet_type, cuisine, min_time_to_eat, max_time_to_eat)
    zero_vector = generate_zero_vector(1536)

    print(filters)

    # Query recipes with filters
    results = recipes_collection.query(
        query_embeddings=[zero_vector],  # Placeholder embedding
        n_results=recipes_collection.count(),  # Fetch all available results
        include=[IncludeEnum.metadatas],
        where=filters
    )

    # Flatten the nested list
    all_metadatas = [meta for sublist in results["metadatas"] for meta in sublist]

    if not all_metadatas:
        return {"error": "No recipes found"}

    total_recipes = len(all_metadatas)
    offset = (page - 1) * limit

    # Ensure offset does not exceed total results
    if offset >= total_recipes:
        return {"error": "Page exceeds total available recipes"}

    # Apply pagination manually
    paginated_metadata = all_metadatas[offset:offset + limit]

    recipes = [meta for meta in paginated_metadata]

    return {
        "page": page,
        "limit": limit,
        "total_recipes": total_recipes,
        "recipes": recipes,
    }





@app.get("/search_by_ingredients")
def search_by_ingredients(
        ingredient_query: str,
        n_results: int = 3,
        diet_type: Optional[str] = None,
        cuisine: Optional[str] = None,
        min_time_to_eat: Optional[int] = Query(None, ge=0),
        max_time_to_eat: Optional[int] = Query(None, ge=0)
):
    # Generate embedding for the ingredient query
    ingredient_embedding = generate_ada_embedding(ingredient_query)
    filters = build_filters(diet_type, cuisine, min_time_to_eat, max_time_to_eat)

    # Perform similarity search
    results = ingredients_collection.query(
        query_embeddings=[ingredient_embedding],
        n_results=n_results,
        include=[IncludeEnum.distances, IncludeEnum.documents, IncludeEnum.metadatas],
        where=filters
    )

    # Use the helper function to extract recipes
    recipes = extract_recipes(results)

    return {"recipes": recipes}


@app.get("/recipes/search_by_text")
def search_by_text(
        query_text: str,
        n_results: int = 3,
        diet_type: Optional[str] = None,
        cuisine: Optional[str] = None,
        min_time_to_eat: Optional[int] = Query(None, ge=0),
        max_time_to_eat: Optional[int] = Query(None, ge=0)
):
    query_embedding = generate_ada_embedding(query_text)
    filters = build_filters(diet_type, cuisine, min_time_to_eat, max_time_to_eat)

    results = recipes_collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=filters
    )

    # Use the helper function to extract recipes
    recipes = extract_recipes(results)

    return {"recipes": recipes}


@app.get("/recipes/filter")
def filter_recipes(
        diet_type: Optional[str] = None,
        cuisine: Optional[str] = None,
        min_time_to_eat: Optional[int] = Query(None, ge=0),
        max_time_to_eat: Optional[int] = Query(None, ge=0)
):
    filters = {}
    zero_vector = generate_zero_vector(1536)
    if diet_type:
        filters["diet_type"] = diet_type
    if cuisine:
        filters["cuisine"] = cuisine
    if min_time_to_eat is not None:
        filters["time_to_eat"] = {"$gte": min_time_to_eat}
    if max_time_to_eat is not None:
        filters["time_to_eat"] = {**filters.get("time_to_eat", {}), "$lte": max_time_to_eat}

    results = recipes_collection.query(
        query_embeddings=[zero_vector],
        where=filters
    )

    # Use the helper function to extract recipes
    recipes = extract_recipes(results)

    return {"recipes": recipes}

