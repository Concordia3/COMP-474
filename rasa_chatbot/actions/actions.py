from typing import Any, Text, Dict, List

from rasa_sdk import Action
from SPARQLWrapper import SPARQLWrapper, JSON
from rasa_sdk.events import SlotSet
import re


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

        if not results["results"]["bindings"]:
            message = f"There are no courses found."
        else:
            message = "Here are all the courses offered at Concordia University:\n"
            for result in results["results"]["bindings"]:
                # Extract course code and number from the URL
                course_url = result["course"]["value"]
                course_code = course_url.split("/")[-2]  # Extract the second last part of the URL
                course_number = course_url.split("/")[-1]  # Extract the last part of the URL
                message += f'- {course_code} {course_number}\n'

        dispatcher.utter_message(text=message)

        return []


import re


class DiscussedTopic(Action):
    def name(self):
        return "action_discussed_topic"

    def run(self, dispatcher, tracker, domain):
        subject = tracker.get_slot('subject')

        sparql = SPARQLWrapper("http://localhost:3030/concordia/query")
        sparql.setQuery(f"""
            PREFIX ns1: <http://example.org/>

            SELECT ?courseTitle
            WHERE {{
              ?course a ns1:Course;
                      ns1:hasTitle ?courseTitle;
                      ns1:hasDescription ?description.
              FILTER regex(?description, "{subject}", "i").
            }}
        """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        if not results["results"]["bindings"]:
            message = f"There are no courses where the mentioned topic is explicitly discussed."
        else:
            message = f"The courses in which {subject} is discussed are:\n"
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

        if not results["results"]["bindings"]:
            message = "No topics found."
        else:
            message = f"The topics discussed in {courseName} {courseNumber} during lecture {lecture} are:\n"
            for result in results["results"]["bindings"]:
                topic_url = result["topic"]["value"]
                topic_name = topic_url.split("/")[-1]
                message += f'- {topic_name}\n'

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

        if not results["results"]["bindings"]:  # Check if any results exist
            message = f"There are no courses within the '{courseName}' subject."
        else:
            message = f"The courses within the '{courseName}' subject are:\n"
            for result in results["results"]["bindings"]:
                # Extract course code and number from the URL
                course_url = result["course"]["value"]
                course_code = course_url.split("/")[-2]  # Extract the second last part of the URL
                course_number = course_url.split("/")[-1]  # Extract the last part of the URL
                message += f'- {course_code} {course_number}\n'

        dispatcher.utter_message(text=message)

        return []


class RecommendedMaterials(Action):
    def name(self):
        return "action_recommended_materials"

    def run(self, dispatcher, tracker, domain):
        courseName = tracker.get_slot('courseName')
        courseNumber = tracker.get_slot('courseNumber')
        discussedTopic = tracker.get_slot('discussedTopic')

        if courseName is None:
            courseName = ''
        if courseNumber is None:
            courseNumber = 0
        if discussedTopic is None:
            topic = ''

        sparql = SPARQLWrapper("http://localhost:3030/concordia/query")
        sparql.setQuery(f"""
        PREFIX ns1: <http://example.org/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?materialType ?materialName ?materialLink
        WHERE {{
          ?topic rdfs:label "{discussedTopic}" .
          ?lecture a ns1:Lecture ;
                   ns1:contentFor <http://example.org/{courseName}/{courseNumber}> ;
                   ns1:contentTopic ?topic ;
                   ns1:contentName ?materialName ;
                   ns1:contentLink ?materialLink .
          BIND("slides" AS ?materialType) .
        }}
        """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        if not results["results"]["bindings"]:  # Check if any results exist
            message = f"No materials found."
        else:
            message = f"The recommended materials for {discussedTopic} in {courseName} {courseNumber} are:\n"
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

        if not results["results"]["bindings"]:  # Check if any results exist
            message = f"{courseName} {courseNumber} not found."
        else:
            for result in results["results"]["bindings"]:
                credit_value = float(result["credits"]["value"])

            message = f"{courseName} {courseNumber} is worth {credit_value} credits."

        dispatcher.utter_message(text=message)

        return []


class AdditionalResources(Action):
    def name(self):
        return "action_additional_resources"

    def run(self, dispatcher, tracker, domain):
        courseName = tracker.get_slot('courseName')
        courseNumber = tracker.get_slot('courseNumber')

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

        if not results["results"]["bindings"]:  # Check if any results exist
            message = f"No additional resources found for {courseName} {courseNumber}."
        else:
            message = f"The additional resources for {courseName} {courseNumber} are:\n"
            for result in results["results"]["bindings"]:
                message += f'- {result["website"]["value"]}\n'

        dispatcher.utter_message(text=message)

        return []


class ContentDetails(Action):
    def name(self):
        return "action_content_details"

    def run(self, dispatcher, tracker, domain):
        courseName = tracker.get_slot('courseName')
        courseNumber = int(tracker.get_slot('courseNumber'))
        lecture = int(tracker.get_slot('lecture'))

        sparql = SPARQLWrapper("http://localhost:3030/concordia/query")
        sparql.setQuery(f"""
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX ns2: <http://ogp.me/ns#video:>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                PREFIX ns1: <http://example.org/>
                PREFIX dbp: <http://dbpedia.org/resource/>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    
                SELECT ?course_code ?course_number ?course_file ?file_type ?file_path ?file_name ?week
                WHERE {{
                    {{ 
                      SELECT ?course
                      WHERE {{
                        ?course ns1:hasCourseCode "{courseName}";
                                ns1:hasCourseNumber ?course_number.
                        FILTER(?course_number = "{courseNumber}")	
                      }}
                    }}
    
                    # extract course code, number, and all the files associated with it
                    ?course ns1:hasCourseCode ?course_code;
                            ns1:hasCourseNumber ?course_number;
                            ns1:contains ?course_file.
    
                    # details of the files
                    ?course_file rdf:type ?file_type;
                                 ns1:contentLink ?file_path;
                                 ns1:contentName ?file_name;
                                 ns1:contentNumber ?week.
                    FILTER(?week = {lecture} && ?course_number = '{courseNumber}')
    
                }}
                ORDER BY ?course_code ?course_number ?week
                """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        print("Results:", results)

        if not results["results"]["bindings"]:  # Check if any results exist
            message = f"No content found for {courseName} {courseNumber}."
        else:
            message = f"Here are the requested contents for {courseName} {courseNumber}:\n"
            for result in results["results"]["bindings"]:
                url = result["file_type"]["value"]
                file = url.split("/")[-1]
                message += f"- Week: {result['week']['value']}, File Type: {file}, File Name: {result.get('file_name', {}).get('value', 'N/A')}, File Path: {result.get('file_path', {}).get('value', 'N/A')}\n"

        dispatcher.utter_message(text=message)

        return []


class ReadingMaterial(Action):
    def name(self):
        return "action_reading_material"

    def run(self, dispatcher, tracker, domain):
        courseName = tracker.get_slot('courseName')
        courseNumber = int(tracker.get_slot('courseNumber'))
        discussedTopic = tracker.get_slot('discussedTopic')

        sparql = SPARQLWrapper("http://localhost:3030/concordia/query")
        sparql.setQuery(f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX ns1: <http://example.org/>

        SELECT ?materialName ?materialLink  ?worksheetName ?worksheetLink
        WHERE {{
          ?topic rdfs:label "{discussedTopic}" .
          ?lecture a ns1:Lecture ;
                   ns1:contentFor <http://example.org/{courseName}/{courseNumber}> ;
                   ns1:contentTopic ?topic ;
                   ns1:contentNumber ?lectureNumber ;
                   ns1:contentName ?materialName ;
                   ns1:contentLink ?materialLink .
          OPTIONAL {{
            ?worksheet a ns1:Worksheet ;
                       ns1:contentFor <http://example.org/{courseName}/{courseNumber}> ;
                       ns1:contentNumber ?worksheetNumber ;
                       ns1:contentName ?worksheetName ;
                       ns1:contentLink ?worksheetLink .
            FILTER (?worksheetNumber = (?lectureNumber - 1))
          }}
        }}
        """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        if not results["results"]["bindings"]:  # Check if any results exist
            message = f"No reading materials available for {courseName} {courseNumber}."
        else:
            message = f"The following reading materials are recommended for {discussedTopic}:\n"
            for result in results["results"]["bindings"]:
                # Access values from the dictionary
                material_name = result.get('materialName', {}).get('value', 'N/A')
                material_link = result.get('materialLink', {}).get('value', 'N/A')
                worksheet_name = result.get('worksheetName', {}).get('value', 'N/A')
                worksheet_link = result.get('worksheetLink', {}).get('value', 'N/A')

                # Update the message with correct variable names
                message += f"- Material Name: {material_name}; Link to material: {material_link}\n"
                message += f"- Worksheet name: {worksheet_name}; Link to worksheet: {worksheet_link}\n"

        dispatcher.utter_message(text=message)

        return []

    class GainedCompetencies(Action):
        def name(self):
            return "action_gained_competencies"

        def run(self, dispatcher, tracker, domain):
            courseName = tracker.get_slot('courseName')
            courseNumber = int(tracker.get_slot('courseNumber'))

            sparql = SPARQLWrapper("http://localhost:3030/concordia/query")
            sparql.setQuery(f"""
            PREFIX ns1: <http://example.org/>
    
            SELECT DISTINCT ?topic
            WHERE {{
              ?lecture a ns1:Lecture ;
                       ns1:contentFor <http://example.org/{courseName}/{courseNumber}> ;
                       ns1:contentTopic ?topic .
            }}
            """)

            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            if not results["results"]["bindings"]:
                message = "No competency information found."
            else:
                message = f"The competencies gained after completing {courseName} {courseNumber} are:\n"
                for result in results["results"]["bindings"]:
                    topic_url = result["topic"]["value"]
                    topic_name = topic_url.split("/")[-1]
                    message += f'- {topic_name}\n'

            dispatcher.utter_message(text=message)

            return []


class StudentGrade(Action):
    def name(self):
        return "action_student_grade"

    def run(self, dispatcher, tracker, domain):
        courseName = tracker.get_slot('courseName')
        courseNumber = int(tracker.get_slot('courseNumber'))
        studentFirstName = tracker.get_slot('studentFirstName')
        studentLastName = tracker.get_slot('studentLastName')

        sparql = SPARQLWrapper("http://localhost:3030/concordia/query")
        sparql.setQuery(f"""
        PREFIX ns2: <http://ogp.me/ns#video:>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX ns1: <http://example.org/>
        PREFIX dbp: <http://dbpedia.org/resource/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>

        SELECT ?id ?first_name ?last_name ?course_code ?course_number ?course_title ?course_desc ?course_credits ?course_website ?grade_val ?grade_status ?grade_comment
        WHERE {{
          ?student ns1:hasId ?id;
                   foaf:firstName "{studentFirstName}";
                   foaf:lastName "{studentLastName}".

          # get his grades
          ?grade ns1:gradeOf ?student;
                 ns1:gradeFor ?course;
                 ns1:hasGradeVal ?grade_val;
                 ns1:gradeStatus ?grade_status;
                 rdfs:comment ?grade_comment.

          ?course ns1:hasCourseCode "{courseName}";
                  ns1:hasCourseNumber "{courseNumber}";
                  ns1:hasTitle ?course_title;
                  ns1:hasDescription ?course_desc;
                  ns1:hasCredits ?course_credits;
                  rdfs:seeAlso ?course_website.
        }}
        ORDER BY ?grade
        """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        if not results["results"]["bindings"]:
            message = f"No grade found."
        else:
            for result in results["results"]["bindings"]:
                grade = float(result["grade_val"]["value"])

            message = f"{studentFirstName}'s grade in {courseName} {courseNumber} is: {grade}%\n"

        dispatcher.utter_message(text=message)

        return []


class StudentsCompletedCourse(Action):
    def name(self):
        return "action_students_completed_course"

    def run(self, dispatcher, tracker, domain):
        courseName = tracker.get_slot('courseName')
        courseNumber = int(tracker.get_slot('courseNumber'))

        sparql = SPARQLWrapper("http://localhost:3030/concordia/query")
        sparql.setQuery(f"""
        PREFIX ns1: <http://example.org/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>

        SELECT ?id ?first_name ?last_name ?course_code ?course_number ?grade_val ?grade_status 
        WHERE {{
          ?grade ns1:gradeOf ?student; 
                 ns1:gradeFor ?course;
                 ns1:hasGradeVal ?grade_val;
                 ns1:gradeStatus ?grade_status.

          ?student ns1:hasId ?id;
                   foaf:firstName ?first_name;
                   foaf:lastName ?last_name.

          # Filter the grades by course
          ?course ns1:hasCourseCode "{courseName}";
                  ns1:hasCourseNumber "{courseNumber}".

          # Filter only passed grades
          FILTER(?grade_status = "P")
        }}
        """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        if not results["results"]["bindings"]:
            message = f"No students have completed {courseName} {courseNumber}."
        else:
            message = f"The students who have completed {courseName} {courseNumber} are:\n"
            for result in results["results"]["bindings"]:
                firstName = result.get('first_name', {}).get('value', 'N/A')
                lastName = result.get('last_name', {}).get('value', 'N/A')
                message += f'{firstName} {lastName}\n'

        dispatcher.utter_message(text=message)

        return []


class PrintTranscript(Action):
    def name(self):
        return "action_print_transcript"

    def run(self, dispatcher, tracker, domain):
        studentFirstName = tracker.get_slot('studentFirstName')
        studentLastName = tracker.get_slot('studentLastName')

        sparql = SPARQLWrapper("http://localhost:3030/concordia/query")
        sparql.setQuery(f"""
        PREFIX ns2: <http://ogp.me/ns#video:>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX ns1: <http://example.org/>
        PREFIX dbp: <http://dbpedia.org/resource/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        
        SELECT ?id ?first_name ?last_name ?course_code ?course_number ?course_title ?course_desc ?course_credits ?course_website ?grade_val ?grade_status
        WHERE {{
          # get the random student's info 
          ?student ns1:hasId ?id;
                   foaf:firstName "{studentFirstName}";
                   foaf:lastName "{studentLastName}".
        
          # get his grades
          ?grade ns1:gradeOf ?student;
                 ns1:gradeFor ?course;
                 ns1:hasGradeVal ?grade_val;
                 ns1:gradeStatus ?grade_status.
        
          # get his courses
          ?course ns1:hasCourseCode ?course_code;
                  ns1:hasCourseNumber ?course_number;
                  ns1:hasTitle ?course_title;
                  ns1:hasDescription ?course_desc;
                  ns1:hasCredits ?course_credits;
                  rdfs:seeAlso ?course_website.
        }}
        """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        if not results["results"]["bindings"]:
            message = f"Student does not exist and/or no transcript available."
        else:
            message = f"Here is the transcript for {studentFirstName} {studentLastName}:\n"
            for result in results["results"]["bindings"]:
                # Access values from the dictionary
                id = float(result["id"]["value"])
                firstName = result.get('first_name', {}).get('value', 'N/A')
                lastName = result.get('last_name', {}).get('value', 'N/A')
                course_code = result.get('course_code', {}).get('value', 'N/A')
                course_number = int(result["course_number"]["value"])
                course_desc = result.get('course_desc', {}).get('value', 'N/A')
                course_credits = float(result["course_credits"]["value"])
                website = result.get('course_website', {}).get('value', 'N/A')
                grade = float(result["grade_val"]["value"])
                grade_status = result.get('grade_status', {}).get('value', 'N/A')
                message += (f'------------------------------------------------\n'
                            f'Course: {course_code}, {course_number}\n'
                            f'Course description: {course_desc}\n'
                            f'Website: {website}\n'
                            f'Grade: {grade}\n'
                            f'Pass/Fail: {grade_status}\n'
                            f'------------------------------------------------')

        dispatcher.utter_message(text=message)

        return []


class AboutCourse(Action):
    def name(self):
        return "action_about_course"

    def run(self, dispatcher, tracker, domain):
        courseName = tracker.get_slot('courseName')
        courseNumber = int(tracker.get_slot('courseNumber'))

        sparql = SPARQLWrapper("http://localhost:3030/concordia/query")
        sparql.setQuery(f"""
        PREFIX ns1: <http://example.org/>

        SELECT ?courseDescription
        WHERE {{
          ?course ns1:hasCourseCode "{courseName}" ;
                  ns1:hasCourseNumber "{courseNumber}" ;
                  ns1:hasDescription ?courseDescription .
        }}
        """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        if not results["results"]["bindings"]:
            message = f"No course description available for {courseName} {courseNumber}."
        else:
            message = f"Here is the course description for {courseName} {courseNumber}:\n"
            for result in results["results"]["bindings"]:
                courseDescription = result.get('courseDescription', {}).get('value', 'N/A')
                message += f'- {courseDescription}.\n'

        dispatcher.utter_message(text=message)

        return []


class CoveredTopics(Action):
    def name(self):
        return "action_covered_topics"

    def run(self, dispatcher, tracker, domain):
        courseName = tracker.get_slot('courseName')
        courseNumber = int(tracker.get_slot('courseNumber'))
        lecture = int(tracker.get_slot('lecture'))
        courseEvent = tracker.get_slot('courseEvent')

        # Adjust lecture variable based on courseEvent
        if courseEvent.lower() == 'lab' or courseEvent.lower() == 'tutorial':
            lecture -= 1

        sparql = SPARQLWrapper("http://localhost:3030/concordia/query")

        sparql.setQuery(f"""
        PREFIX ns1: <http://example.org/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?topic_label ?conceptURI
        WHERE {{
          ?course ns1:hasCourseCode "{courseName}" ;
                  ns1:hasCourseNumber "{courseNumber}" .
          ?lecture ns1:contentFor ?course ;
                   ns1:contentNumber {lecture} ;
                   ns1:contentTopic ?topic .
          ?topic rdfs:label ?topic_label ;
                 ns1:hasConceptURI ?conceptURI .
        }}
        """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        if not results["results"]["bindings"]:
            message = f"No topics found."
        else:
            message = f"The topics covered are:\n"
            for result in results["results"]["bindings"]:
                topic_label = result.get('topic_label', {}).get('value', 'N/A')
                conceptURI = result.get('conceptURI', {}).get('value', 'N/A')
                message += f'{topic_label} - URI: {conceptURI}\n'

        dispatcher.utter_message(text=message)

        return []


class EventCoversTopic(Action):
    def name(self):
        return "action_event_covers_topic"

    def run(self, dispatcher, tracker, domain):
        discussedTopic = tracker.get_slot('discussedTopic')

        sparql = SPARQLWrapper("http://localhost:3030/concordia/query")
        sparql.setQuery(f"""
        PREFIX ns1: <http://example.org/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?course ?event (COUNT(?event) as ?frequency)
        WHERE {{
          ?topic rdfs:label "{discussedTopic}" .

          ?course ns1:hasCourseCode ?course_code ;
                  ns1:hasCourseNumber ?course_number .
          ?event ns1:contentTopic ?topic ;
                 ns1:contentFor ?course .
        }}
        GROUP BY ?course ?event
        ORDER BY DESC(?frequency)
        """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        if not results["results"]["bindings"]:
            message = f"No course events found."
        else:
            message = f"The events that cover {discussedTopic} are:\n"
            for result in results["results"]["bindings"]:
                course_uri = result.get('course', {}).get('value', 'N/A')
                event_uri = result.get('event', {}).get('value', 'N/A')

                course_code = course_uri.split('/')[-1].split('_')[0]
                event_name = event_uri.split('/')[-1]

                message += f'{course_code}: {event_name}\n'

        dispatcher.utter_message(text=message)

        return []
