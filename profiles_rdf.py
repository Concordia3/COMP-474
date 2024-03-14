from tools_libs import *

# load courses graph
courses_graph = Graph()
courses_graph.parse("graphs/courses.ttl", format="turtle")

# iterate over the courses graph and extract the course class
course_class = None
for s, p, o in courses_graph.triples((None, RDF.type, None)):
    if o == RDFS.Class:
        course_class = s

# read the csv file
df = pd.read_csv('data/students/profiles.csv')

# create an empty graph
g = Graph()

# define rdf schema
g.add((ex.Student, RDF.type, RDFS.Class))          # student class
g.add((ex.hasId, RDF.type, RDF.Property))          # id property
g.add((ex.isEnrolled, RDF.type, RDF.Property))     # enrolled property
g.add((ex.studiesAt, RDF.type, RDF.Property))      # studies at property

g.add((ex.Grade, RDF.type, RDFS.Class))            # grade class
g.add((ex.hasGradeVal, RDF.type, RDF.Property))    # value property
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

# function to add attributes to a student
def add_attributes_to_student(id, first_name, last_name, email, courses, grades):
    student_uri = URIRef(ex + str(id))                                              # create a URI for the student

    g.add((student_uri, RDF.type, ex.Student))                                      # specify that the URI is a student
    g.add((student_uri, ex.studiesAt, UNIVERSITY))                                  # specify that the student studies at concordia
    g.add((student_uri, ex.hasId, Literal(id)))                                     # add the id 
    g.add((student_uri, FOAF.firstName, Literal(first_name)))                       # add the first name
    g.add((student_uri, FOAF.lastName, Literal(last_name)))                         # add the last name
    g.add((student_uri, FOAF.mbox, Literal(email)))                                 # add the email

    courses = ast.literal_eval(courses)                                             # convert the string to a list
    grades  = ast.literal_eval(grades)                                              # convert the string to a dictionary

    for course_code, course_number in courses:
        course_uri = URIRef(ex + course_code + '/' + course_number)                 # create a URI for the course

        g.add((course_uri, RDF.type, course_class))                                    # specify that the URI is a course

        if (course_code, course_number) in grades:
            grades_per_course = grades[(course_code, course_number)]                # get the grade(s) for the course

            counter = 0
            for grade in grades_per_course:
                counter += 1

                grade_uri = URIRef(course_uri + '/' + str(id) + '/' + str(counter)) # create a URI for the grade
                g.add((grade_uri, RDF.type, ex.Grade))                              # specify that the URI is a grade
                g.add((grade_uri, ex.hasGradeVal, Literal(grade)))                  # add the grade value
                g.add((grade_uri, ex.gradeOf, student_uri))                         # specify that the grade is of the student
                g.add((grade_uri, ex.gradeFor, course_uri))                         # specify that the grade is for the course

# convert the dataframe to rdf
for index, row in df.iterrows():
    add_attributes_to_student(row['id'], row['first_name'], row['last_name'], row['email'], row['courses'], row['grades'])

# save the graph
g.serialize(destination="graphs/profiles.ttl", format="turtle") 