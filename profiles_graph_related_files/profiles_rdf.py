from tools_libs import *

def profiles_rdf(df, courses_graph_path, comp_courses_graph_path):
    # load the courses graph
    courses_graph = Graph()
    courses_graph.parse(courses_graph_path, format='turtle')

    # load the comp courses graph
    comp_courses_graph = Graph()
    comp_courses_graph.parse(comp_courses_graph_path, format='turtle')

    # iterate over the courses graph and extract the classes
    course_class    = None
    for s, p, o in courses_graph.triples((None, RDF.type, RDFS.Class)):
        if   s == ex.Course: course_class = s

    # iterate over the comp courses graph and extract the skills
    comp_472_skills = []
    comp_474_skills = []
    for s, p, o in comp_courses_graph.triples((None, RDF.type, ex.Syllabus)):
        if s == ex['COMP' + '/' + '472' + '/' + 'syllabus.pdf']:
            for s1, p1, o1 in comp_courses_graph.triples((s, ex.contentTopic, None)):
                comp_472_skills.append(o1)
        elif s == ex['COMP' + '/' + '474' + '/' + 'syllabus.pdf']:
            for s1, p1, o1 in comp_courses_graph.triples((s, ex.contentTopic, None)):
                comp_474_skills.append(o1)

    # create an empty graph
    g = Graph()

    # define rdf schema
    g.add((ex.Student, RDF.type, RDFS.Class))          # student class
    g.add((ex.hasId, RDF.type, RDF.Property))          # id property
    g.add((ex.isEnrolled, RDF.type, RDF.Property))     # enrolled property
    g.add((ex.studiesAt, RDF.type, RDF.Property))      # studies at property
    g.add((ex.hasSkill, RDF.type, RDF.Property))       # skills property

    g.add((ex.Grade, RDF.type, RDFS.Class))            # grade class
    g.add((ex.hasGradeVal, RDF.type, RDF.Property))    # value property
    g.add((ex.gradeStatus, RDF.type, RDF.Property))    # grade status property
    g.add((ex.gradeOf, RDF.type, RDF.Property))        # grade of whom property
    g.add((ex.gradeFor, RDF.type, RDF.Property))       # grade for what course property

    # define relationships between classes
    g.add((ex.studiesAt, RDFS.domain, ex.Student))     # student studies at a university
    g.add((ex.studiesAt, RDFS.range, UNIVERSITY))

    g.add((ex.isEnrolled, RDFS.domain, ex.Student))    # student is enrolled in a course
    g.add((ex.isEnrolled, RDFS.range, course_class))

    g.add((ex.gradeOf, RDFS.domain, ex.Grade))         # grade of a student
    g.add((ex.gradeOf, RDFS.range, ex.Student))

    g.add((ex.gradeFor, RDFS.domain, ex.Grade))        # grade for a course
    g.add((ex.gradeFor, RDFS.range, course_class))

    # convert the dataframe to rdf
    for index, row in df.iterrows():
        id = row['id']
        first_name = row['first_name']
        last_name = row['last_name']
        email = row['email']
        courses = row['courses']
        grades = row['grades']

        student_uri = URIRef(ex + str(id))                                                      # create a URI for the student

        g.add((student_uri, RDF.type, ex.Student))                                              # specify that the URI is a student
        g.add((student_uri, ex.studiesAt, UNIVERSITY))                                          # specify that the student studies at concordia
        g.add((student_uri, ex.hasId, Literal(id)))                                             # add the id 
        g.add((student_uri, FOAF.firstName, Literal(first_name)))                               # add the first name
        g.add((student_uri, FOAF.lastName, Literal(last_name)))                                 # add the last name
        g.add((student_uri, FOAF.mbox, Literal(email)))                                         # add the email

        courses = ast.literal_eval(courses)                                                     # convert the string to a list
        grades  = ast.literal_eval(grades)                                                      # convert the string to a dictionary

        for course_code, course_number in courses:
            course_uri = URIRef(ex + course_code + '/' + course_number)                         # create a URI for the course

            g.add((course_uri, RDF.type, course_class))                                         # specify that the URI is a course
            g.add((student_uri, ex.isEnrolled, course_uri))                                     # specify that the student is enrolled in the course

            if (course_code, course_number) in grades:
                grades_per_course = grades[(course_code, course_number)]                        # get the grade(s) for the course

                counter = 0
                for grade in grades_per_course:
                    counter += 1

                    grade_uri = URIRef(course_uri + '/' + str(id) + '/' + str(counter))         # create a URI for the grade

                    if grade < 60: 
                        g.add((grade_uri, ex.gradeStatus, Literal('F')))                        # grade < 60 is a fail
                    else: 
                        g.add((grade_uri, ex.gradeStatus, Literal('P')))                        # otherwise, it's a pass
                        if course_code == 'COMP' and course_number == '472':                    # if the course is COMP 472
                            for skill in comp_472_skills:
                                g.add((student_uri, ex.hasSkill, skill))                        # add the skills to the student
                        elif course_code == 'COMP' and course_number == '474':                  # if the course is COMP 474
                            for skill in comp_474_skills:
                                g.add((student_uri, ex.hasSkill, skill))                        # add the skills to the student

                    g.add((grade_uri, RDF.type, ex.Grade))                                      # specify that the URI is a grade
                    g.add((grade_uri, ex.hasGradeVal, Literal(grade, datatype=XSD.integer)))    # add the grade value
                    g.add((grade_uri, ex.gradeOf, student_uri))                                 # specify that the grade is of the student
                    g.add((grade_uri, ex.gradeFor, course_uri))                                 # specify that the grade is for the course

                    if counter > 1: g.add((grade_uri, RDFS.comment, Literal('Retake grade')))   # add a comment if the grade is a re-exam
                    else          : g.add((grade_uri, RDFS.comment, Literal('')))

    return g