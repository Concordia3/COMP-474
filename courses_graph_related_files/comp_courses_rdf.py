from tools_libs import *
from topics_excavator.topics_excavator import topics_excavator


def comp_courses_rdf(courses_path, courses_graph_path, nlp_model, cs_concepts):
    # load the courses graph
    courses_graph = Graph()
    courses_graph.parse(courses_graph_path, format='turtle')

    # iterate over the courses graph and extract the classes
    course_class = None
    syllabus_class = None
    lecture_class = None
    worksheet_class = None
    for s, p, o in courses_graph.triples((None, RDF.type, RDFS.Class)):
        if s == ex.Course:
            course_class = s
        elif s == ex.Syllabus:
            syllabus_class = s
        elif s == ex.Lecture:
            lecture_class = s
        elif s == ex.Worksheet:
            worksheet_class = s

    # find comp 472, 474
    comp_472 = None
    comp_474 = None
    for course_uri, _, _ in courses_graph.triples((None, ex.hasCourseCode, Literal('COMP'))):
        # this goes through all the comp courses

        for _, _, course_number in courses_graph.triples((course_uri, ex.hasCourseNumber, None)):
            # this goes thorugh all the comp courses and their course numbers

            if course_number == Literal('472'):
                comp_472 = course_uri
            elif course_number == Literal('474'):
                comp_474 = course_uri

    # iterate over the courses graph and extract the needed properties
    content_for = None
    content_link = None
    content_name = None
    content_topic = None
    content_number = None
    for s, p, o in courses_graph.triples((None, RDF.type, RDF.Property)):
        if s == ex.contentFor:
            content_for = s
        elif s == ex.contentLink:
            content_link = s
        elif s == ex.contentName:
            content_name = s
        elif s == ex.contentTopic:
            content_topic = s
        elif s == ex.contentNumber:
            content_number = s

    # initialize the comp courses graph
    comp_courses_graph = Graph()

    courses = courses_path
    for course in sorted(os.listdir(courses)):
        course_path = os.path.join(courses, course)

        if course == 'comp_472' or course == 'comp_474':
            comp_course = None
            if course == 'comp_472':
                comp_course = comp_472
            elif course == 'comp_474':
                comp_course = comp_474

            for content_type in sorted(os.listdir(course_path)):
                content_type_path = os.path.join(course_path, content_type)

                if content_type == 'lectures':
                    lecture_uris = []
                    count = 1
                    for lecture in sorted(os.listdir(content_type_path)):
                        lecture_path = os.path.join(content_type_path, lecture)

                        lecture_uri = URIRef(comp_course + '/' + content_type + '/' + lecture)
                        lecture_uris.append(lecture_uri)

                        comp_courses_graph.add((lecture_uri, RDF.type, lecture_class))
                        comp_courses_graph.add((lecture_uri, content_for, comp_course))
                        comp_courses_graph.add((lecture_uri, content_link, Literal(lecture_path)))
                        comp_courses_graph.add((lecture_uri, content_name, Literal(lecture)))

                        # extracting topics from the pdf file
                        topics = topics_excavator(lecture_path, nlp_model, cs_concepts)

                        # add the topics to the graph
                        for topic in topics:
                            topic_name = topic[0].replace(' ', '_')
                            comp_courses_graph.add((lecture_uri, content_topic, ex[topic_name]))

                        comp_courses_graph.add((lecture_uri, content_number, Literal(count)))
                        comp_courses_graph.add((comp_course, ex.contains, lecture_uri))

                        count += 1

                elif content_type == 'worksheets':
                    count = 1
                    for worksheet in sorted(os.listdir(content_type_path)):
                        worksheet_path = os.path.join(content_type_path, worksheet)

                        worksheet_uri = URIRef(comp_course + '/' + content_type + '/' + worksheet)
                        comp_courses_graph.add((worksheet_uri, RDF.type, worksheet_class))

                        comp_courses_graph.add((worksheet_uri, content_for, comp_course))
                        comp_courses_graph.add((worksheet_uri, content_link, Literal(worksheet_path)))
                        comp_courses_graph.add((worksheet_uri, content_name, Literal(worksheet)))

                        # extracting topics from the pdf file
                        topics = topics_excavator(worksheet_path, nlp_model, cs_concepts)

                        # add the topics to the graph
                        for topic in topics:
                            topic_name = topic[0].replace(' ', '_')
                            comp_courses_graph.add((worksheet_uri, content_topic, ex[topic_name]))

                        comp_courses_graph.add((worksheet_uri, content_number, Literal(count)))
                        comp_courses_graph.add((comp_course, ex.contains, worksheet_uri))

                        count += 1

                elif content_type == 'syllabus.pdf':

                    syllabus_path = os.path.join(course_path, content_type)

                    syllabus_uri = URIRef(comp_course + '/' + content_type)
                    comp_courses_graph.add((syllabus_uri, RDF.type, syllabus_class))

                    comp_courses_graph.add((syllabus_uri, content_for, comp_course))
                    comp_courses_graph.add((syllabus_uri, content_link, Literal(syllabus_path)))
                    comp_courses_graph.add((syllabus_uri, content_name, Literal(content_type)))

                    # extracting topics from the pdf file
                    topics = topics_excavator(syllabus_path, nlp_model, cs_concepts)

                    # add the topics to the graph
                    for topic in topics:
                        topic_name = topic[0].replace(' ', '_')
                        comp_courses_graph.add((syllabus_uri, content_topic, ex[topic_name]))

                    comp_courses_graph.add((syllabus_uri, content_number, Literal(1)))
                    comp_courses_graph.add((comp_course, ex.contains, syllabus_uri))

    return comp_courses_graph
