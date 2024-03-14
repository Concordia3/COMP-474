from tools_libs import *

courses_graph = Graph()
profiles_graph = Graph()

# load the graphs
courses_graph.parse("graphs/courses.ttl", format="turtle")
profiles_graph.parse("graphs/profiles.ttl", format="turtle")

# merge the graphs
university_graph = courses_graph + profiles_graph

# save the merged graph
university_graph.serialize(destination="graphs/university.ttl", format="turtle")