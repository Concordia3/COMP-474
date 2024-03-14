#   QUICK README

## Steps
0. make sure that you have all the modules in tools_libs.py installed
1. run courses_rdf.py first to make a ttl graph for all the courses that are offered at Concordia
2. run transcripts_generators next -> generate a bunch of random transcripts (the amount must match the number of students)
3. once you have the transcripts, graft them side-by-side with students.csv by running profiles_generator.py -> generate a profiles.csv that contains students and their general info + transcripts

### note: make sure to have a students csv file first before you run step 3 (check my format)

4. next, run profiles_rdf.py to build a graph from profiles.csv
5. finally, run main to merge courses graph and profiles graph together -> university.ttl

## Organization
- data -> contains raw courses data and csv files generated from code
- graphs -> contains graph outputs from code (comp_courses.ttl not done)
- instructions -> contains project instructions