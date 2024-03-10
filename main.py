from rdflib import Graph

# create 2 empty graphs
university_g = Graph()
students_g   = Graph()

# parse the rdf files
university_g.parse("graphs/university.ttl", format="ttl")
students_g.parse("graphs/students.ttl", format="ttl")

# merge the graphs
merged_g = university_g + students_g

# save merged graph
merged_g.serialize(destination="graphs/merged.ttl", format="turtle")