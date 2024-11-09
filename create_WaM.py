import csv
import os
import locale

# Store the current locale
original_locale = locale.getlocale()

PATH_TO_WaD = "telugu/WaD_te.tsv"
PATH_TO_output = "telugu/WaM_te.tsv"
LANG = "te"
LANGUAGE = "telugu"

if LANG == "te":
    # Set the new locale (Telugu, for example)
    locale.setlocale(locale.LC_ALL, 'te_IN.UTF-8')
    print(f"Locale set to: {locale.getlocale()}")
elif LANG == "ta":
    # Set the new locale (Telugu, for example)
    locale.setlocale(locale.LC_ALL, 'ta_IN.UTF-8')
    print(f"Locale set to: {locale.getlocale()}")
elif LANG == "hi":
    # Set the new locale (Telugu, for example)
    locale.setlocale(locale.LC_ALL, 'hi_IN.UTF-8')
    print(f"Locale set to: {locale.getlocale()}")

print(f"Running the script with {LANGUAGE} locale...")

# File paths (modify as needed)
input_file = PATH_TO_WaD  # Your input file path
output_file = PATH_TO_output  # Output file where the classification will be saved
progress_file = 'progress.txt'  # File to store the last processed index

# Function to get the last processed index
def get_last_processed_index():
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            last_index = f.readline().strip()
            if last_index.isdigit():
                return int(last_index)
    return 1

# Function to save the current index
def save_progress(index):
    with open(progress_file, 'w') as f:
        f.write(str(index))

# Function to prompt the user for classification
def classify_word(index, word, definition):
    print(f"-"*90)
    print(f"\nINDEX: {index}")
    print(f"WORD: {word}")
    print(f"DEFINITION: {definition}")
    print("Select Morphology: (V)ocab, (I)nflection, (D)erivation, (C)ompound, (N)one")
    
    while True:
        choice = input("Enter your choice (V/I/D/C/N): ").strip().upper()
        if choice in {'V', 'I', 'D', 'C', 'N'}:
            return choice
        else:
            print("Invalid choice. Please select again.")

# Main function
def main():
    # Read the input TSV file
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile, delimiter='\t')
        rows = list(reader)
    
    # Get the last processed index to resume from
    last_processed_index = get_last_processed_index()

    # Open the output TSV file in append mode
    with open(output_file, 'a', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter='\t')
        # Process each row starting from the last processed index
        
        for row in rows[last_processed_index:]:
            
            index, word, definition, label = row[0], row[1], row[2], row[3]
            wrote = False
            # Prompt the user for morphology classification
            morphology = classify_word(index, word, definition)
            
            # Write the result to the output file
            if morphology == 'V':
                writer.writerow([index, word, "vocab", label])
            elif morphology == 'I':
                writer.writerow([index, word, "inflection", label])
                wrote = True
            elif morphology == 'D':
                writer.writerow([index, word, "derivation", label])
                wrote = True
            elif morphology == 'C':
                writer.writerow([index, word, "compound", label])
                wrote = True
            elif morphology == "N":
                writer.writerow([index, word, "none", label])
            
            
            # Save the current progress
            if wrote == True:
                save_progress(index)
            
            # Allow the user to cancel the process (Ctrl + C to exit)
            try:
                continue
            except KeyboardInterrupt:
                print("\nProcess interrupted. Progress saved.")
                return
    
    

if __name__ == "__main__":
    main()

    # Restore the original locale at the end of the script
    locale.setlocale(locale.LC_ALL, original_locale)
    print(f"Locale reset to: {locale.getlocale()}")