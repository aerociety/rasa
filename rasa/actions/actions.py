from rasa_sdk import Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import random
import requests


class ActionGetRecipe(Action):
    def name(self):
        return "action_get_recipe"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        # Get the ingredients slot
        ingredients = tracker.get_slot("ingredient")
        if not ingredients:
            dispatcher.utter_message(text="I need some ingredients to find a recipe for you.")
            return []

        # Prepare the query string
        ingredient_query = ", ".join(ingredients)
        api_url = f"http://localhost:8844/search_by_ingredients?ingredient_query={ingredient_query}&n_results=3"

        try:
            # Make the API request
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()

            # Filter recipes by distance < 0.5
            filtered_recipes = [
                recipe for recipe in data.get("recipes", [])
                if recipe.get("distance", 1) < 0.75
            ]

            if filtered_recipes:
                # Format and send the recipes as a response
                recipe_messages = [
                    f"🍴 *{recipe['title']}* (Cuisine: {recipe['cuisine']}, Diet: {recipe['diet_type']})\n"
                    f"[View Recipe](/recipe/{recipe['id']})"
                    for recipe in filtered_recipes
                ]
                dispatcher.utter_message(text="\n\n".join(recipe_messages))
            else:
                # No recipes found within distance < 0.5
                dispatcher.utter_message(text="Sorry, I couldn't find any recipes matching your ingredients within a close match.")
        except requests.exceptions.RequestException as e:
            # Handle errors during API request
            dispatcher.utter_message(text="Sorry, I couldn't fetch recipes right now. Please try again later.")
            print(f"Error fetching recipes: {e}")

        return []


class ActionGetSubstitution(Action):
    def name(self):
        return "action_get_substitution"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        missing_ingredient = tracker.get_slot("ingredient")
        response = requests.get(f"http://localhost:8844/substitution?ingredient={missing_ingredient}")
        substitution = response.json().get("substitution", "Sorry, no substitution found.")
        dispatcher.utter_message(text=f"You can use {substitution} instead of {missing_ingredient}.")
        return []


class ActionGetCuisine(Action):
    def name(self):
        return "action_get_cuisine"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        # Get the cuisine slot and ensure it's capitalized
        cuisine = tracker.get_slot("cuisine")
        if not cuisine:
            dispatcher.utter_message(text="I need to know the cuisine type to find recipes.")
            return []
        cuisine = cuisine.capitalize()

        # Prepare the API URL with a high limit
        api_url = f"http://localhost:8844/recipes?page=1&limit=1000&cuisine={cuisine}"

        try:
            # Fetch recipes from the API
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()

            # Extract recipes from the response
            all_recipes = data.get("recipes", [])
            if not all_recipes:
                dispatcher.utter_message(text=f"Sorry, I couldn't find any recipes for {cuisine} cuisine.")
                return []

            # Randomly select up to 3 recipes
            selected_recipes = random.sample(all_recipes, min(3, len(all_recipes)))

            # Format and send the response
            recipe_messages = [
                f"🍴 *{recipe['title']}* (Cuisine: {recipe['cuisine']}, Diet: {recipe['diet_type']})\n"
                f"[View Recipe](/recipe/{recipe['id']})"
                for recipe in selected_recipes
            ]
            dispatcher.utter_message(text="\n\n".join(recipe_messages))
        except requests.exceptions.RequestException as e:
            # Handle errors during API request
            dispatcher.utter_message(text="Sorry, I couldn't fetch recipes right now. Please try again later.")
            print(f"Error fetching recipes: {e}")

        return []


class ActionGetDietaryOptions(Action):
    def name(self):
        return "action_get_dietary_options"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        diet_type = tracker.get_slot("diet_type")
        response = requests.get(f"http://localhost:8844/dietary?diet_type={diet_type}")
        recipes = response.json().get("recipes", "Sorry, no recipes found.")
        dispatcher.utter_message(text=f"Here are some {diet_type} recipes: {recipes}")
        return []
