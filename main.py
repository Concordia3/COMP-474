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
from topics_excavator.pdf_reader import pdf_reader
from topics_excavator.compound_words_finder import compound_words_finder
from topics_excavator.custom_entity_recognizer import custom_entity_recognizer
from topics_excavator.custom_word2vec import custom_word2vec

############################################################################################################
# download the spacy models                                                                                #
############################################################################################################
subprocess.run('python -m spacy download en_core_web_md', shell=True, stdout=subprocess.DEVNULL)
subprocess.run('python -m spacy download en_core_web_lg', shell=True, stdout=subprocess.DEVNULL)

# ############################################################################################################
# # load the raw course csv files                                                                            #
# ############################################################################################################
# # make dfs from the csv files
# df_info = pd.read_csv('data/courses/raw_course_info_2024.csv')
# df_web  = pd.read_csv('data/courses/raw_course_websites_2024.csv')
# df_desc = pd.read_csv('data/courses/raw_course_desc_2024.csv')

# # rename column in df_info to match the column name in df_web
# df_info.rename(columns={'Subject': 'Course code', 'Catalog': 'Course number'}, inplace=True)

# # merge the dataframes
# merged_df_1 = pd.merge(df_info, df_web, on=['Course code', 'Course number'], how='inner')
# merged_df_2 = pd.merge(merged_df_1, df_desc, on=['Course ID'], how='inner')

# # replace NaN values with 'No website provided'
# merged_df_2['Website'] = merged_df_2['Website'].fillna('No website provided')
# merged_df_2['Website'] = merged_df_2['Website'].replace(" ", 'No website provided')

# # save the merged dataframe
# merged_df_2.to_csv('data/courses/processed_course_info_2024.csv', index=False)

# ############################################################################################################
# # make an rdf graph with processed course csv file                                                          #
# ############################################################################################################
# courses_graph = Graph()

# course_graph = courses_rdf(merged_df_2)

# # save the graph
# course_graph.serialize(destination="graphs/courses.ttl", format="turtle") 

# ############################################################################################################
# # make an rdf graph with the info provided on COMP 472 and COMP 474                                        #
# ############################################################################################################
# # make the graph
# comp_courses_graph = comp_courses_rdf('data/courses','graphs/courses.ttl')

# # save the comp courses graph
# comp_courses_graph.serialize("graphs/comp_courses.ttl", format="turtle")

# ############################################################################################################
# # randomly generate transcripts based on the courses found in the processed csv above                      #
# ############################################################################################################
# transcripts_df = transcripts_generator('data/courses/processed_course_info_2024.csv', num_students=50)

# # convert the df into a csv file
# transcripts_df.to_csv('data/students/transcripts.csv', index=False)

# ############################################################################################################
# # generate student profiles with student info and the randomly generated transcripts (50 students)         #
# ############################################################################################################
# profiles_df = profiles_generator('data/students/students.csv', 'data/students/transcripts.csv')

# # convert the df into a csv file
# profiles_df.to_csv('data/students/profiles.csv', index=False)

# ############################################################################################################
# # make an rdf graph with the student profiles                                                              #
# ############################################################################################################
# profiles_graph = Graph()

# profiles_graph = profiles_rdf(profiles_df, 'graphs/courses.ttl')

# # save the graph
# profiles_graph.serialize(destination="graphs/profiles.ttl", format="turtle")

# ############################################################################################################
# # merge graphs                                                                                             #
# ############################################################################################################
# # merge courses and comp courses graphs
# courses_graph = Graph()
# courses_graph.parse("graphs/courses.ttl", format='turtle')

# comp_courses_graph = Graph()
# comp_courses_graph.parse("graphs/comp_courses.ttl", format='turtle')

# courses_graph += comp_courses_graph

# # merge the courses and profiles graphs
# profiles_graph = Graph()
# profiles_graph.parse("graphs/profiles.ttl", format='turtle')

# university_graph = courses_graph + profiles_graph

# # save the final graph
# university_graph.serialize(destination="graphs/university.ttl", format="turtle")

############################################################################################################
# read pdf files and extract text                                                                          #
############################################################################################################
# initialize language model
nlp = spacy.load("en_core_web_lg")

# extract all entities (topics) from comp472 and comp474 pdf files
folder_path = 'data/courses/'

csv_file = open('detected_topics.csv', 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Document Name", "Topics", "URIs"])

for filename in os.listdir(folder_path):
    parent_path = os.path.join(folder_path, filename)

    # check if filename is a course directory
    if os.path.isdir(parent_path):
        course_name = filename

        for filename in os.listdir(parent_path):
            child_path = os.path.join(parent_path, filename)

            # check if filename is a pdf file
            if filename.endswith('.pdf'):
                syllabus = filename

                # conver pdf into text
                text = pdf_reader(child_path)

                # tokenize the text
                tokens = nlp(text)

                # find compound words
                compound_words = compound_words_finder(tokens)

                # find entities
                linked_entities = set()
                for compound_word in tqdm((compound_words), desc='Searching', unit='word(s)'):
                    linked_entities.add(custom_entity_recognizer(compound_word))

                # find description of the course
                g = Graph()
                g.parse("graphs/university.ttl", format='turtle')

                course_code   = course_name.split('_')[0]
                course_number = course_name.split('_')[1]

                query = """
                    PREFIX ns2: <http://ogp.me/ns#video:>
                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                    PREFIX ns1: <http://example.org/>
                    PREFIX dbp: <http://dbpedia.org/resource/>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>

                    SELECT ?course_desc 
                    WHERE {
                            ?course ns1:courseAt dbp:Concordia_University;
                            ns1:hasCourseCode ?course_code;
                            ns1:hasCourseNumber ?course_number;
                            ns1:hasDescription ?course_desc.
                            FILTER(LCASE(?course_code) = '%s' && ?course_number = '%s')
                    }
                """ % (course_code, course_number)

                course_desc = str(g.query(query))

                # tokenize the course description
                course_desc_tokens = nlp(course_desc)

                # find compound words in the course description
                course_desc_compound_words = " ".join(compound_words_finder(course_desc_tokens))

                # convert the course description compound words into a word vector
                course_desc_word_vectors = np.mean([token.vector for token in nlp(course_desc_compound_words) if token.has_vector],
                                                    axis=0)

                # convert the compound words of the syllabus into a word vector
                labels, urls, syllabus_word_vectors = custom_word2vec(nlp, linked_entities)

                # find the cosine similarity between the 2 vectors (both need to be 2d)
                similarities = cosine_similarity([course_desc_word_vectors], syllabus_word_vectors)[0]

                # set a threshold for the similarity
                threshold = 0.77

                # filter out the similarities that are above the threshold
                for i, similarity in enumerate(similarities):
                    if similarity > threshold:
                        csv_writer.writerow([course_name, labels[i], urls[i]])