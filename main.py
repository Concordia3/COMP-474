import subprocess

############################################################################################################
# pip install the required libraries                                                                       #
############################################################################################################
subprocess.run('pip install -r requirements.txt', shell=True, 
               stdout=subprocess.DEVNULL, 
               stderr=subprocess.STDOUT)

############################################################################################################
# import the required libraries                                                                            #
############################################################################################################
from tools_libs import *
from courses_graph_related_files.courses_rdf import courses_rdf
from profiles_graph_related_files.transcripts_generator import transcripts_generator
from courses_graph_related_files.comp_courses_rdf import comp_courses_rdf
from profiles_graph_related_files.profiles_generator import profiles_generator
from profiles_graph_related_files.profiles_rdf import profiles_rdf
from topics_excavator.topics_excavator import topics_excavator

############################################################################################################
# download the spacy models                                                                                #
############################################################################################################
subprocess.run('python -m spacy download en_core_web_md', 
               shell=True, 
               stdout=subprocess.DEVNULL, 
               stderr=subprocess.STDOUT)
subprocess.run('python -m spacy download en_core_web_lg', 
               shell=True, 
               stdout=subprocess.DEVNULL,
               stderr=subprocess.STDOUT)

############################################################################################################
# load the raw course csv files                                                                            #
############################################################################################################
# make dfs from the csv files
df_info = pd.read_csv('data/courses/raw_course_info_2024.csv')
df_web  = pd.read_csv('data/courses/raw_course_websites_2024.csv')
df_desc = pd.read_csv('data/courses/raw_course_desc_2024.csv')

# rename column in df_info to match the column name in df_web
df_info.rename(columns={'Subject': 'Course code', 'Catalog': 'Course number'}, inplace=True)

# merge the dataframes
merged_df_1 = pd.merge(df_info, df_web, on=['Course code', 'Course number'], how='inner')
merged_df_2 = pd.merge(merged_df_1, df_desc, on=['Course ID'], how='inner')

# replace NaN values with 'No website provided'
merged_df_2['Website'] = merged_df_2['Website'].fillna('No website provided')
merged_df_2['Website'] = merged_df_2['Website'].replace(" ", 'No website provided')

# save the merged dataframe
merged_df_2.to_csv('data/courses/processed_course_info_2024.csv', index=False)

############################################################################################################
# make an rdf graph with processed course csv file                                                          #
############################################################################################################
courses_graph = Graph()

course_graph = courses_rdf(merged_df_2)

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

############################################################################################################
# read pdf files and extract text                                                                          #
############################################################################################################
# initialize language model
nlp = spacy.load("en_core_web_lg")

# extract all entities (topics) from comp472 and comp474 pdf files
data_path = 'data/courses/'

# write the results to a csv file
csv_file = open('topics_excavator/detected_topics.csv', 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Document Name", "Document Path", "Topics", "URIs"])

# set of cs concepts that will be used to filter out the topics
with open('topics_excavator/cs_concepts.json') as file:
    data = json.load(file)
cs_concepts = set(data['cs_concepts'])

# data folder
for folder in os.listdir(data_path):
    folder_path = os.path.join(data_path, folder)

    # if folder is indeed a folder
    if os.path.isdir(folder_path):

        # iterate over the items in the folder
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)

            # syllabus
            if item.endswith('.pdf'):
                topics = topics_excavator(item_path, nlp, cs_concepts)

                for topic in topics:
                    topic_name = topic[0]
                    topic_uri = topic[1]
                    csv_writer.writerow([item, item_path, topic_name, topic_uri])
            
            # if folders (lectures, worksheets, etc.)
            elif os.path.isdir(item_path):

                # iterate over the files in the folder
                for file in os.listdir(item_path):
                    file_path = os.path.join(item_path, file)

                    if file.endswith('.pdf'):
                        topics = topics_excavator(file_path, nlp, cs_concepts)

                        for topic in topics:
                            topic_name = topic[0]
                            topic_uri = topic[1]
                            csv_writer.writerow([file, file_path, topic_name, topic_uri])
csv_file.close()