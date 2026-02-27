import argparse
from pathlib import Path

import pandas as pd
import os


def unpack_data(input_dir: str, output_file: str) -> None:
    """
    Combine multiple CSV files from a directory into a single CSV file.

    This function reads all CSV files in the input directory, concatenates
    them into a single DataFrame, and saves the result to the output path.

    Parameters
    ----------
    input_dir : str
        Path to the directory containing the CSV files to combine.
    output_file : str
        Path where the combined CSV file will be saved.

    Steps
    -----
    1. List all files in the input directory
    2. Filter to keep only .csv files
    3. Read each CSV file into a pandas DataFrame
    4. Concatenate all DataFrames
    5. Save the combined DataFrame to output_file
    """
    all_csv_files = get_all_files(input_dir)
    final_dataframe = concatenate_csv(all_csv_files)
    final_dataframe.to_csv(output_file)


def get_all_files(path):
    """
        Creates a list of all csv files in the directory recursively
    """
    res = []
    for root, dirs, files in os.walk(path):
        for file in files:
            res.append(os.path.join(root, file))
    return res

def concatenate_csv(files_list):
    """
        Reads each CSV in the file, creates a dataframe and concatenates all the dataframes
    """
    final_dataframe = pd.DataFrame()

    for file in files_list:
        df = pd.read_csv(Path(file))
        final_dataframe = pd.concat([final_dataframe, df])
    
    return final_dataframe


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unpack and combine CSV files.")
    parser.add_argument("--input_dir", type=str, required=True)
    parser.add_argument("--output_file", type=str, required=True)

    args = parser.parse_args()

    unpack_data(args.input_dir, args.output_file)
