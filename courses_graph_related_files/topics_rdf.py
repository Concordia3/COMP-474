from tools_libs import *
from topics_excavator.search_wikidata import search_wikidata

def topics_rdf(comp_courses_graph_path):
    comp_courses_graph = Graph()
    comp_courses_graph.parse(comp_courses_graph_path, format='turtle')

    # extract all the topics from the comp courses graph
    topics = []
    for s, p, o in comp_courses_graph.triples((None, ex.contentTopic, None)):
        topics.append(o)

    # initialize the topics graph
    topics_graph = Graph()

    topics_graph.add((ex.Topic, RDF.type, RDFS.Class))
    topics_graph.add((ex.hasConceptURI, RDF.type, RDF.Property))

    for topic in topics:
        topic_name = topic.split('/')[-1].replace('_', ' ')

        result = search_wikidata(topic_name)
        if result['search']:
            topics_graph.add((topic, RDF.type, ex.Topic))
            topics_graph.add((topic, RDFS.label, Literal(topic_name)))
            topics_graph.add((topic, ex.hasConceptURI, Literal(result['search'][0]['concepturi'])))

    return topics_graph
