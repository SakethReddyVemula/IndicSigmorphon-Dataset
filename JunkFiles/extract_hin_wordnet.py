from iwnlp.iwnlp_wrapper import IWNLPWrapper
import csv

# Initialize the IWNLP Wrapper
iwnlp = IWNLPWrapper()

def extract_hindi_word_definition_pairs():
    word_def_pairs = []

    # Get all synsets from the IndoWordNet
    for synset_id in range(1, iwnlp.get_max_synset_id() + 1):
        # Get the synset information
        synset_info = iwnlp.get_synset_data(synset_id)
        if synset_info and synset_info['language'] == 'hindi':  # Only Hindi synsets
            words = synset_info['lemmas']  # Lemmas (words)
            definition = synset_info.get('gloss', '')  # Definition (if available)
            for word in words:
                word_def_pairs.append((word, definition))
    
    return word_def_pairs

# Get the Hindi word-definition pairs
hindi_pairs = extract_hindi_word_definition_pairs()

# Write the Hindi word-definition pairs to a TSV file
with open('WaD_extract_hindi.tsv', 'w', newline='', encoding='utf-8') as tsv_file:
    tsv_writer = csv.writer(tsv_file, delimiter='\t')

    # Write the header
    tsv_writer.writerow(['index', 'word', 'definition', 'label'])

    # Write the word-definition pairs with index
    for index, (word, definition) in enumerate(hindi_pairs):
        tsv_writer.writerow([index, word, definition, 1])

print("Hindi word-definition pairs written to WaD_extract_hindi.tsv.")
