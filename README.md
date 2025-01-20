# IndicSIGMORPHON Dataset Preparation

## WaW: Word and Word
Classify whether two words in input are semantically related to one another.

### Data
Training and development data are UTF-8-encoded tab-separated values files. Each example occupies a single line and consists of two input words, as well as the corresponding output category. The following shows two lines of the training data:
    
    photocopy  mosaic  1
    poorer  proxy  0

## Preparation

### Word-Word Relationship Dataset

This repository contains code and data for creating word relationship datasets using IndoWordNet, specifically designed for evaluating language models' understanding of semantic relationships in Indian languages.

### Overview

The dataset consists of word pairs labeled as either semantically related (positive samples) or unrelated (negative samples). The relationships are derived from IndoWordNet's semantic relations, making this dataset suitable for testing language models' ability to capture word-level semantic relationships.

### Data Preparation Process

#### 1. Positive Sample Creation
Positive samples are extracted from IndoWordNet using the following process:
1. For each synset in IndoWordNet:
   - Extract the head word
   - Collect related words through multiple relationship types:
     - Similar words (SIMILAR relation)
     - Hypernyms (HYPERNYMY relation)
     - Hyponyms (HYPONYMY relation)
2. Create word pairs between the head word and each related word
3. Filter out pairs containing special characters or identical words
4. Store unique pairs as positive samples with label 1

#### 2. Negative Sample Generation
Negative samples are generated through a careful validation process to ensure true semantic unrelatedness:

1. Random Pair Selection:
   - Randomly select two words from the vocabulary
   - Generate equal number of negative pairs as positive pairs

2. Validation Checks:
   Each potential negative pair must pass multiple validation criteria:
   - Words must not be identical
   - The pair (or its reverse) must not exist in positive samples
   - Words must not share any common neighbors in the semantic network
   - Words must not share common hypernyms
   - Words must not have entailment relationships

3. Implementation Details:
   - Uses a maximum attempt limit to prevent infinite loops
   - Implements comprehensive WordNet-based checks
   - Issues warnings if required number of negative samples cannot be generated

### Output Format

The dataset is saved in TSV format with the following columns:
- `index`: Unique identifier for each pair
- `word_a`: First word in the pair
- `word_b`: Second word in the pair
- `label`: 1 for positive pairs (semantically related), 0 for negative pairs

## Usage

1. Install required dependencies:
```bash
pip install pyiwn
```

2. Prepare your corpus file with space-separated words

3. Update the language settings in the script:
```python
LANG = "ml"  # Language code
LANG_FULL = "malayalam"  # Language name
corpus_file = "path/to/your/corpus.txt"
```

4. Run the script:
```bash
python WaW.py
```

## Notes
- The quality of the dataset depends on the coverage of IndoWordNet
- Negative sampling is computationally intensive due to extensive validation checks
- The validation process ensures high-quality negative samples by checking multiple types of semantic relationships

### Language Support

Till date, `WaW` data for following languages are prepared:
1. English

|   Set                |   Number of Samples  |
|------------------------|-------------------|
|   train  |   148069           |
|   dev      |   42304           |
|   test      |   21153           |

2. Hindi

|   Set                |   Number of Samples  |
|------------------------|-------------------|
|   train  |   57451           |
|   dev      |   16415           |
|   test      |   8208           |

3. Telugu

|   Set                |   Number of Samples  |
|------------------------|-------------------|
|   train  |   24884           |
|   dev      |   7109           |
|   test      |   3555           |
4. Tamil

|   Set                |   Number of Samples  |
|------------------------|-------------------|
|   train  |   30913           |
|   dev      |   8832           |
|   test      |   4417           |
5. Malayalam

|   Set                |   Number of Samples  |
|------------------------|-------------------|
|   train  |   37553           |
|   dev      |   10729           |
|   test      |   5365           |

+ Link to Word and Word Data: [WaW](https://github.com/SakethReddyVemula/IndicSigmorphon-Dataset/tree/main/Final_Dataset)