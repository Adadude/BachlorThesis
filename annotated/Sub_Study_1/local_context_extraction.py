import os
import re
import pandas as pd


# Folder where this script is located
DATA_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)

# Input CSV is stored in the folder "input" from the folder "Sub-Study 1".
INPUT_CSV = os.path.join(
    DATA_FOLDER,
    "input/kafkaesque_main_comparable_corpus.csv"
)

# Output folder inside Sub_Study_1
OUTPUT_FOLDER = os.path.join(
    DATA_FOLDER,
    "output"
)

# Creates the output folder if it does not already exist
os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)

# Output CSV
OUTPUT_CONTEXTS = os.path.join(
    OUTPUT_FOLDER,
    "kafkaesque_local_contexts_all_six_books.csv"
)

# Name of the column containing the unique review identifier
REVIEW_ID_COL = "review_id"

# Name of the column containing the Kafka work associated with each review
BOOK_COL = "book_title"

# Name of the column containing the preprocessed review text
CLEAN_TEXT_COL = "clean_text"


df = pd.read_csv(
    INPUT_CSV,
    encoding="utf-8-sig"
)

print("Input file:")
print(INPUT_CSV)

print("\nNumber of reviews:")
print(len(df))


print("\nReviews by book:")
print(df[BOOK_COL].value_counts())


# This code snippet creates a regular-expression pattern for identifying
# Kafkaesque-related terms in the cleaned review text
#
# The pattern identifies forms such as:
#   kafkaesque
#   kafka-esque
#   kafkaesques
#   kafkaesquely
#   kafka-esqueness
#   kafkaian

keyword_pattern = re.compile(
    r"\b(kafka(?:-?esque\w*|ian))\b",
    re.IGNORECASE
)

# This code snippet divides an individual review into sentences
# The text is split when a period, question mark, or exclamation mark is followed by whitespace
def split_into_sentences(text):
    sentences = re.split(
        r"(?<=[.!?])\s+",
        str(text)
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


# In this code snippet, the sentence containing the Kafkaesque keyword is extracted 
# together with the sentence immediately before and after it, where available, referred to as the local context
# In other words:
# Local context = previous sentence + keyword sentence + following sentence

local_rows = []

for _, row in df.iterrows():

    review_id = row[REVIEW_ID_COL]
    book_title = row[BOOK_COL]
    clean_text = row[CLEAN_TEXT_COL]

    sentences = split_into_sentences(clean_text)

    for sentence_index, sentence in enumerate(sentences):

        match = keyword_pattern.search(sentence)

        if not match:
            continue

        keyword = match.group(0)

        start_index = max(
            0,
            sentence_index - 1
        )

        end_index = min(
            len(sentences),
            sentence_index + 2
        )

        local_context = " ".join(
            sentences[start_index:end_index]
        )

        local_rows.append({
            "review_id": review_id,
            "book_title": book_title,
            "keyword": keyword,
            "keyword_sentence": sentence,
            "local_context": local_context
        })



local_df = pd.DataFrame(local_rows)


print("\nNumber of local contexts:")
print(len(local_df))

print("\nLocal contexts by book:")
print(local_df["book_title"].value_counts())

print("\nKeyword variants:")
print(
    local_df["keyword"]
    .str.lower()
    .value_counts()
)


# Saves the local contexts
local_df.to_csv(
    OUTPUT_CONTEXTS,
    index=False,
    encoding="utf-8-sig"
)

print("\nSaved local contexts to:")
print(OUTPUT_CONTEXTS)