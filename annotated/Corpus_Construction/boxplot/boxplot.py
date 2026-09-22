import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D


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

OUTPUT_BOOK_BOXPLOT = os.path.join(
    OUTPUT_FOLDER,
    "boxplot_review_length_entire_and_books.png"
)

BOOK_COL = "book_title"
LENGTH_COL = "token_count"


df = pd.read_csv(
    INPUT_CSV,
    encoding="utf-8-sig"
)

if BOOK_COL not in df.columns:
    raise ValueError(f"Column '{BOOK_COL}' not found.")

if LENGTH_COL not in df.columns:
    raise ValueError(f"Column '{LENGTH_COL}' not found.")



# Converts token counts into numeric values
df[LENGTH_COL] = pd.to_numeric(
    df[LENGTH_COL],
    errors="coerce"
)

df = df.dropna(
    subset=[BOOK_COL, LENGTH_COL]
).copy()

df[BOOK_COL] = (
    df[BOOK_COL]
    .astype(str)
    .str.strip()
)

df[LENGTH_COL] = df[LENGTH_COL].astype(int)


# Calculates the median review length for each Kafka work and orders the books from the lowest to the highest median
book_order = (
    df.groupby(BOOK_COL)[LENGTH_COL]
    .median()
    .sort_values()
    .index
    .tolist()
)



# Creates the labels for the boxplot
# The individual Kafka works are ordered by their median review length, followed by the entire corpus.
plot_labels = book_order + ["Entire corpus"]

plot_data = [
    df.loc[
        df[BOOK_COL] == book,
        LENGTH_COL
    ]
    for book in book_order
]

plot_data.append(
    df[LENGTH_COL]
)


# Creates the boxplot
legend_elements = [
    mpatches.Patch(
        facecolor="lightblue",
        edgecolor="black",
        label="IQR (25th–75th percentile)"
    ),
    Line2D(
        [0],
        [0],
        color="orange",
        linewidth=2,
        label="Median"
    ),
    Line2D(
        [0],
        [0],
        marker="^",
        color="green",
        linestyle="None",
        markersize=9,
        label="Mean"
    ),
    Line2D(
        [0],
        [0],
        marker="x",
        color="black",
        linestyle="None",
        markersize=6,
        label="Outliers"
    )
]

plt.figure(figsize=(13, max(7, len(plot_labels) * 0.8)))

boxplot = plt.boxplot(
    plot_data,
    tick_labels=plot_labels,
    vert=False,
    showfliers=True,
    showmeans=True,
    patch_artist=True,
    flierprops={
        "marker": "x",
        "markersize": 6,
        "markeredgecolor": "black"
    },
    meanprops={
        "marker": "^",
        "markerfacecolor": "green",
        "markeredgecolor": "green"
    },
    medianprops={
        "color": "orange",
        "linewidth": 2
    }
)

for box in boxplot["boxes"]:
    box.set_facecolor("lightblue")

plt.legend(
    handles=legend_elements,
    loc="lower right"
)

plt.title("Review Length Distribution in the English Kafka Corpus")
plt.xlabel("Tokens per Review")
plt.ylabel("Corpus")
plt.grid(axis="x", linestyle="--", alpha=0.5)
plt.tight_layout()

plt.savefig(
    OUTPUT_BOOK_BOXPLOT,
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

print(f"Saved: {OUTPUT_BOOK_BOXPLOT}")