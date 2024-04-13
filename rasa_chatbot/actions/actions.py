from typing import Any, Text, Dict, List

from rasa_sdk import Action
from SPARQLWrapper import SPARQLWrapper, JSON
from rasa_sdk.events import SlotSet


class ActionListCourses(Action):
    def name(self):
        return "action_list_courses"

    def run(self, dispatcher, tracker, domain):
        university = tracker.get_slot('university')
        if university is None:
            university = ''

        sparql = SPARQLWrapper("http://localhost:3030/concordia/query")
        sparql.setQuery(f"""
            PREFIX ns1: <http://example.org/>
            PREFIX dbp: <http://dbpedia.org/resource/>

            SELECT ?course
            WHERE {{
                ?course ns1:courseAt dbp:Concordia_University
            }}
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        message = "Courses at Concordia:\n"
        for result in results["results"]["bindings"]:
            message += f'- {result["course"]["value"]}\n'

        dispatcher.utter_message(text=message)

        return []


class DiscussedTopic(Action):
    def name(self):
        return "action_discussed_topic"

    def run(self, dispatcher, tracker, domain):
        topic = tracker.get_slot('topic')
        if topic is None:
            topic = ''

        sparql = SPARQLWrapper("http://localhost:3030/concordia/query")
        sparql.setQuery(f"""
            PREFIX ns1: <http://example.org/>
        
            SELECT ?courseTitle
            WHERE {{
            ?course a ns1:Course;
            ns1:hasTitle ?courseTitle;
            ns1:hasDescription ?description;
            FILTER
            regex(?description, "{tracker.slots['topic']}", "i").
            }}

    """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        message = "The courses are:\n"
        for result in results["results"]["bindings"]:
            message += f'- {result["courseTitle"]["value"]}\n'

        dispatcher.utter_message(text=message)

        return []


class TopicDiscussedLecture(Action):
    def name(self):
        return "action_topic_discussed_lecture"

    def run(self, dispatcher, tracker, domain):
        lecture = int(tracker.get_slot('lecture'))
        courseName = tracker.get_slot('courseName')
        courseNumber = tracker.get_slot('courseNumber')
        if lecture is None:
            lecture = 0
        if courseName is None:
            courseName = ''
        if courseNumber is None:
            courseNumber = 0

        sparql = SPARQLWrapper("http://localhost:3030/concordia/query")
        sparql.setQuery(f"""
        PREFIX ns1: <http://example.org/>

        SELECT ?topic
        WHERE {{
        ?lecture a ns1:Lecture;
        ns1:contentFor <http://example.org/{tracker.slots['courseName']}/{tracker.slots['courseNumber']}> ;
        ns1:contentNumber {tracker.slots['lecture']} ;
        ns1:contentTopic ?topic.
        }}
        """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        message = "The topics are:\n"
        for result in results["results"]["bindings"]:
            message += f'- {result["topic"]["value"]}\n'

        dispatcher.utter_message(text=message)

        return []


class OfferedInSubject(Action):
    def name(self):
        return "action_offered_in_subject"

    def run(self, dispatcher, tracker, domain):
        courseName = tracker.get_slot('courseName')
        if courseName is None:
            courseName = ''

        sparql = SPARQLWrapper("http://localhost:3030/concordia/query")
        sparql.setQuery(f"""
        PREFIX ns1: <http://example.org/>
        PREFIX dbp: <http://dbpedia.org/resource/>

        SELECT ?course
        WHERE {{
        ?course ns1:courseAt dbp:Concordia_University;
        ns1:hasCourseCode "{tracker.slots['courseName']}".
        }}
        ORDER BY ?course
        """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        message = "The courses are:\n"
        for result in results["results"]["bindings"]:
            message += f'- {result["course"]["value"]}\n'

        dispatcher.utter_message(text=message)

        return []


class RecommendedMaterials(Action):
    def name(self):
        return "action_recommended_materials"

    def run(self, dispatcher, tracker, domain):
        courseName = tracker.get_slot('courseName')
        courseNumber = tracker.get_slot('courseNumber')
        topic = tracker.get_slot('topic')

        if courseName is None:
            courseName = ''
        if courseNumber is None:
            courseNumber = 0
        if topic is None:
            topic = ''

        sparql = SPARQLWrapper("http://localhost:3030/concordia/query")
        sparql.setQuery(f"""
        PREFIX ns1: <http://example.org/>

        SELECT ?materialType ?materialName ?materialLink
        WHERE {{
        ?lecture a ns1:Lecture ;
        ns1:contentFor <http://example.org/{tracker.slots['courseName']}/{tracker.slots['courseNumber']}> ;
        ns1:topic "{tracker.slots['topic']}" ;
        ns1:contentName ?materialName ;
        ns1:contentLink ?materialLink .
        BIND("slides" AS ?materialType) .
        }}
        """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        message = "The courses are:\n"
        for result in results["results"]["bindings"]:
            material_type = result["materialType"]["value"]
            material_name = result["materialName"]["value"]
            material_link = result["materialLink"]["value"]
            message += f'- Material Type: {material_type}, Material Name: {material_name}, Material Link: {material_link}\n'

        dispatcher.utter_message(text=message)

        return []


class CreditsCourse(Action):
    def name(self):
        return "action_credits_course"

    def run(self, dispatcher, tracker, domain):
        courseName = tracker.get_slot('courseName')
        courseNumber = tracker.get_slot('courseNumber')
        if courseName is None:
            courseName = ''
        if courseNumber is None:
            courseNumber = 0

        sparql = SPARQLWrapper("http://localhost:3030/concordia/query")
        sparql.setQuery(f"""
        PREFIX ns1: <http://example.org/>
        PREFIX dbp: <http://dbpedia.org/resource/>
        
        SELECT ?credits
        WHERE {{
        ?course ns1:courseAt dbp:Concordia_University;
        ns1:hasCourseCode "{tracker.slots['courseName']}";
        ns1:hasCourseNumber "{tracker.slots['courseNumber']}";
        ns1:hasCredits ?credits.
        }}
        """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        message = "Credits:\n"
        for result in results["results"]["bindings"]:
            # Access the credit value and convert it to float (assuming it's a string)
            credit_value = float(result["credits"]["value"])
            message += f'- {credit_value}\n'

        dispatcher.utter_message(text=message)

        return []


class AdditionalResources(Action):
    def name(self):
        return "action_additional_resources"

    def run(self, dispatcher, tracker, domain):
        courseName = tracker.get_slot('courseName')
        courseNumber = tracker.get_slot('courseNumber')
        if courseName is None:
            courseName = ''
        if courseNumber is None:
            courseNumber = 0

        sparql = SPARQLWrapper("http://localhost:3030/concordia/query")
        sparql.setQuery(f"""
        PREFIX ns1: <http://example.org/>
        PREFIX dbp: <http://dbpedia.org/resource/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?website
        WHERE {{
        ?course ns1:courseAt dbp:Concordia_University;
        ns1:hasCourseCode "{tracker.slots['courseName']}"; 
        ns1:hasCourseNumber "{tracker.slots['courseNumber']}";
        rdfs:seeAlso ?website.
        FILTER(?website != "No website provided" && ?website != "Contact faculty member directly to inquire about potential openings for a student working in the lab.")
        }}
        """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        message = "The resources are:\n"
        for result in results["results"]["bindings"]:
            message += f'- {result["website"]["value"]}\n'

        dispatcher.utter_message(text=message)

        return []
