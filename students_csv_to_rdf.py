import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import FOAF, RDF, RDFS, XSD

# define rdf namespaces
ex = Namespace("http://example.org/")
dbp = Namespace("http://dbpedia.org/resource/")

# constants
UNIVERSITY = dbp.Concordia_University

# read the csv file
df = pd.read_csv('data/students.csv')

# create an empty graph
g = Graph()

# define rdf schema
g.add((ex.Student, RDF.type, RDFS.Class))          # student class
g.add((ex.hasId, RDF.type, RDF.Property))          # id property
g.add((ex.hasFirstName, RDF.type, RDF.Property))   # first name property
g.add((ex.hasLastName, RDF.type, RDF.Property))    # last name property
g.add((ex.isEnrolled, RDF.type, RDF.Property))     # enrolled property
g.add((ex.studiesAt, RDF.type, RDF.Property))      # studies at property

g.add((ex.Course, RDF.type, RDFS.Class))           # course class
g.add((ex.hasCourseCode, RDF.type, RDF.Property))  # code property
g.add((ex.courseAt, RDF.type, RDF.Property))       # course at what school property

g.add((ex.Grade, RDF.type, RDFS.Class))            # grade class
g.add((ex.hasGradeVal, RDF.type, RDF.Property))    # value property
g.add((ex.gradeOf, RDF.type, RDF.Property))        # grade of whom property
g.add((ex.gradeFor, RDF.type, RDF.Property))       # grade for what property

g.add((UNIVERSITY, RDF.type, RDFS.Class))      # concordia university class

# define relationships between classes
g.add((ex.studiesAt, RDFS.domain, ex.Student))     # student studies at a university
g.add((ex.studiesAt, RDFS.range, UNIVERSITY))

g.add((ex.courseAt, RDFS.domain, ex.Course))       # course is at a university
g.add((ex.courseAt, RDFS.range, UNIVERSITY))

g.add((ex.isEnrolled, RDFS.domain, ex.Student))    # student is enrolled in a course
g.add((ex.isEnrolled, RDFS.range, ex.Course))

g.add((ex.gradeOf, RDFS.domain, ex.Grade))         # grade of a student
g.add((ex.gradeOf, RDFS.range, ex.Student))

g.add((ex.gradeFor, RDFS.domain, ex.Grade))        # grade for a course
g.add((ex.gradeFor, RDFS.range, ex.Course))

# function to add attributes to a student
def add_attributes_to_student(id, first_name, last_name, courses, grades):
    student_uri = URIRef(ex + str(id))                              # create a URI for the student
    g.add((student_uri, RDF.type, ex.Student))                      # specify that the URI is a student
    g.add((student_uri, ex.studiesAt, UNIVERSITY))              # specify that the student studies at concordia
    g.add((student_uri, ex.hasId, Literal(id)))                     # add the id 
    g.add((student_uri, ex.hasFirstName, Literal(first_name)))      # add the first name
    g.add((student_uri, ex.hasLastName, Literal(last_name)))        # add the last name

    courses = courses.split(", ")                                   # split the courses into a list
    grades  = grades.split(", ")                                    # split the grades into a list

    for course, grade in zip(courses, grades):
        course_uri = URIRef(ex + course)                            # create a URI for the course
        g.add((course_uri, RDF.type, ex.Course))                    # specify that the URI is a course
        g.add((course_uri, ex.courseAt, UNIVERSITY))            # specify that the course is at concordia
        g.add((course_uri, ex.hasCourseCode, Literal(course)))      # add the course code
        g.add((student_uri, ex.isEnrolled, course_uri))             # enroll the student in the course

        grade_uri = URIRef(ex + str(id) + "-" + course)             # create a URI for the grade
        g.add((grade_uri, RDF.type, ex.Grade))                      # specify that the URI is a grade
        g.add((grade_uri, ex.hasGradeVal, Literal(grade)))          # add the grade value
        g.add((grade_uri, ex.gradeOf, student_uri))                 # specify that the grade is of the student
        g.add((grade_uri, ex.gradeFor, course_uri))                 # specify that the grade is for the course

# convert the dataframe to rdf
for index, row in df.iterrows():
    add_attributes_to_student(row['id'], row['first_name'], row['last_name'], row['courses'], row['grades'])

# save the graph
g.serialize(destination="graphs/students.ttl", format="turtle") 