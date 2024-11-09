import pyiwn
import csv
from collections import defaultdict
import random

# Function to read the large corpus and create a set of words
def load_corpus_as_set(corpus_file):
    word_set = set()
    with open(corpus_file, 'r', encoding='utf-8') as file:
        for line in file:
            # Assuming each line contains space-separated words
            words = line.strip().split()
            word_set.update(words)
    return word_set

# Function to extract WordNet word-definition pairs
def extract_word_definition_pairs():
    synsets = iwn.all_synsets()
    pairs = []
    # Iterate through each synset
    for synset in synsets:
        pairs.append((synset.head_word(), synset.gloss(), synset))

    return pairs


def create_tsv_with_presence_check(corpus_file, output_OOV_file, output_IOV_file, output_common_file):
    corpus_word_set = load_corpus_as_set(corpus_file)

    word_def_pairs = extract_word_definition_pairs()

    unique_positive_pairs = set() # does not contain reverse
    unique_positive_pairs_IOV = set() # does not contain reverse
    unique_positive_pairs_OOV = set() # does not contain reverse
    positive_pairs = set()
    positive_pairs_OOV = set()
    positive_pairs_IOV = set()
    word_pos_neighbors = defaultdict(set)
    word_pos_neighbors_OOV = defaultdict(set)
    word_pos_neighbors_IOV = defaultdict(set)
    all_words = set()
    all_words_OOV = set()
    all_words_IOV = set()
    negative_pairs = set()
    negative_pairs_OOV = set()
    negative_pairs_IOV = set()


    for index, (word, definition, synset) in enumerate(word_def_pairs):

        similars = iwn.synset_relation(synset, pyiwn.SynsetRelations.SIMILAR)
        hypernyms = iwn.synset_relation(synset, pyiwn.SynsetRelations.HYPERNYMY)
        hyponyms = iwn.synset_relation(synset, pyiwn.SynsetRelations.HYPONYMY)
        similar_words_list = []
        for similar in similars:
            similar_words_list.append(similar.head_word())
        for hypernym in hypernyms:
            similar_words_list.append(hypernym.head_word())
        for hyponym in hyponyms:
            similar_words_list.append(hyponym.head_word())

        if len(similar_words_list) > 0:
            for word_b in similar_words_list:
                if (word in corpus_word_set and word_b in corpus_word_set) \
                    and "_" not in word and "-" not in word and " " not in word \
                    and "_" not in word_b and "-" not in word_b and " " not in word_b \
                    and word != word_b:
                    # go into IOV since both are in vocabulary
                    positive_pairs_IOV.add((word, word_b))
                    unique_positive_pairs_IOV.add((word, word_b))
                    positive_pairs_IOV.add((word_b, word)) # reverse
                    word_pos_neighbors_IOV[word].update([word_b])
                    word_pos_neighbors_IOV[word_b].update([word]) # reverse

                    all_words_IOV.add(word)
                    all_words_IOV.update([word_b])

                elif (word not in corpus_word_set and word_b not in corpus_word_set) \
                    and "_" not in word and "-" not in word and "_" not in word_b \
                    and "-" not in word_b and " " not in word and " " not in word_b \
                    and word != word_b:
                    # go into OOV
                    positive_pairs_OOV.add((word, word_b))
                    unique_positive_pairs_OOV.add((word, word_b))
                    positive_pairs_OOV.add((word_b, word))
                    word_pos_neighbors_OOV[word].update([word_b])
                    word_pos_neighbors_OOV[word_b].update([word])

                    all_words_OOV.add(word)
                    all_words_OOV.update([word_b])

                if "_" not in word and "-" not in word and " " not in word and "_" not in word_b \
                    and "-" not in word_b and " " not in word_b \
                    and word != word_b:
                    # go into common
                    positive_pairs.add((word, word_b))
                    unique_positive_pairs.add((word, word_b))
                    positive_pairs.add((word_b, word)) # add reverse direction also
                    word_pos_neighbors[word].update(similar_words_list)
                    word_pos_neighbors[word_b].update([word])

                    all_words.add(word)
                    all_words.update([word_b])
        
    all_words = list(all_words)
    all_words_OOV = list(all_words_OOV)
    all_words_IOV = list(all_words_IOV)
    required_negative_samples = len(unique_positive_pairs)
    required_negative_samples_OOV = len(unique_positive_pairs_OOV)
    required_negative_sampels_IOV = len(unique_positive_pairs_IOV)

    def is_valid_negative_pair(word1, word2):
        # Check if this pair or its reverse is not already positive
        if (word1, word2) in positive_pairs or (word2, word1) in positive_pairs:
            return False
            
        # Check if words share any neighbors (indirect relationship)
        if word_pos_neighbors[word1] & word_pos_neighbors[word2]:
            return False
            
        # Additional WordNet-based checks
        word1_synsets = iwn.synsets(word1)
        word2_synsets = iwn.synsets(word2)
        
        for s1 in word1_synsets:
            for s2 in word2_synsets:
                # Check if they share any hypernym
                hyper1 = set(iwn.synset_relation(s1, pyiwn.SynsetRelations.HYPERNYMY))
                hyper2 = set(iwn.synset_relation(s2, pyiwn.SynsetRelations.HYPERNYMY))
                if hyper1 & hyper2:
                    return False
                
                # Check for other semantic relationships
                if s2 in iwn.synset_relation(s1, pyiwn.SynsetRelations.ENTAILMENT):
                    return False
        
        return True
    
    def is_valid_negative_pair_IOV(word1, word2):
        # Check if this pair or its reverse is not already positive
        if (word1, word2) in positive_pairs_IOV or (word2, word1) in positive_pairs_IOV:
            return False
            
        # Check if words share any neighbors (indirect relationship)
        if word_pos_neighbors_IOV[word1] & word_pos_neighbors_IOV[word2]:
            return False
            
        # Additional WordNet-based checks
        word1_synsets = iwn.synsets(word1)
        word2_synsets = iwn.synsets(word2)
        
        for s1 in word1_synsets:
            for s2 in word2_synsets:
                # Check if they share any hypernym
                hyper1 = set(iwn.synset_relation(s1, pyiwn.SynsetRelations.HYPERNYMY))
                hyper2 = set(iwn.synset_relation(s2, pyiwn.SynsetRelations.HYPERNYMY))
                if hyper1 & hyper2:
                    return False
                
                # Check for other semantic relationships
                if s2 in iwn.synset_relation(s1, pyiwn.SynsetRelations.ENTAILMENT):
                    return False
        
        return True
    
    def is_valid_negative_pair_OOV(word1, word2):
        # Check if this pair or its reverse is not already positive
        if (word1, word2) in positive_pairs_OOV or (word2, word1) in positive_pairs_OOV:
            return False
            
        # Check if words share any neighbors (indirect relationship)
        if word_pos_neighbors_OOV[word1] & word_pos_neighbors_OOV[word2]:
            return False
            
        # Additional WordNet-based checks
        word1_synsets = iwn.synsets(word1)
        word2_synsets = iwn.synsets(word2)
        
        for s1 in word1_synsets:
            for s2 in word2_synsets:
                # Check if they share any hypernym
                hyper1 = set(iwn.synset_relation(s1, pyiwn.SynsetRelations.HYPERNYMY))
                hyper2 = set(iwn.synset_relation(s2, pyiwn.SynsetRelations.HYPERNYMY))
                if hyper1 & hyper2:
                    return False
                
                # Check for other semantic relationships
                if s2 in iwn.synset_relation(s1, pyiwn.SynsetRelations.ENTAILMENT):
                    return False
        
        return True
    
    # Common
    with open(output_common_file, 'w', newline='', encoding='utf-8') as common_file:
        tsv_writer = csv.writer(common_file, delimiter='\t')
        tsv_writer.writerow(['index', 'word_a', 'word_b', 'label'])

        index = 0
        for (word_a, word_b) in unique_positive_pairs:
            tsv_writer.writerow([index, word_a, word_b, 1])
            index += 1

        attempt_count = 0
        max_attempts = required_negative_samples * 10 # limit attempts to avoid infinite loops

        while len(negative_pairs) < required_negative_samples and attempt_count < max_attempts:
            word1 = random.choice(all_words)
            word2 = random.choice(all_words)

            if word1 != word2 and is_valid_negative_pair(word1, word2):
                negative_pairs.add((word1, word2))
                tsv_writer.writerow([index, word1, word2, 0])
                index += 1

            attempt_count += 1
        
        if len(negative_pairs) < required_negative_samples:
            print(f"Warning: Could only generate {len(negative_pairs)} negative sampels out of {required_negative_samples} requested")
            

    # IOV
    with open(output_IOV_file, 'w', newline='', encoding='utf-8') as iov_file:
        tsv_writer = csv.writer(iov_file, delimiter='\t')
        tsv_writer.writerow(['index', 'word_a', 'word_b', 'label'])

        index = 0
        for (word_a, word_b) in unique_positive_pairs_IOV:
            tsv_writer.writerow([index, word_a, word_b, 1])
            index += 1

        attempt_count = 0
        max_attempts = required_negative_sampels_IOV * 10 # limit attempts to avoid infinite loops

        while len(negative_pairs_IOV) < required_negative_sampels_IOV and attempt_count < max_attempts:
            word1 = random.choice(all_words_IOV)
            word2 = random.choice(all_words_IOV)

            if word1 != word2 and is_valid_negative_pair_IOV(word1, word2):
                negative_pairs_IOV.add((word1, word2))
                tsv_writer.writerow([index, word1, word2, 0])
                index += 1

            attempt_count += 1
        
        if len(negative_pairs_IOV) < required_negative_sampels_IOV:
            print(f"Warning: Could only generate {len(negative_pairs_IOV)} negative sampels out of {required_negative_sampels_IOV} requested")


    # OOV
    with open(output_OOV_file, 'w', newline='', encoding='utf-8') as oov_file:
        tsv_writer = csv.writer(oov_file, delimiter='\t')
        tsv_writer.writerow(['index', 'word_a', 'word_b', 'label'])

        index = 0
        for (word_a, word_b) in unique_positive_pairs_OOV:
            tsv_writer.writerow([index, word_a, word_b, 1])
            index += 1

        attempt_count = 0
        max_attempts = required_negative_samples_OOV * 10 # limit attempts to avoid infinite loops

        while len(negative_pairs_OOV) < required_negative_samples_OOV and attempt_count < max_attempts:
            word1 = random.choice(all_words_OOV)
            word2 = random.choice(all_words_OOV)

            if word1 != word2 and is_valid_negative_pair_OOV(word1, word2):
                negative_pairs_OOV.add((word1, word2))
                tsv_writer.writerow([index, word1, word2, 0])
                index += 1

            attempt_count += 1
        
        if len(negative_pairs_OOV) < required_negative_samples_OOV:
            print(f"Warning: Could only generate {len(negative_pairs_OOV)} negative sampels out of {required_negative_samples_OOV} requested")



LANG = "hi"
LANG_FULL = "hindi"
corpus_file = f'/media/saketh/New Volume/NAACL 2025/Datasets/{LANG}/{LANG}_10M_splits.txt'  # 4GB large corpus file
output_OOV_file = f'{LANG_FULL}/WaW_{LANG}_OOV.tsv'
output_IOV_file = f'{LANG_FULL}/WaW_{LANG}_IOV.tsv'
output_common_file = f'{LANG_FULL}/WaW_{LANG}_all.tsv'

iwn = pyiwn.IndoWordNet(lang=pyiwn.Language.HINDI)

# Create the TSV file
create_tsv_with_presence_check(corpus_file, output_OOV_file, output_IOV_file, output_common_file)