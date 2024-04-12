from typing import Any, Text, Dict, List

import rasa_sdk
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests


class ActionReturnAllCourses(Action):

    def name(self) -> Text:
        return "action_return_all_courses"

    def run(self, dispatcher, tracker, domain):

        query = """
            PREFIX ns1: <http://example.org/>
            PREFIX dbp: <http://dbpedia.org/resource/>

            SELECT ?course
            WHERE {
              ?course ns1:courseAt dbp:Concordia_University
            }
        """
        print("HELLOOOOOO")
        response = requests.post('http://localhost:3030/concordia/query',
                                 data={'query': query})

        results = response.json()['results']['bindings']
        if results:
            dispatcher.utter_message("Here are all the courses offered by Concordia University:")
            for binding in results:
                course_uri = binding['course']['value']
                dispatcher.utter_message(course_uri)
        else:
            dispatcher.utter_message("No courses found.")

        return []
