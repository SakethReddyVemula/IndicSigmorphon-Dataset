import pandas as pd
import csv

LANG = "te"
LANGUAGE = "telugu"
INFILE_PATH = f"{LANGUAGE}/WaD_{LANG}_words.tsv"
OUTFILE_PATH = f"{LANGUAGE}/WaD_{LANG}_words.csv"

# Open the TSV filae for reding and the CSV file for writing
with open(INFILE_PATH, 'r') as tsv_file, open(OUTFILE_PATH, 'w', newline='') as csv_file:
    tsv_reader = csv.reader(tsv_file, delimiter='\t')
    csv_writer = csv.writer(csv_file)

    # Write all rows from TSV to CSV
    for row in tsv_reader:
        print(row[0], row[1])
        csv_writer.writerow(row)

