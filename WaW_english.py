import nltk
from nltk.corpus import wordnet as wn
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

# Function to extract WordNet word pairs
def extract_word_pairs():
    pairs = []
    # Iterate through all synsets
    for synset in list(wn.all_synsets()):
        # Get the main lemma (similar to head_word in IndoWordNet)
        word = synset.lemmas()[0].name().lower()
        
        # Collect similar words from various relations
        similar_words = set()
        
        # Similar words (like SIMILAR relation in IndoWordNet)
        for similar in synset.similar_tos():
            similar_words.add(similar.lemmas()[0].name().lower())
            
        # Hypernyms (equivalent to HYPERNYMY in IndoWordNet)
        for hypernym in synset.hypernyms():
            similar_words.add(hypernym.lemmas()[0].name().lower())
            
        # Hyponyms (equivalent to HYPONYMY in IndoWordNet)
        for hyponym in synset.hyponyms():
            similar_words.add(hyponym.lemmas()[0].name().lower())
        
        # Add word pairs to the list
        for similar_word in similar_words:
            pairs.append((word, similar_word))
            
    return pairs

def create_tsv_with_presence_check(corpus_file, output_OOV_file, output_IOV_file, output_common_file):
    corpus_word_set = load_corpus_as_set(corpus_file)
    word_pairs = extract_word_pairs()
    
    unique_positive_pairs = set()  # does not contain reverse
    unique_positive_pairs_IOV = set()  # does not contain reverse
    unique_positive_pairs_OOV = set()  # does not contain reverse
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
    
    # Process word pairs
    for word, word_b in word_pairs:
        if (word in corpus_word_set and word_b in corpus_word_set) \
            and "_" not in word and "-" not in word and " " not in word \
            and "_" not in word_b and "-" not in word_b and " " not in word_b \
            and word != word_b:
            # IOV pairs
            positive_pairs_IOV.add((word, word_b))
            unique_positive_pairs_IOV.add((word, word_b))
            positive_pairs_IOV.add((word_b, word))  # reverse
            word_pos_neighbors_IOV[word].add(word_b)
            word_pos_neighbors_IOV[word_b].add(word)  # reverse
            
            all_words_IOV.add(word)
            all_words_IOV.add(word_b)
            
        elif (word not in corpus_word_set and word_b not in corpus_word_set) \
            and "_" not in word and "-" not in word and " " not in word \
            and "_" not in word_b and "-" not in word_b and " " not in word_b \
            and word != word_b:
            # OOV pairs
            positive_pairs_OOV.add((word, word_b))
            unique_positive_pairs_OOV.add((word, word_b))
            positive_pairs_OOV.add((word_b, word))
            word_pos_neighbors_OOV[word].add(word_b)
            word_pos_neighbors_OOV[word_b].add(word)
            
            all_words_OOV.add(word)
            all_words_OOV.add(word_b)
        
        if "_" not in word and "-" not in word and " " not in word \
            and "_" not in word_b and "-" not in word_b and " " not in word_b \
            and word != word_b:
            # Common pairs
            positive_pairs.add((word, word_b))
            unique_positive_pairs.add((word, word_b))
            positive_pairs.add((word_b, word))
            word_pos_neighbors[word].add(word_b)
            word_pos_neighbors[word_b].add(word)
            
            all_words.add(word)
            all_words.add(word_b)
    
    all_words = list(all_words)
    all_words_OOV = list(all_words_OOV)
    all_words_IOV = list(all_words_IOV)
    required_negative_samples = len(unique_positive_pairs)
    required_negative_samples_OOV = len(unique_positive_pairs_OOV)
    required_negative_samples_IOV = len(unique_positive_pairs_IOV)
    
    def is_valid_negative_pair(word1, word2, check_type='common'):
        # Select appropriate positive pairs and neighbors based on check type
        pos_pairs = positive_pairs if check_type == 'common' else \
                   positive_pairs_IOV if check_type == 'iov' else \
                   positive_pairs_OOV
        neighbors = word_pos_neighbors if check_type == 'common' else \
                   word_pos_neighbors_IOV if check_type == 'iov' else \
                   word_pos_neighbors_OOV
        
        # Check if this pair or its reverse is not already positive
        if (word1, word2) in pos_pairs or (word2, word1) in pos_pairs:
            return False
        
        # Check if words share any neighbors
        if neighbors[word1] & neighbors[word2]:
            return False
        
        # Additional WordNet-based checks
        word1_synsets = wn.synsets(word1)
        word2_synsets = wn.synsets(word2)
        
        for s1 in word1_synsets:
            for s2 in word2_synsets:
                # Check if they share any hypernym
                hyper1 = set(s1.hypernyms())
                hyper2 = set(s2.hypernyms())
                if hyper1 & hyper2:
                    return False
                
                # Check for entailment
                if s2 in s1.entailments():
                    return False
        
        return True
    
    # Write common pairs
    with open(output_common_file, 'w', newline='', encoding='utf-8') as common_file:
        tsv_writer = csv.writer(common_file, delimiter='\t')
        tsv_writer.writerow(['index', 'word_a', 'word_b', 'label'])
        
        index = 0
        for (word_a, word_b) in unique_positive_pairs:
            tsv_writer.writerow([index, word_a, word_b, 1])
            index += 1
        
        attempt_count = 0
        max_attempts = required_negative_samples * 10
        
        while len(negative_pairs) < required_negative_samples and attempt_count < max_attempts:
            word1 = random.choice(all_words)
            word2 = random.choice(all_words)
            
            if word1 != word2 and is_valid_negative_pair(word1, word2, 'common'):
                negative_pairs.add((word1, word2))
                tsv_writer.writerow([index, word1, word2, 0])
                index += 1
            
            attempt_count += 1
    
    # Write IOV pairs
    with open(output_IOV_file, 'w', newline='', encoding='utf-8') as iov_file:
        tsv_writer = csv.writer(iov_file, delimiter='\t')
        tsv_writer.writerow(['index', 'word_a', 'word_b', 'label'])
        
        index = 0
        for (word_a, word_b) in unique_positive_pairs_IOV:
            tsv_writer.writerow([index, word_a, word_b, 1])
            index += 1
        
        attempt_count = 0
        max_attempts = required_negative_samples_IOV * 10
        
        while len(negative_pairs_IOV) < required_negative_samples_IOV and attempt_count < max_attempts:
            word1 = random.choice(all_words_IOV)
            word2 = random.choice(all_words_IOV)
            
            if word1 != word2 and is_valid_negative_pair(word1, word2, 'iov'):
                negative_pairs_IOV.add((word1, word2))
                tsv_writer.writerow([index, word1, word2, 0])
                index += 1
            
            attempt_count += 1
    
    # Write OOV pairs
    with open(output_OOV_file, 'w', newline='', encoding='utf-8') as oov_file:
        tsv_writer = csv.writer(oov_file, delimiter='\t')
        tsv_writer.writerow(['index', 'word_a', 'word_b', 'label'])
        
        index = 0
        for (word_a, word_b) in unique_positive_pairs_OOV:
            tsv_writer.writerow([index, word_a, word_b, 1])
            index += 1
        
        attempt_count = 0
        max_attempts = required_negative_samples_OOV * 10
        
        while len(negative_pairs_OOV) < required_negative_samples_OOV and attempt_count < max_attempts:
            word1 = random.choice(all_words_OOV)
            word2 = random.choice(all_words_OOV)
            
            if word1 != word2 and is_valid_negative_pair(word1, word2, 'oov'):
                negative_pairs_OOV.add((word1, word2))
                tsv_writer.writerow([index, word1, word2, 0])
                index += 1
            
            attempt_count += 1

LANG = "en"
LANG_FULL = "english"
corpus_file = f'/media/saketh/New Volume/NAACL 2025/Datasets/{LANG}/{LANG}_10M_splits.txt'  # 4GB large corpus file
output_OOV_file = f'{LANG_FULL}/WaW_{LANG}_OOV.tsv'
output_IOV_file = f'{LANG_FULL}/WaW_{LANG}_IOV.tsv'
output_common_file = f'{LANG_FULL}/WaW_{LANG}_all.tsv'

# Download required NLTK data
nltk.download('wordnet')

# Create the TSV files
create_tsv_with_presence_check(corpus_file, output_OOV_file, output_IOV_file, output_common_file)