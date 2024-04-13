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
