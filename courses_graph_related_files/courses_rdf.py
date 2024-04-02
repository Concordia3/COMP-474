from tools_libs import *

def courses_rdf(df):
    # create RDF graph
    g = Graph()

    # define RDF schema
    g.add((ex.Course, RDF.type, RDFS.Class))                # course class
    g.add((ex.hasCourseCode, RDF.type, RDF.Property))       # subject property
    g.add((ex.hasCourseNumber, RDF.type, RDF.Property))     # catalog property
    g.add((ex.hasTitle, RDF.type, RDF.Property))            # title property
    g.add((ex.hasCredits, RDF.type, RDF.Property))          # credits property
    g.add((ex.hasDescription, RDF.type, RDF.Property))      # description property
    g.add((ex.contains, RDF.type, RDF.Property))            # contains property

    # define private RDF schema
    g.add((ex.Syllabus, RDF.type, RDFS.Class))              # syllabus class
    g.add((ex.Syllabus, RDFS.subClassOf, ex.Course))

    g.add((ex.Lecture, RDF.type, RDFS.Class))               # slides subclass of course class
    g.add((ex.Lecture, RDFS.subClassOf, ex.Course))

    g.add((ex.Worksheet, RDF.type, RDFS.Class))             # worksheet subclass of course class
    g.add((ex.Worksheet, RDFS.subClassOf, ex.Course))
    g.add((ex.associatedWith, RDF.type, RDF.Property))      # associated lecture property

    # define common RDF schema
    g.add((ex.contentFor, RDF.type, RDF.Property))          # content for what class property 
    g.add((ex.contentLink, RDF.type, RDF.Property))         # content link property
    g.add((ex.contentName, RDF.type, RDF.Property))         # content name property
    g.add((ex.topic, RDF.type, RDF.Property))               # topic property
    g.add((ex.contentNumber, RDF.type, RDF.Property))       # content number property

    # define relationships between classes
    g.add((ex.courseAt, RDFS.domain, ex.Course))            # course is at a university
    g.add((ex.courseAt, RDFS.range, UNIVERSITY))

    g.add((ex.associatedWith, RDFS.domain, ex.Worksheet))   # worksheet is associated with a lecture
    g.add((ex.associatedWith, RDFS.range, ex.Lecture))

    # Convert selected data to RDF
    for index, row in df.iterrows():
        subject = URIRef(ex + row['Course code'] + '/' + row['Course number'])

        # current subject is of course class
        g.add((subject, RDF.type, ex.Course))

        # add properties
        g.add((subject, ex.courseAt, UNIVERSITY))
        g.add((subject, ex.hasCourseCode, Literal(row['Course code'])))
        g.add((subject, ex.hasCourseNumber, Literal(row['Course number'])))
        g.add((subject, ex.hasTitle, Literal(row['Long Title'])))
        g.add((subject, ex.hasCredits, Literal(row['Class Units'], datatype=XSD.float)))
        g.add((subject, ex.hasDescription, Literal(row['Descr'])))
        g.add((subject, RDFS.seeAlso, Literal(row['Website'])))

    return g