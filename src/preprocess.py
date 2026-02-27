import argparse
from pathlib import Path

import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

def preprocess_data(data_file: str, output_dir: str) -> None:
    """
    Preprocess raw protein sequence data for model training.

    This function loads the raw data, cleans it, encodes labels, and splits
    it into train/validation/test sets. The split strategy must handle the
    extreme class imbalance in the Pfam dataset.

    Parameters
    ----------
    data_file : str
        Path to the combined raw data CSV file.
    output_dir : str
        Directory where processed files will be saved.

    Steps
    -----
    1. Load the data with pandas
    2. Remove rows with missing values
    3. Encode the 'family_accession' column with LabelEncoder
    4. Design and implement a split strategy that handles class imbalance
    5. Save train.csv, val.csv, and test.csv to output_dir

    Notes
    -----
    sklearn's train_test_split with stratify will fail on this dataset
    because some classes have only one sample. You need to implement
    a custom strategy.
    """
    #1. Load data
    df = pd.read_csv(data_file)

    #2. Remove rows with missing values
    df = df.dropna(axis=0, how='any')

    #3. Encode family_accession column with LabelEncoder
    le = LabelEncoder()
    df["family_encoded"] = le.fit_transform(df["family_accession"])

    #4. Division des classes entre rare et common 
    family_count = df['family_encoded'].value_counts()
    rare_families = family_count[family_count < 10].index
    df_rare = df[df['family_encoded'].isin(rare_families)]
    df_common = df[~df['family_encoded'].isin(rare_families)]

    #5. Stratégie de split
    X_train, y_train, X_test, y_test, X_val, y_val = split(df_common, df_rare)

    #6. Sauvegarde des fichiers
    save_splits(X_train, y_train, X_val, y_val, X_test, y_test, output_dir)
    
def split(df_common, df_rare):
    X = df_common['sequence']
    y = df_common['family_encoded']

    # Premier split = 70% train et 30% test
    Xcommon_train, X_temp, y_train_common, y_temp = train_test_split(
        X, 
        y, 
        test_size=0.30, 
        random_state=42, 
        stratify=y)

    # Deuxième split = 15% test et 15% validation
    X_test, X_val, y_test, y_val = train_test_split(
        X_temp, 
        y_temp, 
        test_size=0.5, 
        random_state=42, 
        stratify=y_temp)

    # Fusion rare et common
    X_rare = df_rare['sequence']
    y_rare = df_rare['family_encoded']
    X_train = pd.concat([Xcommon_train, X_rare], ignore_index=True)
    y_train = pd.concat([y_train_common, y_rare], ignore_index=True)

    return X_train, y_train, X_test, y_test, X_val, y_val

def save_splits(X_train, y_train, X_val, y_val, X_test, y_test, output_dir):

    # Créer le dossier si nécessaire
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Créer les DataFrames
    train_df = pd.DataFrame({
        'sequence': X_train.values,
        'family_encoded': y_train.values
    })
    
    val_df = pd.DataFrame({
        'sequence': X_val.values,
        'family_encoded': y_val.values
    })
    
    test_df = pd.DataFrame({
        'sequence': X_test.values,
        'family_encoded': y_test.values
    })
    
    # Sauvegarder
    train_df.to_csv(output_dir / 'train.csv', index=False)
    val_df.to_csv(output_dir / 'val.csv', index=False)
    test_df.to_csv(output_dir / 'test.csv', index=False) 
     
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Preprocess Pfam data.")
    parser.add_argument("--data_file", type=str, required=True)
    parser.add_argument("--output_dir", type=str, required=True)

    args = parser.parse_args()

    preprocess_data(args.data_file, args.output_dir)
    
