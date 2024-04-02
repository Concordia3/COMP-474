def compound_words_finder(tokens):
    # initialize a set to store compound words
    compound_words = set()

    # iterate over the tokens in the document
    for token in tokens:
        compound_word = ''

        # check if the token and its head form a compound word
        if token.dep_ == "compound":
            # construct the compound word by joining the token and its head
            compound_word += token.text

            # Iterate over the children of the token to form the complete compound word
            child = token

            while child.dep_ == "compound":
                compound_word += ' ' + child.head.text  # add the head of the compound word
                child = child.head

            # Add the compound word to the list
            compound_words.add(compound_word)

        # check if the token is an appositive (a noun that renames another noun or noun phrase)
        if token.dep_ == "appos":
            compound_words.add(token)

    return compound_words