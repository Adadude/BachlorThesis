from bertopic import BERTopic
from umap import UMAP
from sentence_transformers import SentenceTransformer

import os
import pandas as pd

from sklearn.feature_extraction.text import (
    CountVectorizer,
    ENGLISH_STOP_WORDS
)

DATA_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)

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

OUTPUT_GRAPH = os.path.join(
    OUTPUT_FOLDER,
    "bertopic_barchart.html"
)

TEXT_COL = "local_context"

RANDOM_SEED = 42

MIN_DF = 2

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


df = pd.read_csv(
    INPUT_CSV,
    encoding="utf-8-sig"
)
docs = (
    df[TEXT_COL]
    .astype(str)
    .tolist()
)

print("Number of local contexts:")
print(len(docs))

# Stopwords and other common words
STOPWORDS = set(
    ENGLISH_STOP_WORDS
).union({

    "kafkaesque",
    "kafka",
    "kafkaesk",
    "kafkaian",
    "kafkaesqued",
    "kafkaesquely",
    "kafkaesques",
    "kafkaesqueity",
    "esque",

    "br",

    "read",
    "reading",
    "book",
    "story",

    "like",
    "just",
    "im"
})


vectorizer_model = CountVectorizer(
    ngram_range=(1, 2),
    stop_words=list(STOPWORDS),
    min_df=MIN_DF
)


sentence_model = SentenceTransformer(
    EMBEDDING_MODEL_NAME
)

embeddings = sentence_model.encode(
    docs,
    show_progress_bar=True
)


umap_model = UMAP(
    n_neighbors=15,
    n_components=5,
    min_dist=0.0,
    metric="cosine",
    random_state=RANDOM_SEED
)

topic_model = BERTopic(
    umap_model=umap_model,
    vectorizer_model=vectorizer_model,
    verbose=True
)

topics, _ = topic_model.fit_transform(
    docs,
    embeddings
)

fig = topic_model.visualize_barchart()

fig.show()

fig.write_html(
    OUTPUT_GRAPH
)

print("\nGraph saved as:")
print(OUTPUT_GRAPH)