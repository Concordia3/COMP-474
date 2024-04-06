from tools_libs import *
from topics_excavator.pdf_reader import pdf_reader
from topics_excavator.compound_words_finder import compound_words_finder
from topics_excavator.custom_entity_recognizer import custom_entity_recognizer
from topics_excavator.custom_word2vec import custom_word2vec

def topics_excavator(course_name, input_filename, input_path, nlp_model, threshold):
    file_name = input_filename

    # conver pdf into text
    text = pdf_reader(input_path)

    # tokenize the text
    tokens = nlp_model(text)

    preprocessed_tokens = nlp_model(' '.join([token.text.replace('- ', '') if ('•' in token.text) else token.text for token in tokens]))

    # find compound words
    compound_words = compound_words_finder(preprocessed_tokens)

    # find entities
    linked_entities = set()
    for compound_word in tqdm((compound_words), desc='Searching', unit='word(s)'):
        linked_entities.add(custom_entity_recognizer(compound_word))

    # find description of the course
    g = Graph()
    g.parse("graphs/courses.ttl", format='turtle')

    course_code   = course_name.split('_')[0].upper()
    course_number = course_name.split('_')[1]
    course_uri    = ex[course_code + '/' + course_number]

    course_desc = ''
    for s, p, o in g.triples((course_uri, None, None)):
        if p == ex['hasDescription']:
            course_desc = str(o)

    course_desc = """
        Scope of AI. First-order logic. Automated reasoning. 
        Search and heuristic search. 
        Game-playing. 
        Planning. 
        Knowledge representation. 
        Probabilistic reasoning. 
        Introduction to machine learning. 
        Introduction to natural language processing. 
        Project. Lectures: three hours per week. 
        Laboratory: two hours per week.
        Prerequisite: COMP 352 or COEN 352.
    """

    # tokenize the course description
    course_desc_tokens = nlp_model((course_desc))

    # find compound words in the course description
    course_desc_compound_words = " ".join(compound_words_finder(course_desc_tokens))

    # convert the course description compound words into a word vector
    course_desc_word_vectors = np.mean([token.vector for token in nlp_model(course_desc_compound_words) if token.has_vector],
                                        axis=0)

    # convert the compound words of the syllabus into a word vector
    labels, urls, syllabus_word_vectors = custom_word2vec(nlp_model, linked_entities)

    # find the cosine similarity between the 2 vectors (both need to be 2d)
    similarities = cosine_similarity([course_desc_word_vectors], 
                                     syllabus_word_vectors)[0]

    # set a threshold for the similarity
    threshold = threshold

    # filter out the similarities that are above the threshold
    extracted_topics = []
    for i, similarity in enumerate(similarities):
        if similarity > threshold:
            extracted_topics.append((course_name, file_name, labels[i], urls[i]))

    return extracted_topics