from tools_libs import *
from courses_rdf import courses_rdf
from transcripts_generator import transcripts_generator
from comp_courses_rdf import comp_courses_rdf
from profiles_generator import profiles_generator
from profiles_rdf import profiles_rdf

import random

# Set the random seed
random.seed(0)

############################################################################################################
# load the raw course csv files                                                                            #
############################################################################################################
# make dfs from the csv files
df_info = pd.read_csv('data/courses/raw_course_info_2024.csv')
df_web  = pd.read_csv('data/courses/raw_course_websites_2024.csv')

# rename column in df_info to match the column name in df_web
df_info.rename(columns={'Subject': 'Course code', 'Catalog': 'Course number'}, inplace=True)

# merge the dataframes
merged_df = pd.merge(df_info, df_web, on=['Course code', 'Course number'], how='inner')

# replace NaN values with 'No website provided'
merged_df['Website'] = merged_df['Website'].fillna('No website provided')
merged_df['Website'] = merged_df['Website'].replace(" ", 'No website provided')

# save the merged dataframe
merged_df.to_csv('data/courses/processed_course_info_2024.csv', index=False)

############################################################################################################
# make an rdf graph with processed course csv file                                                          #
############################################################################################################
courses_graph = Graph()

course_graph = courses_rdf(merged_df)

# save the graph
course_graph.serialize(destination="graphs/courses.ttl", format="turtle") 

############################################################################################################
# make an rdf graph with the info provided on COMP 472 and COMP 474                                        #
############################################################################################################
# make the graph
comp_courses_graph = comp_courses_rdf('data/courses','graphs/courses.ttl')

# save the comp courses graph
comp_courses_graph.serialize("graphs/comp_courses.ttl", format="turtle")

############################################################################################################
# randomly generate transcripts based on the courses found in the processed csv above                      #
############################################################################################################
transcripts_df = transcripts_generator('data/courses/processed_course_info_2024.csv', num_students=50)

# convert the df into a csv file
transcripts_df.to_csv('data/students/transcripts.csv', index=False)

############################################################################################################
# generate student profiles with student info and the randomly generated transcripts (50 students)         #
############################################################################################################
profiles_df = profiles_generator('data/students/students.csv', 'data/students/transcripts.csv')

# convert the df into a csv file
profiles_df.to_csv('data/students/profiles.csv', index=False)

############################################################################################################
# make an rdf graph with the student profiles                                                              #
############################################################################################################
profiles_graph = Graph()

profiles_graph = profiles_rdf(profiles_df, 'graphs/courses.ttl')

# save the graph
profiles_graph.serialize(destination="graphs/profiles.ttl", format="turtle")

############################################################################################################
# merge graphs                                                                                             #
############################################################################################################
# merge courses and comp courses graphs
courses_graph = Graph()
courses_graph.parse("graphs/courses.ttl", format='turtle')

comp_courses_graph = Graph()
comp_courses_graph.parse("graphs/comp_courses.ttl", format='turtle')

courses_graph += comp_courses_graph

# merge the courses and profiles graphs
profiles_graph = Graph()
profiles_graph.parse("graphs/profiles.ttl", format='turtle')

university_graph = courses_graph + profiles_graph

# save the final graph
university_graph.serialize(destination="graphs/university.ttl", format="turtle")