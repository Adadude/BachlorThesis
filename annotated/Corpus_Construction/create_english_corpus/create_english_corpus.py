import os 
import pandas as pd 
 
# Folder where this Python script is located
DATA_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)

# Output folder from the language detection step
LANGUAGE_DETECTION_OUTPUT = os.path.abspath(
    os.path.join(
        DATA_FOLDER,
        "..",
        "language_detection",
        "output"
    )
)

# Output folder for the English corpus
OUTPUT_FOLDER = os.path.join(
    DATA_FOLDER,
    "output"
)

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)
 
# Here we have the exact annotated filenames and their readable book titles 
BOOK_FILES = { 
    "GoodreadsKafkaAmerikaReviews_annotated_confidence.csv": "Amerika", 
    "GoodreadsKafkaCastleReviews_annotated_confidence.csv": "The Castle", 
    "GoodreadsKafkaHungerArtistReviews_annotated_confidence.csv": "A Hunger Artist", 
    "GoodreadsKafkaMetamorphosisReviews_annotated_confidence.csv": "Metamorphosis", 
    "GoodreadsKafkaPenalColonyReviews_annotated_confidence.csv": "In the Penal Colony", 
    "GoodreadsKafkaTrialReviews_annotated_confidence.csv": "The Trial" 
} 
 
all_dfs = [] 
 
for file_name, book_title in BOOK_FILES.items(): 
    file_path = os.path.join(
        LANGUAGE_DETECTION_OUTPUT,
        file_name
    )
 
    print(f"Reading: {file_name}") 
 
    df = pd.read_csv(file_path, encoding="utf-8-sig") 
 
    df["source_file"] = file_name 
    df["book_title"] = book_title 
 
    df["language"] = ( 
        df["language"] 
        .astype(str) 
        .str.strip() 
        .str.lower() 
    ) 
 
# Keeps only (>= 0.80) English reviews 
    df = df[ 
    (df["language"] == "en") & 
    (df["language_confidence"] >= 0.80) 
    ].copy() 
 
    print(f"High-confidence and English reviews retained: {len(df)}") 
 
    all_dfs.append(df) 
 
if not all_dfs: 
    raise ValueError("None of the six annotated files could be processed.") 
 
# Combines the English reviews from all six books 
english_corpus = pd.concat(all_dfs, ignore_index=True) 
 
output_path = os.path.join( 
    OUTPUT_FOLDER, 
    "kafka_english_corpus.csv" 
) 
 
english_corpus.to_csv( 
    output_path, 
    index=False, 
    encoding="utf-8-sig" 
) 
 
print("\nEnglish corpus created successfully.") 
print(f"Output file: {output_path}") 
print(f"Total English reviews: {len(english_corpus)}") 
 
print("\nReviews per book:") 
print(english_corpus["book_title"].value_counts())