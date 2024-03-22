# Roboprof :robot: (Work-in-Progess)


## [Preamble](#preamble-section)
The project involves building "Roboprof" :robot: an intelligent agent capable of answering university course- and student-related questions using a knowledge graph and natural language processing. In this first phase, the focus is on constructing the knowledge base. Subsequent phases will refine the base with enhancements, develop the natural language processing interface, and integrate all components into a cohesive system. 


## [File Organization](file-organization-section)
data ---------------> contains raw courses data and csv files generated from code
            |
            |-------> courses --------> contains info on courses that are offered at Concordia in csv format along with course materials for COMP472 and COMP474
            |
            |-------> students -------> contains info on students attending Concordia (randomly generated)
            
graphs -------------> contains graph outputs from code

instructions -------> contains project instructions


## [Execution](execution-section)
To install rdflib in your Python environment, run:
``` 
pip install rdflib
```

To generate students, courses rdf graphs, and ultimately, the final graph (i.e. `university.ttl`)that encompasses both courses and students graphs, run:
``` 
python main.py
```
