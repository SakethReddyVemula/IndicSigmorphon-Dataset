import pandas as pd
import os
from sklearn.model_selection import train_test_split

def create_balanced_splits(common_file, iov_file, oov_file, lang, train_size=0.7, dev_size=0.15, test_size=0.15, random_state=42):
    """
    Creates balanced train/dev/test splits for three input TSV files while preserving the original files.
    
    Args:
        common_file (str): Path to the common (all) data TSV file
        iov_file (str): Path to the in-vocabulary data TSV file
        oov_file (str): Path to the out-of-vocabulary data TSV file
        train_size (float): Proportion of data for training (default: 0.7)
        dev_size (float): Proportion of data for development (default: 0.15)
        test_size (float): Proportion of data for testing (default: 0.15)
        random_state (int): Random seed for reproducibility
        
    Returns:
        None (saves files to disk)
    """
    def split_and_save(input_file, prefix):
        # Read the input TSV
        df = pd.read_csv(input_file, sep='\t')
        
        # Separate positive and negative samples
        pos_samples = df[df['label'] == 1]
        neg_samples = df[df['label'] == 0]
        
        # First split into train and temp (dev+test)
        pos_train, pos_temp = train_test_split(
            pos_samples, 
            train_size=train_size,
            random_state=random_state
        )
        
        neg_train, neg_temp = train_test_split(
            neg_samples,
            train_size=train_size,
            random_state=random_state
        )
        
        # Split temp into dev and test
        dev_ratio = dev_size / (dev_size + test_size)
        pos_dev, pos_test = train_test_split(
            pos_temp,
            train_size=dev_ratio,
            random_state=random_state
        )
        
        neg_dev, neg_test = train_test_split(
            neg_temp,
            train_size=dev_ratio,
            random_state=random_state
        )
        
        # Combine positive and negative samples for each split
        train_df = pd.concat([pos_train, neg_train]).sample(frac=1, random_state=random_state)
        dev_df = pd.concat([pos_dev, neg_dev]).sample(frac=1, random_state=random_state)
        test_df = pd.concat([pos_test, neg_test]).sample(frac=1, random_state=random_state)
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(input_file)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save splits with new indices
        for df, split_name in [(train_df, 'train'), (dev_df, 'dev'), (test_df, 'test')]:
            # Reset index to create sequential indices
            df = df.reset_index(drop=True)
            df['index'] = df.index
            
            # Reorder columns to match original format
            df = df[['index', 'word_a', 'word_b', 'label']]
            
            # Save to file
            output_file = os.path.join(output_dir, f'{prefix}_{split_name}.tsv')
            df.to_csv(output_file, sep='\t', index=False)
            
        # Print statistics
        print(f"\nStatistics for {prefix}:")
        print(f"Train set: {len(train_df)} samples ({len(pos_train)} positive, {len(neg_train)} negative)")
        print(f"Dev set: {len(dev_df)} samples ({len(pos_dev)} positive, {len(neg_dev)} negative)")
        print(f"Test set: {len(test_df)} samples ({len(pos_test)} positive, {len(neg_test)} negative)")
    
    # Process each file
    for input_file, prefix in [
        (common_file, f'WaW_{lang}_all'),
        (iov_file, f'WaW_{lang}_IOV'),
        (oov_file, f'WaW_{lang}_OOV')
    ]:
        print(f"\nProcessing {os.path.basename(input_file)}...")
        split_and_save(input_file, prefix)


LANG = "hi"
LANG_FULL = "hindi"
path_to_common_file = f"{LANG_FULL}/WaW_{LANG}_all.tsv"
path_to_IOV_file = f"{LANG_FULL}/WaW_{LANG}_IOV.tsv"
path_to_OOV_file = f"{LANG_FULL}/WaW_{LANG}_OOV.tsv"


create_balanced_splits(
    path_to_common_file,
    path_to_IOV_file,
    path_to_OOV_file,
    lang=LANG,
    train_size=0.7,
    dev_size=0.2,
    test_size=0.1,
    random_state=42
)