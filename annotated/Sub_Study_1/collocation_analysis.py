import os
import re
import math
from collections import Counter, defaultdict

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Folder where this Python script is located
DATA_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)

# Output folder inside Sub_Study_1
OUTPUT_FOLDER = os.path.join(
    DATA_FOLDER,
    "output"
)

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)

INPUT_CSV = os.path.join(
    OUTPUT_FOLDER,
    "kafkaesque_local_contexts_all_six_books.csv"
)

# Saves collocation results into the same output folder
OUTPUT_CSV = os.path.join(
    OUTPUT_FOLDER,
    "all_six_books_collocations_pmi.csv"
)

OUTPUT_PLOT = os.path.join(
    OUTPUT_FOLDER,
    "all_six_books_collocations_pmi_top40.png"
)

TEXT_COL = "local_context"
REVIEW_ID_COL = "review_id"

# Only bigrams occurring at least three times are included, which reduces the influence of very rare word combinations
MIN_BIGRAM_COUNT = 3

# Number of highest-PMI bigrams shown in the terminal and plot
TOP_N = 40

# Maximum number of local context examples stored for each bigram
MAX_EXAMPLE_CONTEXTS = 3


df = pd.read_csv(
    INPUT_CSV,
    encoding="utf-8-sig"
)

print("Number of local contexts:")
print(len(df))


sentence_rows = []

for _, row in df.iterrows():

    review_id = row[REVIEW_ID_COL]
    text = row[TEXT_COL]

    sentences = re.split(
        r"(?<=[.!?])\s+",
        str(text)
    )

    for sentence in sentences:

        sentence = sentence.strip()

        if sentence:

            sentence_rows.append({
                REVIEW_ID_COL: review_id,
                "sentence": sentence,
                TEXT_COL: text
            })


sentence_df = pd.DataFrame(
    sentence_rows
)

sentence_count_before = len(
    sentence_df
)

sentence_df = (
    sentence_df
    .drop_duplicates(
        subset=[
            REVIEW_ID_COL,
            "sentence"
        ]
    )
    .reset_index(drop=True)
)

sentence_count_after = len(
    sentence_df
)

print("\nSentences before removing overlap:")
print(sentence_count_before)

print("\nUnique sentences used for bigram analysis:")
print(sentence_count_after)

print("\nRepeated sentences removed:")
print(
    sentence_count_before
    - sentence_count_after
)


# Here we tokenize local contexts
def tokenize(text):

    text = str(text).lower()

    tokens = re.findall(
        r"\b[a-z]+(?:'[a-z]+)?\b",
        text
    )

    return tokens


# Here we create and count the bigrams
all_tokens = []
all_bigrams = []

# Stores only a few example contexts for each bigram
example_contexts = defaultdict(list)


for _, row in sentence_df.iterrows():

    sentence = row["sentence"]
    text = row[TEXT_COL]

    tokens = tokenize(sentence)

    all_tokens.extend(tokens)

    for position in range(len(tokens) - 1):

        word1 = tokens[position]
        word2 = tokens[position + 1]

        bigram = (word1, word2)

        all_bigrams.append(bigram)

        # Keeps at most three example contexts
        if (
            len(example_contexts[bigram])
            < MAX_EXAMPLE_CONTEXTS
            and text not in example_contexts[bigram]
        ):
            example_contexts[bigram].append(text)


# Counts individual words and bigrams
unigram_counts = Counter(all_tokens)
bigram_counts = Counter(all_bigrams)

total_unigrams = sum(
    unigram_counts.values()
)

total_bigrams = sum(
    bigram_counts.values()
)


print("\nTotal words:")
print(total_unigrams)

print("\nTotal bigrams:")
print(total_bigrams)



# In this code snippet, the PMI is calculated
# Only bigrams occurring at least 3 times are included in the final results

rows = []


for (word1, word2), bigram_count in bigram_counts.items():

    if bigram_count < MIN_BIGRAM_COUNT:
        continue

    p_word1 = (
        unigram_counts[word1]
        / total_unigrams
    )

    p_word2 = (
        unigram_counts[word2]
        / total_unigrams
    )

    p_bigram = (
        bigram_count
        / total_bigrams
    )

    pmi = math.log2(
        p_bigram
        / (p_word1 * p_word2)
    )

    contexts = example_contexts[
        (word1, word2)
    ]

    rows.append({
        "bigram": f"{word1} {word2}",
        "bigram_count": bigram_count,
        "pmi": pmi,
        "example_contexts": " ||| ".join(
            contexts
        )
    })


collocation_df = pd.DataFrame(rows)

if collocation_df.empty:
    raise ValueError(
        "No bigrams met the minimum frequency "
        f"threshold of {MIN_BIGRAM_COUNT}."
    )


collocation_df = (
    collocation_df
    .sort_values(
        [
            "pmi",
            "bigram_count"
        ],
        ascending=[
            False,
            False
        ]
    )
    .reset_index(drop=True)
)


print("\nTop PMI bigrams:")

print(
    collocation_df[
        [
            "bigram",
            "bigram_count",
            "pmi"
        ]
    ]
    .head(TOP_N)
    .to_string(index=False)
)


collocation_df.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig"
)

print("\nSaved collocation results:")
print(OUTPUT_CSV)


# This code snippet plots the top 40 PMI-ranked bigrams
plot_df = (
    collocation_df
    .head(TOP_N)
    .copy()
)

sns.set_theme(
    style="whitegrid"
)

plt.figure(
    figsize=(10, 8)
)

sns.barplot(
    data=plot_df,
    x="pmi",
    y="bigram",
    color="#BFF400"
)

plt.title(
    "Top PMI Bigrams in Kafkaesque "
    "Local Contexts: All Six Books",
    fontsize=16,
    weight="bold"
)

plt.xlabel(
    "PMI score"
)

plt.ylabel(
    "Bigram"
)

plt.tight_layout()

plt.savefig(
    OUTPUT_PLOT,
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


print("\nSaved plot:")
print(OUTPUT_PLOT)