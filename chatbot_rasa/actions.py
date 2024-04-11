from SPARQLWrapper import SPARQLWrapper, JSON
from rasa_sdk import Action


class QueryFusekiServer(Action):
    def name(self):
        return "action_query_fuseki_server"

    def run(self, dispatcher, tracker, domain):
        query_type = tracker.get_slot("query_type")

        if query_type == "list_all_courses":
            query = self.build_sparql_query_list_all_courses()
        elif query_type == "courses_discussing_topic":
            topic = tracker.get_slot("topic")
            query = self.build_sparql_query_courses_discussing_topic(topic)
        elif query_type == "course_description":
            course_code = tracker.get_slot("course_code")
            query = self.build_sparql_query_course_description(course_code)
        elif query_type == "topics_covered_in_course_event":
            course_code = tracker.get_slot("course_code")
            course_event = tracker.get_slot("course_event")
            query = self.build_sparql_query_topics_covered_in_course_event(course_code, course_event)
        elif query_type == "course_events_covering_topic":
            topic = tracker.get_slot("topic")
            query = self.build_sparql_query_course_events_covering_topic(topic)

        # Connect to the Fuseki server
        sparql = SPARQLWrapper("http://your-fuseki-server-endpoint")

        # Set the SPARQL query and request JSON results
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)

        # Execute the query and process the results
        results = sparql.query().convert()

        # Process the results based on the query type
        if query_type == "list_all_courses" or query_type == "courses_discussing_topic":
            course_list = self.process_sparql_results(results)
            self.send_response(dispatcher, course_list)
        elif query_type == "course_description":
            description = self.extract_course_description(results)
            dispatcher.utter_message(f"The description of the course is: {description}")
        elif query_type == "topics_covered_in_course_event":
            topics = self.extract_topics_covered_in_course_event(results)
            self.send_topics_response(dispatcher, topics)
        elif query_type == "course_events_covering_topic":
            courses_events = self.extract_course_events_covering_topic(results)
            self.send_course_events_response(dispatcher, courses_events)
        # Add more elif clauses for other query types

        return []

    # Methods to build SPARQL queries for different query types

    # Methods to process SPARQL query results for different query types

    def send_response(self, dispatcher, course_list):
        """
        Sends the response containing the course information to the user.
        """
        dispatcher.utter_message("Here are the results:")
        for course in course_list:
            dispatcher.utter_message(f"Course: {course['course_name']}\nDescription: {course['description']}\n")

    def extract_course_description(self, results):
        """
        Extracts the course description from the SPARQL query results.
        """
        # Implement logic to extract course description from results
        # Return the course description
        return "Course description"

    def send_topics_response(self, dispatcher, topics):
        """
        Sends the response containing the topics covered in a course event to the user.
        """
        # Implement logic to format and send the response
        pass

    def extract_topics_covered_in_course_event(self, results):
        """
        Extracts the topics covered in a course event from the SPARQL query results.
        """
        # Implement logic to extract topics covered in course event
        # Return the topics with their resource URIs
        return [("Topic 1", "Resource URI 1"), ("Topic 2", "Resource URI 2")]

    def send_course_events_response(self, dispatcher, courses_events):
        """
        Sends the response containing the course events covering a topic to the user.
        """
        # Implement logic to format and send the response
        pass

    def extract_course_events_covering_topic(self, results):
        """
        Extracts the course events covering a topic from the SPARQL query results.
        """
        # Implement logic to extract course events covering topic
        # Return the course events
        return [("Course 1", "Event 1"), ("Course 2", "Event 2")]
