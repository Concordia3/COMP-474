import pandas as pd
import random
import ast
import os

from rdflib import Graph, Namespace, URIRef, Literal, XSD
from rdflib.namespace import RDF, RDFS, FOAF

# define rdf namespaces
ex = Namespace("http://example.org/")
dbp = Namespace("http://dbpedia.org/resource/")

# constants
UNIVERSITY = dbp.Concordia_University