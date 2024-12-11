import json
import re
import uuid

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI
from urllib.parse import urlparse, urlunparse
import os

load_dotenv()

client = OpenAI()


def get_base_url(url):
    """
    Removes query parameters and fragments from a URL.

    Args:
        url (str): The full URL to process.

    Returns:
        str: The base URL without query parameters or fragments.
    """
    parsed_url = urlparse(url)
    # Reconstruct the URL without query and fragment
    base_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    return base_url


def fetch_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch the URL. Status code: {response.status_code}")


def extract_text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")

    # Remove scripts and styles
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()

    # Extract links and images
    for a in soup.find_all("a", href=True):
        # Add the link's href to the text
        a.insert_after(f" [Link: {a['href']}]")
    for img in soup.find_all("img", src=True):
        # Add the image's src to the text
        img.insert_after(f" [Image: {img['src']}]")

    return soup.get_text()


def extract_recipe_from_url(url):
    html_content = fetch_html(url)
    plain_text = extract_text_from_html(html_content)

    prompt = f"""
    Extract and format the recipe from the following text into the structure below:

    {{
      "title": "Recipe Title",
      "ingredients": ["list of ingredients"],
      "core_ingredients": ["list of core ingredients"],
      "instructions": "step-by-step instructions",
      "tags": ["relevant tags"],
      "diet_type": "e.g., Vegetarian, Vegan, Non-Vegetarian",
      "cuisine": "e.g., Italian, Chinese, Indian",
      "time_to_eat": estimate how long it takes from cutting to cooking to eating for an average cook in minutes,
      "suggestion_links": ["list of links to suggested recipes"],
      "img_links": ["list of links to images for this recipe"]
    }}
    
    Always answer with JSON only. If an error occurs, answer with an JSON containing the reason in the
    error field. Explain what is missing and why something is an error. 
    Everything should be translated to english. Core ingredients should be only the ingredient itself
    without any measurement. e.g. 15ml of honey should be just 'honey'. Often the recipe is hidden in html code and
    other useless stuff, extract only the recipe and ignore the rest. Suggestion links can often be found in <a> tags
    in href. Keep the link intact as is! otherwise they will break!. The links will look similar to {url}. The img_links
    should only include direct images that can be embedded later.

    Recipe Text:
    {plain_text}

    Output:
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    raw_response = response.choices[0].message.content
    cleaned_response = clean_gpt_response(raw_response)

    if isinstance(cleaned_response, str):
        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            raise ValueError("Failed to decode GPT's response as JSON.")
    elif isinstance(cleaned_response, dict):
        return cleaned_response  # Already a dict
    else:
        raise ValueError("Unexpected GPT response format.")


def save_recipe(recipe_data, folder="../db/recipes_raw"):
    """
    Save the recipe JSON data to a file with a UUID as the filename.
    """
    # Generate a UUID for the recipe
    recipe_id = str(uuid.uuid4())

    # Ensure the output folder exists
    os.makedirs(folder, exist_ok=True)

    # Update the recipe JSON with the ID and source URL
    recipe_data["id"] = recipe_id

    # Save the recipe JSON to a file
    file_path = os.path.join(folder, f"{recipe_id}.json")
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(recipe_data, file, indent=4, ensure_ascii=False)

    full_path = os.path.abspath(file_path)
    print(f"Recipe saved to {full_path}")
    return full_path


def clean_gpt_response(response_text):
    """
    Clean GPT response to extract valid JSON and handle single quotes.
    """
    # Remove code block markers (```json ... ```)
    if response_text.startswith("```json"):
        response_text = response_text.strip("```json").strip()
    if response_text.endswith("```"):
        response_text = response_text.rstrip("```").strip()

    # Replace single quotes with double quotes for valid JSON
    # Use regex to ensure we're replacing only those outside of valid JSON strings
    # response_text = re.sub(r"(?<!\\)'", '"', response_text)

    return response_text


auto = True
links_traversed = []
links_open = []

if __name__ == "__main__":
    while True:
        try:
            # Prompt user for URL
            recipe_url = input("Enter a recipe URL (or 'exit' to quit): ").strip()
            recipe_data = ""
            if recipe_url.lower() == "exit":
                print("Exiting...")
                break

            if recipe_url.lower() == "raw":
                print("Paste recipe here")
                recipe_data = input()
            else:
                print("Processing the recipe...")
                recipe_data = extract_recipe_from_url(recipe_url)
                recipe_data["source_url"] = recipe_url

            if "error" in recipe_data:
                print(f"Error: {recipe_data['error']}")
                continue

            # Save the recipe
            save_recipe(recipe_data)

            if auto:
                links_open.extend(list(map(lambda url: get_base_url(url), recipe_data["suggestion_links"])))
                links_traversed.append(get_base_url(recipe_url))
                links_open = [item for item in links_open if item not in links_traversed]

            while auto:
                if len(links_open) > 0:
                    next_url = links_open.pop()
                    print(f"auto fetching {next_url}")

                    recipe_data = extract_recipe_from_url(next_url)
                    recipe_data["source_url"] = next_url

                    if "error" in recipe_data:
                        print(f"Error: {recipe_data['error']}")
                        continue

                    save_recipe(recipe_data)

                    links_open.extend(list(map(lambda url: get_base_url(url), recipe_data["suggestion_links"])))
                    links_traversed.append(get_base_url(next_url))
                    links_open = [item for item in links_open if item not in links_traversed]
                else:
                    print("Cannot auto-fetch more recipes")
                    break

        except Exception as e:
            print(f"An error occurred: {e}")
