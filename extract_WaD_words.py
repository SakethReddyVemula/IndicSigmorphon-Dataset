import csv 

LANG = "ta"
LANGUAGE = "tamil"
INFILE_PATH = f"{LANGUAGE}/WaD_{LANG}.tsv"
OUTFILE_PATH = f"{LANGUAGE}/WaD_{LANG}_words.tsv"

with open(INFILE_PATH, "r", encoding='utf-8') as infile:
    reader = csv.reader(infile, delimiter='\t')
    rows = list(reader)

    with open(OUTFILE_PATH, "a", encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter='\t')

        writer.writerow(["index", "word", "definition", "morphology_type"])
        for row in rows[1:]:
            writer.writerow([row[0], row[1], row[2]])
            