import pandas as pd
import random
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

# define rdf namespaces
ex = Namespace("http://example.org/")
dbp = Namespace("http://dbpedia.org/resource/")

# constants
UNIVERSITY = dbp.Concordia_University