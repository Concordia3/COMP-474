import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import FOAF, RDF, RDFS, XSD

# define rdf namespaces
ex = Namespace("http://example.org/")

# read the csv file
df = pd.read_csv('students.csv')

# create an empty graph
g = Graph()

# define rdf schema
g.add((ex.Student, RDF.type, RDFS.Class))          # student class
g.add((ex.hasId, RDF.type, RDF.Property))          # id property
g.add((ex.hasFirstName, RDF.type, RDF.Property))   # first name property
g.add((ex.hasLastName, RDF.type, RDF.Property))    # last name property
g.add((ex.hasGrade, RDF.type, RDF.Property))       # grade property
g.add((ex.isEnrolled, RDF.type, RDF.Property))     # enrolled property
g.add((ex.studiesAt, RDF.type, RDF.Property))      # studies at property

# function to add attributes to a student
def add_attributes_to_student(id, first_name, last_name, courses, grades):
    student_uri = URIRef(ex + str(id))                              # create a URI for the student

    g.add((student_uri, RDF.type, ex.Student))                      # specify that the URI is a student
    g.add((student_uri, ex.hasId, Literal(id)))                     # add the id 
    g.add((student_uri, ex.hasFirstName, Literal(first_name)))      # add the first name
    g.add((student_uri, ex.hasLastName, Literal(last_name)))        # add the last name

    courses = courses.split(", ")                                   # split the courses into a list
    grades = grades.split(", ")                                     # split the grades into a list
    for course, grade in zip(courses, grades) :
        g.add((student_uri, ex.isEnrolled, URIRef(ex + course)))    # add the courses
        g.add((student_uri, ex.hasGrade, Literal(grade)))           # add the grades

# convert the dataframe to rdf
for index, row in df.iterrows():
    add_attributes_to_student(row['id'], row['first_name'], row['last_name'], row['courses'], row['grades'])

# Serialize and print the RDF graph
g.serialize(destination="students.ttl", format="turtle")