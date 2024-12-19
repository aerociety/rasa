from typing import Text, List, Any, Dict

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
import random
import requests


class ActionGetRecipe(Action):
    def name(self):
        return "action_get_recipe"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        # Extract ingredients from the slot
        ingredients = tracker.get_slot("ingredient")
        if not ingredients:
            dispatcher.utter_message(text="I need some ingredients to find a recipe for you.")
            # Reset diet_type and cuisine if they exist
            return [
                SlotSet("diet_type", None),
                SlotSet("cuisine", None)
            ]

        # Prepare ingredient_query by joining all ingredients
        ingredient_query = ", ".join(ingredients)

        # Extract diet_type and cuisine from the current message
        current_diet_type = None
        current_cuisine = None

        # Get 'diet_type' entities from the latest message
        diet_type_entities = [
            e for e in tracker.latest_message.get('entities', [])
            if e['entity'] == 'diet_type'
        ]
        if diet_type_entities:
            current_diet_type = diet_type_entities[0]['value']

        # Get 'cuisine' entities from the latest message
        cuisine_entities = [
            e for e in tracker.latest_message.get('entities', [])
            if e['entity'] == 'cuisine'
        ]
        if cuisine_entities:
            current_cuisine = cuisine_entities[0]['value']

        # Prepare query parameters
        params = {
            "ingredient_query": ingredient_query,
            "n_results": 3
        }

        if current_diet_type:
            params["diet_type"] = current_diet_type
        if current_cuisine:
            params["cuisine"] = current_cuisine

        api_url = "http://localhost:8844/search_by_ingredients"

        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()

            recipes = data.get("recipes", [])

            if recipes:
                dispatcher.utter_message(text="Here are some recipes that you might like:")
                dispatcher.utter_message(json_message={"recipes": recipes})
            else:
                dispatcher.utter_message(text="Sorry, I couldn't find any close matches based on your criteria.")
        except requests.exceptions.RequestException as e:
            dispatcher.utter_message(text="Sorry, I couldn't fetch recipes right now. Please try again later.")
            print(f"Error fetching recipes: {e}")

        # Update slots based on current message
        return [
            SlotSet("diet_type", None),
            SlotSet("cuisine", None),
            SlotSet("ingredient", None)
        ]


class ActionGetSubstitution(Action):
    def name(self) -> Text:
        return "action_get_substitution"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        # Get the ingredient from the slot
        ingredient = tracker.get_slot("ingredient")

        if not ingredient:
            dispatcher.utter_message(text="I need to know which ingredient to substitute. Please provide one.")
            return []

        if type(ingredient) is list:
            ingredient = " ".join(ingredient)

        # Send the request to the substitution API
        api_url = f"http://localhost:8844/substitute?query={ingredient}"
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()

            # Check if substitutions are available
            substitutions = data.get("substitutions")
            if substitutions:
                substitutes_text = ", ".join(substitutions)
                dispatcher.utter_message(text=f"You can use these substitutes for {ingredient}: {substitutes_text}.")
            else:
                dispatcher.utter_message(text=f"Sorry, I couldn't find any substitutes for {ingredient}.")
        except requests.exceptions.RequestException as e:
            dispatcher.utter_message(text="I couldn't fetch the substitution data. Please try again later.")
            print(f"Error fetching substitution data: {e}")

        # Reset the slot after providing the response
        return [SlotSet("ingredient", None)]


class ActionSearchByText(Action):
    def name(self):
        return "action_search_by_text"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        # Extract slots
        query_text = tracker.get_slot("query_text")
        diet_type = tracker.get_slot("diet_type")
        cuisine = tracker.get_slot("cuisine")

        # Build query_text if it's not provided
        if not query_text and (diet_type or cuisine):
            # Use non-None arguments to build query_text
            # components = [diet_type, cuisine]
            # query_text = " ".join(filter(None, components))
            query_text = ""

        # If query_text is still empty, return an error
        if not query_text and query_text != "":
            dispatcher.utter_message(text="I need something to search for. Please provide a query.")
            return [
                SlotSet("diet_type", None),
                SlotSet("cuisine", None),
                SlotSet("ingredient", None),
                SlotSet("query_text", None)
            ]

        # Extract entities from the latest message
        current_diet_type = None
        current_cuisine = None

        diet_type_entities = [
            e for e in tracker.latest_message.get('entities', [])
            if e['entity'] == 'diet_type'
        ]
        if diet_type_entities:
            current_diet_type = diet_type_entities[0]['value']

        cuisine_entities = [
            e for e in tracker.latest_message.get('entities', [])
            if e['entity'] == 'cuisine'
        ]
        if cuisine_entities:
            current_cuisine = cuisine_entities[0]['value']

        # Get all 'ingredient' entities from the latest message
        ingredients = tracker.get_slot("ingredient")
        ingredient_query = ", ".join(ingredients) if ingredients else None

        # Prepare query parameters
        params = {
            "query_text": query_text,
            "n_results": 3
        }

        if current_diet_type:
            params["diet_type"] = current_diet_type
        if current_cuisine:
            params["cuisine"] = current_cuisine
        if ingredient_query:
            params["ingredient_query"] = ingredient_query

        api_url = "http://localhost:8844/search_by_text"

        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()
            recipes = data.get("recipes", [])

            if recipes:
                dispatcher.utter_message(text="Here are some recipes based on your search:")
                dispatcher.utter_message(json_message={"recipes": recipes})
            else:
                dispatcher.utter_message(text="Sorry, I couldn't find any recipes matching your search.")
        except requests.exceptions.RequestException as e:
            dispatcher.utter_message(text="Sorry, I couldn't fetch recipes right now. Please try again later.")
            print(f"Error fetching recipes by text: {e}")

        # Reset query_text after each search
        return [
            SlotSet("diet_type", None),
            SlotSet("cuisine", None),
            SlotSet("ingredient", None),
            SlotSet("query_text", None)
        ]


class ActionGetCuisine(Action):
    def name(self):
        return "action_get_cuisine"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        cuisine = tracker.get_slot("cuisine")
        if not cuisine:
            dispatcher.utter_message(text="I need to know the cuisine type to find recipes.")
            return [SlotSet("diet_type", None)]

        # Prepare query parameters
        params = {
            "cuisine": cuisine,
            "limit": 3,
            "page": 1
        }

        diet_type = tracker.get_slot("diet_type")
        if diet_type:
            params["diet_type"] = diet_type

        api_url = "http://localhost:8844/recipes"

        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()
            recipes = data.get("recipes", [])

            if recipes:
                dispatcher.utter_message(text=f"Here are some {cuisine} recipes you might like:")
                dispatcher.utter_message(json_message={"recipes": recipes})
            else:
                dispatcher.utter_message(text=f"Sorry, I couldn't find any {cuisine} recipes.")
        except requests.exceptions.RequestException as e:
            dispatcher.utter_message(text="Sorry, I couldn't fetch recipes right now. Please try again later.")
            print(f"Error fetching cuisine recipes: {e}")

        # Update slots based on current message
        return [
            SlotSet("diet_type", None),
            SlotSet("cuisine", None),
            SlotSet("ingredient", None),
            SlotSet("query_text", None)
        ]


class ActionGetDietaryOptions(Action):
    def name(self):
        return "action_get_dietary_options"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        diet_type = tracker.get_slot("diet_type")
        if not diet_type:
            dispatcher.utter_message(text="I need to know the diet type to find recipes.")
            return [SlotSet("cuisine", None)]

        # Prepare query parameters
        params = {
            "diet_type": diet_type,
            "limit": 3,
            "page": 1
        }

        cuisine = tracker.get_slot("cuisine")
        if cuisine:
            params["cuisine"] = cuisine

        api_url = "http://localhost:8844/recipes"

        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()
            recipes = data.get("recipes", [])

            if recipes:
                dispatcher.utter_message(text=f"Here are some {diet_type} recipes:")
                dispatcher.utter_message(json_message={"recipes": recipes})
            else:
                dispatcher.utter_message(text=f"Sorry, I couldn't find any {diet_type} recipes.")
        except requests.exceptions.RequestException as e:
            dispatcher.utter_message(text="Sorry, I couldn't fetch recipes right now. Please try again later.")
            print(f"Error fetching dietary recipes: {e}")

        # Update slots based on current message
        return [
            SlotSet("diet_type", None),
            SlotSet("cuisine", None),
            SlotSet("ingredient", None),
            SlotSet("query_text", None)
        ]
