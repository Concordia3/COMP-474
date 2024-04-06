from tools_libs import np

def custom_word2vec(nlp_model, custom_linked_entities):
    labels       = []
    urls         = []
    word_vectors = []
    for linked_identity in list(custom_linked_entities):
        label, url, desc = linked_identity

        # Average the word vectors for each description
        tokens = nlp_model(label + ' ' + desc)
        desc_vector = np.mean([token.vector for token in tokens if token.has_vector], axis=0)
        word_vectors.append(desc_vector)

        urls.append(url)
        labels.append(label)

    return labels, urls, word_vectors