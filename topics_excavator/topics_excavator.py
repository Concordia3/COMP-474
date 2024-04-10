from tools_libs import *
from topics_excavator.pdf_reader import pdf_reader
from topics_excavator.search_wikidata import search_wikidata

def topics_excavator(file_path, nlp_model, comp_concepts):
    """
    file_path: str, path to the pdf file
    nlp_model: spacy model, the language model
    comp_concepts: set, the comp concepts
    topics: list, the topics extracted from the pdf file and their URIs
    """
    # read pdf file
    text = pdf_reader(file_path)

    # tokenize the text
    doc = nlp_model(text)

    # remove bullet points
    preprocessed_doc = nlp_model(' '.join([token.text.replace('•', '')for token in doc]))

    # extract chunks and remove stop words, spaces, and punctuations
    noun_chunks = set()
    for chunk in preprocessed_doc.noun_chunks:
        cleaned_chunk = []
        for token in chunk:
            # if the token is not a stop word, space, or punctuation, add it to the cleaned chunk
            if not (token.is_stop or token.is_space or token.is_punct):
                cleaned_chunk.append(token.text)
        if cleaned_chunk:
            noun_chunks.add(' '.join(cleaned_chunk).lower())

    # extract common terms between the extracted chunks and the comp concepts
    common_terms = list(noun_chunks.intersection(comp_concepts))

    # search wikidata for the topics
    topics = []
    for term in common_terms:
        result = search_wikidata(term)
        if result['search']:
            topics.append((term, result['search'][0]['concepturi']))

    return topics