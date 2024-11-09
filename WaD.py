import pyiwn
import csv
import random
from difflib import SequenceMatcher

def load_corpus_as_set(corpus_file):
    word_set = set()
    with open(corpus_file, 'r', encoding='utf-8') as file:
        for line in file:
            words = line.strip().split()
            word_set.update(words)
    return word_set

def extract_word_definition_pairs():
    synsets = iwn.all_synsets()
    pairs = []
    for synset in synsets:
        if " " not in synset.head_word() and "_" not in synset.head_word():
            pairs.append((synset.head_word(), synset.gloss(), synset))
    return pairs

def create_negative_samples(word_def_pairs):
    words, definitions, _ = zip(*word_def_pairs)
    shuffled_definitions = list(definitions)
    random.shuffle(shuffled_definitions)
    
    negative_pairs = []
    for word, shuffled_def in zip(words, shuffled_definitions):
        negative_pairs.append((word, shuffled_def))
    
    return negative_pairs

def lexical_similarity(word1, word2):
    return SequenceMatcher(None, word1, word2).ratio()

# def select_lexically_similar_negatives(word_def_pairs, negative_pairs, num_samples):
#     selected_negatives = []
#     for index, (word, definition, _) in enumerate(word_def_pairs):
#         if index % 50 == 0:
#             print(f"index: {index}")
#         similarities = [(neg_word, neg_def, lexical_similarity(word, neg_word)) 
#                         for neg_word, neg_def in negative_pairs if neg_word != word]
#         similarities.sort(key=lambda x: x[2], reverse=True)
#         # print(f"-"*90)
#         # print(f"ACTUAL WORD: {word}")
#         # print(f"SIMILAR WORDS: ")
#         # for similar in similarities[:10]:
#         #     print(f"{similar[0]}")
#         # if similarities:
#         #     selected_negatives.append((word, similarities[0][1]))

#         i = 0
#         temperature = 3
#         for i in range(0, len(similarities)):
#             if similarities[i][0] == word:
#                 continue
#             else:
#                 if temperature > 0:
#                     if definition != similarities[i][1]:
#                         temperature -= 1
#                     continue
#                 else:
#                     break
        
#         # Print selected negative sample
#         # print(f"WORD: {word}")
#         # print(f"POS_DEFINITION: {definition}")
#         # print(f"LEXICALLY_SIMILAR_WORD: {similarities[i][0]}")
        
#         neg_sample_idx = i
#         i = 0
#         neg_definition = ""
#         for i in range(0, len(word_def_pairs)):
#             if word_def_pairs[i][0] == similarities[neg_sample_idx][0]:
#                 # print(f"NEG_DEFINITION: {word_def_pairs[i][1]}")
#                 neg_definition = word_def_pairs[i][1]
#                 break

#         selected_negatives.append((word, neg_definition))

        
#         if len(selected_negatives) >= num_samples:
#             break
#         # print(len(selected_negatives))

#     return selected_negatives[:num_samples]


def select_lexically_similar_negatives(word_def_pairs, negative_pairs, num_samples):
    selected_negatives = []
    for index, (word, definition, _) in enumerate(word_def_pairs):
        if index % 50 == 0:
            print(f"index: {index}")
        similarities = [(neg_word, neg_def, lexical_similarity(word, neg_word)) 
                        for neg_word, neg_def, _ in word_def_pairs if neg_word != word]
        similarities.sort(key=lambda x: x[2], reverse=True)
        print(f"-"*90)
        print(f"ACTUAL WORD: {word}")
        print(f"SIMILAR WORDS: ")
        for similar in similarities[:10]:
            print(f"{similar[0]}")
        if similarities:
            selected_negatives.append((word, similarities[0][1]))

        i = 0
        temperature = 3
        for i in range(0, len(similarities)):
            if similarities[i][0] == word:
                continue
            else:
                if temperature > 0:
                    if definition != similarities[i][1]:
                        temperature -= 1
                    continue
                else:
                    break
        
        # Print selected negative sample
        print(f"WORD: {word}")
        print(f"POS_DEFINITION: {definition}")
        print(f"LEXICALLY_SIMILAR_WORD: {similarities[i][0]}")
        
        neg_sample_idx = i
        i = 0
        neg_definition = ""
        for i in range(0, len(word_def_pairs)):
            if word_def_pairs[i][0] == similarities[neg_sample_idx][0]:
                print(f"NEG_DEFINITION: {word_def_pairs[i][1]}")
                neg_definition = word_def_pairs[i][1]
                break

        selected_negatives.append((word, neg_definition))

        
        if len(selected_negatives) >= num_samples:
            break
        # print(len(selected_negatives))

    return selected_negatives[:num_samples]

def create_tsv_with_balanced_samples(wordnet_data, corpus_file, output_file):
    corpus_word_set = load_corpus_as_set(corpus_file)
    word_def_pairs = extract_word_definition_pairs()
    
    # positive_samples = [(word, definition) for word, definition, _ in word_def_pairs 
    #                     if word not in corpus_word_set and "_" not in word and " " not in word]
    
    positive_samples = []
    for (word, definition, _) in word_def_pairs:
        if word not in corpus_word_set and " " not in word and "_" not in word:
            # print(word)
            positive_samples.append((word, definition, 1))

    positive_samples = positive_samples[:10]
    negative_pairs = create_negative_samples(word_def_pairs)
    negative_samples = select_lexically_similar_negatives(word_def_pairs, negative_pairs, len(positive_samples))
    
    with open(output_file, 'w', newline='', encoding='utf-8') as tsv_file:
        tsv_writer = csv.writer(tsv_file, delimiter='\t')
        tsv_writer.writerow(['index', 'word', 'definition', 'label'])
        
        for index, (word, definition, _) in enumerate(positive_samples):
            tsv_writer.writerow([index, word, definition, 1])
        
        for index, (word, definition) in enumerate(negative_samples, start=len(positive_samples)):
            tsv_writer.writerow([index, word, definition, 0])

# Example usage
LANG = "te"
LANG_FULL = "telugu"
corpus_file = f'/media/saketh/New Volume/NAACL 2025/Datasets/{LANG}/{LANG}_10M_splits.txt'
output_file = f'{LANG_FULL}/WaD_neg_samples_10.tsv'

iwn = pyiwn.IndoWordNet(lang=pyiwn.Language.TELUGU)

create_tsv_with_balanced_samples(extract_word_definition_pairs(), corpus_file, output_file)

print(f"TSV file with balanced positive and negative samples created: {output_file}")