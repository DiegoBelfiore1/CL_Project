# -*- coding: utf-8 -*-
"""CL_project_as_db.ipynb"""

import re
import pandas as pd
import numpy as np
from scipy.stats import spearmanr, pearsonr
import matplotlib.pyplot as plt
import csv
import random
plt.style.use('ggplot')

from google.colab import drive
drive.mount('/content/drive')

"""to extract the text colum and randomize the value"""

import csv
import random

# Funzione per leggere il file CSV di input e estrarre le colonne pertinenti
def read_csv(file_name):
    data = []
    pair_ids = set()  # Set per tenere traccia di tutti i PairID
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 4:
                data.append((row[3], row[4]))  # Estrai ID (3ª colonna) ed elemento (4ª colonna)
                pair_ids.add(row[3])  # Aggiungi l'ID al set di PairID
    return data, pair_ids

# Funzione per creare combinazioni di 8 colonne con ID ed elementi
def create_combinations(data, pair_ids):
    unique_combinations = set()
    used_pair_ids = set()  # Set per tenere traccia degli ID utilizzati
    while len(unique_combinations) < 11000 or used_pair_ids != pair_ids:
        random_selection = random.sample(data, 4)
        combination = []
        for id_, element in random_selection:
            combination.extend([id_, element])
            used_pair_ids.add(id_)  # Aggiungi l'ID al set degli ID utilizzati
        tuple_ = tuple(combination)
        unique_combinations.add(tuple_)
    return list(unique_combinations)

# Funzione per scrivere le combinazioni in un nuovo file CSV
def write_csv(combinations):
    with open('new_tuples_11k.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for combination in combinations:
            writer.writerow(combination)

# Sostituisci 'input.csv' con il nome del file CSV di input
input_data, pair_ids = read_csv('/content/sem_text_rel_ranked.csv')

if len(input_data) < 4:
    print("Dati insufficienti per creare combinazioni.")
else:
    unique_combinations = create_combinations(input_data, pair_ids)
    write_csv(unique_combinations)
    print("File CSV con 11000 combinazioni uniche è stato creato.")

import csv

# Function to insert a row at the beginning of a CSV file
def insert_row_to_csv(file_name, row_data):
    with open(file_name, 'r', newline='') as file:
        reader = csv.reader(file)
        rows = list(reader)

    rows.insert(0, row_data)

    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

# Replace 'your_file.csv' with the name of your CSV file
file_name = 'new_tuples_11k.csv'

# New row data (example values)
new_row_text = 'id1,pair1,id2,pair2,id3,pair3,id4,pair4'
new_row = new_row_text.split(',')  # Splitting the text by commas into separate cells

# Inserting the new row at the beginning of the CSV file
insert_row_to_csv(file_name, new_row)

dataset = pd.read_csv('new_tuples_11k.csv')

dataset['pair1'].values

import csv

# Function to divide the text in columns by '\n' and create new columns
def divide_columns(input_file, output_file):
    with open(input_file, 'r', newline='') as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames
        rows = list(reader)

        for col in ['pair1', 'pair2', 'pair3', 'pair4']:
            index = headers.index(col)  # Find the index of the column to split
            col_a = col + 'a'
            col_b = col + 'b'
            headers.insert(index + 1, col_a)  # Insert new column names
            headers.insert(index + 2, col_b)

            for row in rows:
                if '\n' in row[col]:
                    row[col_a], row[col_b] = row[col].split('\n', 1)  # Split the text at '\n'
                else:
                    row[col_a], row[col_b] = row[col], ''  # If no '\n', assign the whole text to col_a and an empty string to col_b

                del row[col]  # Remove the original column

    with open(output_file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

# Replace 'input.csv' with the name of your input CSV file and 'output.csv' with the desired output filename
divide_columns('new_tuples_11k.csv', 'pair_splitted.csv')

#Install the library
! pip install -U sentence-transformers

!pip install transformers

import csv
from sentence_transformers import SentenceTransformer
import torch

# Function to compute similarity scores between pairs of sentences
def compute_similarity_scores(sentences_a, sentences_b):
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')  # Load Sentence-BERT model
    sentence_embeddings_a = model.encode(sentences_a, convert_to_tensor=True)
    sentence_embeddings_b = model.encode(sentences_b, convert_to_tensor=True)

    similarity_scores = []
    for emb_a, emb_b in zip(sentence_embeddings_a, sentence_embeddings_b):
        similarity = torch.nn.functional.cosine_similarity(emb_a, emb_b, dim=0)
        similarity_scores.append(float(similarity))

    return similarity_scores

# Function to compute similarity scores between pairs of columns and write scores to a new CSV file
def compute_and_save_similarity_scores(input_file, output_file):
    with open(input_file, 'r', newline='') as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames
        rows = list(reader)

        pair_columns = [('pair1a', 'pair1b'), ('pair2a', 'pair2b'), ('pair3a', 'pair3b'), ('pair4a', 'pair4b')]
        similarity_columns = ['pair1', 'pair2', 'pair3', 'pair4']

        for i, (col_a, col_b) in enumerate(pair_columns):
            sentences_a = [row[col_a] for row in rows]
            sentences_b = [row[col_b] for row in rows]

            similarity_scores = compute_similarity_scores(sentences_a, sentences_b)

            for j, score in enumerate(similarity_scores):
                rows[j][similarity_columns[i]] = score

    with open(output_file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

# Replace 'input.csv' with the name of your input CSV file and 'similarity_score.csv' with the desired output filename
compute_and_save_similarity_scores('pair_splitted.csv', 'similarity_score.csv')

# The file has been uploaded. Let's load the data and apply the corrected algorithm.

# Load the CSV file
csv_path = '/content/similarity_score.csv'
data = pd.read_csv(csv_path)

# Step 1: Combine 'id1', 'id2', 'id3', 'id4' into a single column, ensuring no NaNs and converting to string
combined_ids = pd.concat([
    data['id1'].dropna().astype(str),
    data['id2'].dropna().astype(str),
    data['id3'].dropna().astype(str),
    data['id4'].dropna().astype(str)
])

# Step 2: Remove duplicates and sort the values
unique_sorted_ids = combined_ids.unique()
unique_sorted_ids.sort()

# Step 3: Create a DataFrame from the sorted unique IDs
ids_df = pd.DataFrame(unique_sorted_ids, columns=['ID'])

# Step 4: Adjust the DataFrame to have exactly 5500 entries
num_entries_required = 5500
num_entries_current = len(ids_df)

if num_entries_current > num_entries_required:
    # If more than 5500, truncate
    ids_df = ids_df.head(num_entries_required)
elif num_entries_current < num_entries_required:
    # If less than 5500, fill the shortfall with NaN or placeholders
    shortfall = num_entries_required - num_entries_current
    filler = pd.DataFrame([None] * shortfall, columns=['ID'])
    ids_df = pd.concat([ids_df, filler], ignore_index=True)

# Save this new DataFrame to a new CSV file
new_csv_path = '/content/combined_id.csv'
ids_df.to_csv(new_csv_path, index=False)

# Extracting the id columns from the similarity_score_df

similarity_score_df = pd.read_csv('similarity_score.csv')  # Replace 'your_data_file.csv' with your actual data file path

id_columns = [col for col in similarity_score_df.columns if 'id' in col]
id_data = similarity_score_df[id_columns]

# Counting the occurrences of each id value across all the id columns
id_counts = id_data.apply(pd.Series.value_counts).sum(axis=1)

combined_ids_df = pd.read_csv('combined_id.csv')  # Replace 'your_data_file.csv' with your actual data file path

# Merging this count data with the combined_ids_df
combined_ids_df['occurrences'] = combined_ids_df['ID'].map(id_counts)

# Saving the updated combined_ids_df to a new CSV file
updated_combined_ids_path = '/content/updated_combined_ids.csv'
combined_ids_df.to_csv(updated_combined_ids_path, index=False)

updated_combined_ids_path

# Leggi il file CSV risultante
combined_ids_df = pd.read_csv('/content/updated_combined_ids.csv')

# Crea due colonne vuote chiamate "best" e "worst" prima della colonna "occurrences"
combined_ids_df.insert(combined_ids_df.columns.get_loc("occurrences"), "best", None)
combined_ids_df.insert(combined_ids_df.columns.get_loc("occurrences"), "worst", None)

# Salva il DataFrame aggiornato in un nuovo file CSV
updated_combined_ids_path = '/content/updated_combined_ids_with_columns.csv'
combined_ids_df.to_csv(updated_combined_ids_path, index=False)

# Extracting the ids and scores for each pair from the similarity_score dataframe
ids = ['id1', 'id2', 'id3', 'id4']
scores = ['pair1', 'pair2', 'pair3', 'pair4']

df_modified_combined_ids = pd.read_csv('updated_combined_ids_with_columns.csv')  # Replace 'your_data_file.csv' with your actual data file path

# Create a dictionary to store the count of best and worst scores for each id
score_counts = {id: {'best': 0, 'worst': 0} for id in df_modified_combined_ids['ID']}

# Iterate through each row in the dataframe
for _, row in similarity_score_df.iterrows():
    # Extract the scores for the current row
    row_scores = [row[score] for score in scores]

    # Find the best and worst scores and the corresponding ids
    best_score_id = row[ids[row_scores.index(max(row_scores))]]
    worst_score_id = row[ids[row_scores.index(min(row_scores))]]

    # Increment the count for the best and worst score ids
    if best_score_id in score_counts:
        score_counts[best_score_id]['best'] += 1
    if worst_score_id in score_counts:
        score_counts[worst_score_id]['worst'] += 1

# Update the modified_combined_ids dataframe with the counts
for id in df_modified_combined_ids['ID']:
    df_modified_combined_ids.loc[df_modified_combined_ids['ID'] == id, 'best'] = score_counts[id]['best']
    df_modified_combined_ids.loc[df_modified_combined_ids['ID'] == id, 'worst'] = score_counts[id]['worst']

# Saving the updated dataframe to a new CSV file
updated_file_path = '/content/updated_modified_combined_ids.csv'
df_modified_combined_ids.to_csv(updated_file_path, index=False)

updated_file_path

# Saving the updated dataframe with the 'relatedness_score' column to a new CSV file
# Calculate the "relatedness_score" for each row
df_modified_combined_ids = pd.read_csv('updated_modified_combined_ids.csv')  # Replace 'your_data_file.csv' with your actual data file path

df_modified_combined_ids['relatedness_score'] = (df_modified_combined_ids['best'] / df_modified_combined_ids['occurrences']) - (df_modified_combined_ids['worst'] / df_modified_combined_ids['occurrences'])

# Display the first few rows to verify the calculation
df_modified_combined_ids.head()

updated_file_path_with_score = '/content/updated_modified_combined_ids_with_score.csv'
df_modified_combined_ids.to_csv(updated_file_path_with_score, index=False)

#Calcola il minimo e il massimo valore dei tuoi "relatedness_score"
min_value = df_modified_combined_ids['relatedness_score'].min()
max_value = df_modified_combined_ids['relatedness_score'].max()

# Applica la normalizzazione min-max
df_modified_combined_ids['normalized_relatedness_score'] = (df_modified_combined_ids['relatedness_score'] - min_value) / (max_value - min_value)

# Rimuovi la colonna "relatedness_score" se non la vuoi più nel dataframe
df_modified_combined_ids.drop(columns=['relatedness_score'], inplace=True)

# Salvare il dataframe aggiornato in un nuovo file CSV
updated_file_path = '/content/relatedness_updated_modified_combined_ids.csv'
df_modified_combined_ids.to_csv(updated_file_path, index=False)

from typing import Tuple, Set

df = pd.read_csv('/content/sem_text_rel_ranked.csv')  # Replace 'your_data_file.csv' with your actual data file path

def calculate_dice_coefficient(text_pair: str) -> float:
    # Split the pair into two sentences
    sentence_x, sentence_y = text_pair.split("\n")

    # Tokenize the sentences into unigrams (words)
    unigrams_x = set(sentence_x.split())
    unigrams_y = set(sentence_y.split())

    # Calculate the intersection and the union of the two unigram sets
    intersection = len(unigrams_x.intersection(unigrams_y))
    union = len(unigrams_x) + len(unigrams_y)

    # Calculate the Dice Coefficient
    dice_coefficient = (2 * intersection) / union if union != 0 else 0
    return dice_coefficient

# Apply the Dice Coefficient calculation to each text pair in the dataframe
df['LexicalOverlap'] = df['Text'].apply(calculate_dice_coefficient)

# Save the updated dataframe to a new CSV file to return to the user
output_csv_path = '/content/sem_text_rel_ranked_with_overlap.csv'
df.to_csv(output_csv_path, index=False)

average_lexical_overlap = df['LexicalOverlap'].mean()
print(f"Average Lexical Overlap: {average_lexical_overlap:.4f}")

# Estraggo le colonne rilevanti da ciascun dataframe
relatedness_df = pd.read_csv('relatedness_updated_modified_combined_ids.csv')  # Replace 'your_data_file.csv' with your actual data file path
sem_text_df = pd.read_csv('sem_text_rel_ranked_with_overlap.csv')  # Replace 'your_data_file.csv' with your actual data file path

relatedness_ids = relatedness_df['ID']
sem_text_pair_ids = sem_text_df['PairID']

# Riordino il dataframe relatedness in base all'ordine dei PairID in sem_text
# Creo un dizionario per mappare gli id di sem_text al loro indice
order_dict = {id: index for index, id in enumerate(sem_text_pair_ids)}

# Aggiungo una colonna temporanea al dataframe relatedness per mappare gli indici
relatedness_df['order_index'] = relatedness_df['ID'].map(order_dict)

# Riordino il dataframe relatedness basandomi sugli indici mappati e rimuovo la colonna temporanea
ordered_relatedness_df = relatedness_df.sort_values(by='order_index').drop(columns=['order_index'])

ordered_relatedness_df.to_csv('ordered_relatedness.csv', index=False)

# Load the two files
file_ordered_relatedness = '/content/ordered_relatedness.csv'
file_sem_text_rel_ranked_with_overlap = '/content/sem_text_rel_ranked_with_overlap.csv'

df_ordered_relatedness = pd.read_csv(file_ordered_relatedness)
df_sem_text_rel_ranked_with_overlap = pd.read_csv(file_sem_text_rel_ranked_with_overlap)

# Assuming there is a common identifier column to join on (e.g., 'ID')
# If there isn't, we need more information about how to align the rows of the two datasets
# For now, let's assume the rows in both files are in the same order and we can directly transfer the column
# Check if the number of rows in both dataframes is the same
if len(df_ordered_relatedness) == len(df_sem_text_rel_ranked_with_overlap):
    # Add the 'LexicalOverlap' column from sem_text_rel_ranked_with_overlap to ordered_relatedness
    df_ordered_relatedness['LexicalOverlap'] = df_sem_text_rel_ranked_with_overlap['LexicalOverlap']

    # Save to a new CSV file
    output_file = '/content/updated_ordered_relatedness.csv'
    df_ordered_relatedness.to_csv(output_file, index=False)
else:
    output_file = 'Error: The number of rows in the files does not match.'

from scipy.stats import spearmanr

# Caricamento del file CSV
data = pd.read_csv('updated_ordered_relatedness.csv')

# Assicurarsi che le colonne 'normalized_relatedness_score' e 'LexicalOverlap' siano presenti nel DataFrame
if 'normalized_relatedness_score' in data.columns and 'LexicalOverlap' in data.columns:
    # Calcolo della correlazione di Spearman
    correlation, p_value = spearmanr(data['LexicalOverlap'], data['normalized_relatedness_score'])
    print("Correlation:", correlation)
    print("P-value:", p_value)
else:
    print("Le colonne richieste non sono presenti nel file CSV.")

import pandas as pd

def attach_score_column(input_file_path: str, output_file_path: str) -> None:
    """
    Extract the 'Score' column from 'sem_text_rel_ranked.csv' and attach it to 'updated_ordered_relatedness.csv'.

    Parameters:
    - input_file_path (str): Path to 'sem_text_rel_ranked.csv'.
    - output_file_path (str): Path to 'updated_ordered_relatedness.csv'.
    """
    try:
        # Read the 'sem_text_rel_ranked.csv' file
        df_sem_text_rel_ranked = pd.read_csv(input_file_path)

        # Extract the 'Score' column
        score_column = df_sem_text_rel_ranked['Score']

        # Read the 'updated_ordered_relatedness.csv' file
        df_updated_ordered_relatedness = pd.read_csv(output_file_path)

        # Attach the 'Score' column to 'updated_ordered_relatedness.csv'
        df_updated_ordered_relatedness['Score'] = score_column

        # Save the updated dataframe to the output file
        df_updated_ordered_relatedness.to_csv(output_file_path, index=False)

        print(f"The 'Score' column has been attached to '{output_file_path}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
input_file_path = '/content/sem_text_rel_ranked.csv'
output_file_path = '/content/updated_ordered_relatedness.csv'
attach_score_column(input_file_path, output_file_path)

import pandas as pd
from scipy.stats import spearmanr

def compute_spearman_correlation(input_file_path: str) -> float:
    """
    Compute the Spearman correlation between 'Score' and 'normalized_relatedness_score' columns.

    Parameters:
    - input_file_path (str): Path to the input file containing both columns.

    Returns:
    - float: Spearman correlation coefficient.
    """
    try:
        # Read the input file
        df = pd.read_csv(input_file_path)

        # Extract the 'Score' and 'normalized_relatedness_score' columns
        score_column = df['Score']
        normalized_relatedness_column = df['normalized_relatedness_score']

        # Calculate Spearman correlation
        correlation, _ = spearmanr(score_column, normalized_relatedness_column)

        return correlation
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
input_file_path = '/content/updated_ordered_relatedness.csv'
correlation = compute_spearman_correlation(input_file_path)

if correlation is not None:
    print(f"Spearman correlation: {correlation:.4f}")

"""LEXICAL OVERLAP"""

# Load the File
df_str_rel = pd.read_csv('/content/sem_text_rel_ranked.csv', usecols=[3,4,5])
df_str_rel.head()

# Creating a column "Split_Text" which is a list of two sentences.
df_str_rel['Split_Text'] = df_str_rel['Text'].apply(lambda x: x.split("\n"))
df_str_rel.head()

def dice_score(s1,s2):
  s1 = s1.lower()
  s1_split = re.findall(r"\w+|[^\w\s]", s1, re.UNICODE)

  s2 = s2.lower()
  s2_split = re.findall(r"\w+|[^\w\s]", s2, re.UNICODE)

  dice_coef = len(set(s1_split).intersection(set(s2_split))) / (len(set(s1_split)) + len(set(s2_split)))
  return round(dice_coef, 2)

true_scores = df_str_rel['Score'].values
pred_scores = []

for index,row in df_str_rel.iterrows():
  s1,s2 = row["Text"].split("\n")

  # Overlap score
  pred_scores.append(dice_score(s1,s2))

df_str_rel['Pred_Score'] = pred_scores
df_str_rel.head()
