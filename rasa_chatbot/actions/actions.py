from typing import Any, Text, Dict, List

from rasa_sdk import Action
from SPARQLWrapper import SPARQLWrapper, JSON

class ActionListCourses(Action):
    def name(self):
        return "action_list_courses"

    def run(self, dispatcher, tracker, domain):
        university = tracker.get_slot('university')
        if university is None:
            university = ''

        sparql = SPARQLWrapper("http://localhost:3030/ds/query")  # Corrected URL
        sparql.setQuery(f"""
            PREFIX ns1: <http://example.org/>
            PREFIX dbp: <http://dbpedia.org/resource/>

            SELECT ?course
            WHERE {{
                ?course ns1:courseAt dbp:Concordia_University
            }}
            LIMIT 10
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        message = "Courses at Concordia:\n"
        for result in results["results"]["bindings"]:
            message += f'- {result["course"]["value"]}\n'

        dispatcher.utter_message(text=message)

        return []