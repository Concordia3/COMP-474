import pandas as pd
import ast
import os
import random
import spacy
import numpy as np
import torch
import requests
import csv
import json

from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
from rdflib import Graph, Namespace, URIRef, Literal, XSD
from rdflib.namespace import RDF, RDFS, FOAF

# initialize language model
nlp = spacy.load("en_core_web_lg")

# set of cs concepts that will be used to filter out the topics
with open('topics_excavator/cs_concepts.json') as file:
    data = json.load(file)
cs_concepts = set(data['cs_concepts'])

# define rdf namespaces
ex = Namespace("http://example.org/")
dbp = Namespace("http://dbpedia.org/resource/")

# constants
UNIVERSITY = dbp.Concordia_University