import os
import re
import ast
import pandas as pd
import matplotlib.pyplot as plt


# Folder where this Python script is located
DATA_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)

INPUT_CSV = os.path.abspath(
    os.path.join(
        DATA_FOLDER,
        "..",
        "tokenize_english_corpus",
        "output",
        "kafka_english_corpus_tokenized.csv"
    )
)

OUTPUT_FOLDER = os.path.join(
    DATA_FOLDER,
    "output"
)

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


TEXT_COL = "text"
CLEAN_TEXT_COL = "clean_text"
BOOK_COL = "book_title"
TOKENS_COL = "tokens"
LENGTH_COL = "token_count"

# threshold used to identify very short reviews.
SHORT_LIMIT = 10

BOOK_ORDER = [
    "Metamorphosis",
    "The Trial",
    "The Castle",
    "Amerika",
    "In the Penal Colony",
    "A Hunger Artist"
]


OUTPUT_DESCRIPTIVE = os.path.join(
    OUTPUT_FOLDER,
    "corpus_descriptive_statistics.csv"
)


OUTPUT_KEYWORD_REVIEWS = os.path.join(
    OUTPUT_FOLDER,
    "kafkaesque_keyword_reviews_all_books.csv"
)


OUTPUT_FREQUENCY = os.path.join(
    OUTPUT_FOLDER,
    "kafkaesque_keyword_frequency_by_book.csv"
)


OUTPUT_MAIN = os.path.join(
    OUTPUT_FOLDER,
    "kafkaesque_main_comparable_corpus.csv"
)


OUTPUT_KEYWORD_BOXPLOT = os.path.join(
    OUTPUT_FOLDER,
    "boxplot_kafkaesque_review_lengths.png"
)


# Keyword pattern
KEYWORD_PATTERN = r"\b(kafka(?:-?esque\w*|ian))\b"


df = pd.read_csv(
    INPUT_CSV,
    encoding="utf-8-sig"
)


original_count = len(df)


df[LENGTH_COL] = pd.to_numeric(
    df[LENGTH_COL],
    errors="coerce"
)


df[BOOK_COL] = (
    df[BOOK_COL]
    .astype("string")
    .str.strip()
)


def parse_tokens(value):

    if isinstance(value, list):
        return value

    if pd.isna(value):
        return []

    try:
        parsed = ast.literal_eval(
            str(value)
        )

        if isinstance(parsed, list):
            return parsed

    except (
        ValueError,
        SyntaxError
    ):
        pass

    return []


df["_token_list"] = (
    df[TOKENS_COL]
    .apply(parse_tokens)
)


# Calculates basic corpus statistics
def corpus_statistics(
    corpus_df,
    corpus_name
):

    total_tokens = int(
        corpus_df[LENGTH_COL].sum()
    )

    unique_types = set()

    for token_list in corpus_df[
        "_token_list"
    ]:
        unique_types.update(
            token_list
        )

    return {
        "corpus": corpus_name,
        "reviews": len(corpus_df),
        "tokens": total_tokens,
        "types": len(unique_types),
        "Mean review length (tokens)": round(
            corpus_df[LENGTH_COL].mean(),
            2
        )
    }


descriptive_rows = [
    corpus_statistics(
        df,
        "Entire corpus"
    )
]


for book in BOOK_ORDER:

    book_df = df.loc[
        df[BOOK_COL] == book
    ]

    if not book_df.empty:

        descriptive_rows.append(
            corpus_statistics(
                book_df,
                book
            )
        )


descriptive_df = pd.DataFrame(
    descriptive_rows
)


print(
    "\nCorpus descriptive statistics:"
)

print(
    descriptive_df.to_string(
        index=False
    )
)


descriptive_df.to_csv(
    OUTPUT_DESCRIPTIVE,
    index=False,
    encoding="utf-8-sig"
)



# Identifies reviews that contain all information required for subsequent textual analysis such as:
# cleaned text, book title, and review length.
usable_mask = (
    df[CLEAN_TEXT_COL].notna()
    & df[BOOK_COL].notna()
    & df[LENGTH_COL].notna()
)


textual_df = df.loc[
    usable_mask
].copy()


textual_df[TEXT_COL] = (
    textual_df[TEXT_COL]
    .fillna("")
    .astype(str)
)


textual_df[CLEAN_TEXT_COL] = (
    textual_df[CLEAN_TEXT_COL]
    .astype(str)
    .str.strip()
)


textual_df[LENGTH_COL] = (
    textual_df[LENGTH_COL]
    .astype(int)
)


# Removes entries with no remaining textual content just in case any empty strings remaing after cleaning
textual_df = textual_df.loc[
    textual_df[CLEAN_TEXT_COL] != ""
].copy()


removed_count = (
    original_count - len(textual_df)
)


print(
    "\nReviews removed before textual analysis: "
    f"{removed_count}"
)

print(
    "\nUsable reviews for textual analysis:"
)

print(len(textual_df))



textual_df["keyword"] = textual_df[
    CLEAN_TEXT_COL
].str.extract(
    KEYWORD_PATTERN,
    flags=re.IGNORECASE,
    expand=False
)


keyword_df = textual_df.loc[
    textual_df["keyword"].notna()
].copy()


keyword_df["keyword"] = (
    keyword_df["keyword"]
    .astype(str)
    .str.lower()
)


if keyword_df.empty:
    raise ValueError(
        "No Kafkaesque keyword variants were found."
    )


print(
    "\nKafkaesque keyword reviews:"
)

print(len(keyword_df))


print(
    "\nDetected keyword variants:"
)

print(
    keyword_df[
        "keyword"
    ].value_counts()
)



# Does keyword frequency by book
all_review_counts = (
    textual_df.groupby(
        BOOK_COL
    )
    .size()
    .rename(
        "all_reviews"
    )
)


keyword_counts = (
    keyword_df.groupby(
        BOOK_COL
    )
    .size()
    .rename(
        "keyword_reviews"
    )
)


book_frequency = pd.concat(
    [
        all_review_counts,
        keyword_counts
    ],
    axis=1
).fillna(0)


book_frequency[
    [
        "all_reviews",
        "keyword_reviews"
    ]
] = (
    book_frequency[
        [
            "all_reviews",
            "keyword_reviews"
        ]
    ]
    .astype(int)
)


book_frequency[
    "keyword_rate_percent"
] = (
    book_frequency[
        "keyword_reviews"
    ]
    /
    book_frequency[
        "all_reviews"
    ]
    * 100
).round(2)


book_frequency = (
    book_frequency
    .sort_values(
        "keyword_rate_percent",
        ascending=False
    )
    .reset_index()
)


print(
    "\nKeyword frequency by book:"
)

print(
    book_frequency.to_string(
        index=False
    )
)


book_frequency.to_csv(
    OUTPUT_FREQUENCY,
    index=False,
    encoding="utf-8-sig"
)



# Calculates the mean review length among all Kafkaesque-containing reviews.
mean_length = (
    keyword_df[
        LENGTH_COL
    ].mean()
)

median_length = (
    keyword_df[
        LENGTH_COL
    ].median()
)

q1 = (
    keyword_df[
        LENGTH_COL
    ].quantile(0.25)
)

q3 = (
    keyword_df[
        LENGTH_COL
    ].quantile(0.75)
)

iqr = (
    q3 - q1
)

upper_bound = (
    q3
    + 1.5 * iqr
)


print(
    "\nKafkaesque review-length statistics:"
)

print(
    f"Reviews: {len(keyword_df)}"
)

print(
    f"Mean: {mean_length:.2f} tokens"
)

print(
    f"Median: {median_length:.2f} tokens"
)

print(
    f"Q1: {q1:.2f}"
)

print(
    f"Q3: {q3:.2f}"
)

print(
    f"IQR: {iqr:.2f}"
)

print(
    "Upper boundary: "
    f"{upper_bound:.2f} tokens"
)


# Creates a horizontal boxplot showing the length distribution of all Kafkaesque-containing reviews.
fig, ax = plt.subplots(
    figsize=(12, 4)
)

ax.boxplot(
    [
        keyword_df[
            LENGTH_COL
        ]
    ],
    tick_labels=[
        "Kafkaesque reviews"
    ],
    vert=False,
    showmeans=True,
    showfliers=True
)


ax.axvline(
    SHORT_LIMIT,
    linestyle="--",
    label="Lower cutoff (10 tokens)"
)


ax.axvline(
    upper_bound,
    linestyle=":",
    label=(
        "Upper IQR cutoff "
        f"({upper_bound:.0f} tokens)"
    )
)


ax.set_title(
    "Length Distribution of "
    "Kafkaesque Keyword Reviews"
)

ax.set_xlabel(
    "Tokens per Review"
)

ax.legend()

ax.grid(
    axis="x",
    linestyle="--",
    alpha=0.5
)

plt.tight_layout()

plt.savefig(
    OUTPUT_KEYWORD_BOXPLOT,
    dpi=300,
    bbox_inches="tight"
)

plt.close()



# Main comparable corpus
main_df = keyword_df.loc[
    (
        keyword_df[LENGTH_COL]
        > SHORT_LIMIT
    )
    &
    (
        keyword_df[LENGTH_COL]
        <= upper_bound
    )
].copy()


output_columns = [
    "review_id",
    BOOK_COL,
    TEXT_COL,
    CLEAN_TEXT_COL,
    LENGTH_COL,
    "keyword"
]


keyword_output = keyword_df[
    output_columns
].copy()

main_output = main_df[
    output_columns
].copy()



keyword_output.to_csv(
    OUTPUT_KEYWORD_REVIEWS,
    index=False,
    encoding="utf-8-sig"
)

main_output.to_csv(
    OUTPUT_MAIN,
    index=False,
    encoding="utf-8-sig"
)


# Final summary
print("\nDone.")

print(
    "\nCorpus development:"
)

print(
    f"Original English corpus: "
    f"{original_count}"
)

print(
    f"Reviews removed before textual analysis: "
    f"{removed_count}"
)

print(
    f"Usable textual reviews: "
    f"{len(textual_df)}"
)

print(
    f"Kafkaesque keyword reviews: "
    f"{len(keyword_df)}"
)

print(
    f"Main comparable corpus: "
    f"{len(main_df)}"
)


print(
    "\nCreated files:"
)

output_files = [
    OUTPUT_DESCRIPTIVE,
    OUTPUT_KEYWORD_REVIEWS,
    OUTPUT_FREQUENCY,
    OUTPUT_KEYWORD_BOXPLOT,
    OUTPUT_MAIN
]

for output_file in output_files:
    print(
        f"- {output_file}"
    )