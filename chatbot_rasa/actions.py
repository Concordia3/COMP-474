from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests


class ActionReturnAllCourses(Action):

    def name(self) -> Text:
        return "action_return_all_courses"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        query = """
            PREFIX ns1: <http://example.org/>
            PREFIX dbp: <http://dbpedia.org/resource/>
            
            SELECT ?course
            WHERE {
              ?course ns1:courseAt dbp:Concordia_University
            }
        """

        response = requests.post('http://localhost:3030/concordia/query',
                                 data={'query': query})

        results = response.json()

        course_list = []
        # Check if 'bindings' key exists (adjust based on your Fuseki response format)
        if 'bindings' in results:
            course_list = [result['course']['value'] for result in results['bindings']]

        if course_list:
            dispatcher.utter_message("Here are all the courses offered by Concordia University:")
            for course in course_list:
                dispatcher.utter_message(course)
        else:
            dispatcher.utter_message("No courses found.")

        return []
