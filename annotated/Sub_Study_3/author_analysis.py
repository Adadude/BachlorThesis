import os
import re
 
import pandas as pd
import torch
from tqdm import tqdm
from gliner import GLiNER
 

# Folder where this Python script is located
DATA_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)

INPUT_FILE = os.path.join(
    DATA_FOLDER,
    "input",
    "kafka_english_corpus_tokenized.csv"
)

OUTPUT_FOLDER = os.path.join(
    DATA_FOLDER,
    "output"
)

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)

TEXT_COL = "clean_text"
BOOK_COL = "book_title"

OUTPUT_RAW = os.path.join(
    OUTPUT_FOLDER,
    "metamorphosis_gliner_entities_raw.csv"
)

OUTPUT_CANONICAL = os.path.join(
    OUTPUT_FOLDER,
    "metamorphosis_canonical_entity_counts.csv"
)
 
# Minimum GLiNER confidence score required for an entity to be retained
THRESHOLD = 0.50
 
MODEL_NAME = "urchade/gliner_small-v2.1"
 
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
 
# Faster batching
BATCH_SIZE = 64 if DEVICE == "cuda" else 16
OUTER_BATCH_SIZE = 1024
 
 
df = pd.read_csv(INPUT_FILE)
 
# Restrict the corpus to reviews of The Metamorphosis
df = df[
    df[BOOK_COL]
    .astype(str)
    .str.contains("metamorphosis", case=False, na=False)
].copy()
 
df[TEXT_COL] = df[TEXT_COL].fillna("").astype(str)
df = df[df[TEXT_COL].str.strip().ne("")]
 
df = df.drop_duplicates(
    subset=[TEXT_COL]
).reset_index(drop=True)
 
print("Metamorphosis reviews:", len(df))
print("Device:", DEVICE)
print("Batch size:", BATCH_SIZE)
 
 
print("Loading GLiNER...")
 
# Loads the pretrained GLiNER model for zero-shot entity extraction
model = GLiNER.from_pretrained(
    MODEL_NAME,
    map_location=DEVICE
)
 
model.eval()
 
print("GLiNER loaded.")
 
# Instructs GLiNER to identify "author" entities
labels = [
    "author"
]
 
 
# Splits long reviews into chunks of up to 250 words, which makes the texts easier and more efficient for GLiNER to process
def split_review(text, words_per_chunk=250):
    words = text.split()
 
    return [
        " ".join(words[start:start + words_per_chunk])
        for start in range(0, len(words), words_per_chunk)
    ]
 
# Cleans the entity detected by GLiNER by removing punctuation and unnecessary whitespace
def clean_entity(name):
    name = str(name).strip()
    name = re.sub(r"^[^\w]+|[^\w]+$", "", name)
    name = re.sub(r"\s+", " ", name)
    return name
 
# Extracts a short surrounding text around each detected author, which allows the detections to be inspected later
def create_context(text, start, end, window=120):
    left = max(0, start - window)
    right = min(len(text), end + window)
 
    return (
        text[left:right]
        .replace("\n", " ")
        .strip()
    )
 
 
def predict_batch(texts):
    with torch.inference_mode():
 
        if hasattr(model, "inference"):
            return model.inference(
                texts,
                labels,
                threshold=THRESHOLD,
                batch_size=BATCH_SIZE
            )
 
        return model.batch_predict_entities(
            texts,
            labels,
            threshold=THRESHOLD,
            batch_size=BATCH_SIZE
        )
 
 
items = []
 
for row in df.itertuples(index=False):
 
    text = getattr(row, TEXT_COL)
    review_id = getattr(row, "review_id")
    book = getattr(row, BOOK_COL)
 
    for chunk_number, chunk in enumerate(
        split_review(text),
        start=1
    ):
        items.append({
            "review_id": review_id,
            "book": book,
            "chunk_number": chunk_number,
            "text": chunk
        })
 
 
# Groups similarly sized texts together, which reduces unnecessary padding during inference
items.sort(key=lambda x: len(x["text"]))
 
print("Text chunks to analyse:", len(items))
 
 
# Stores all retained author detections
records = []
 
for start_position in tqdm(
    range(0, len(items), OUTER_BATCH_SIZE),
    desc="Analysing review batches"
):
 
    item_batch = items[
        start_position:
        start_position + OUTER_BATCH_SIZE
    ]
 
    text_batch = [
        item["text"]
        for item in item_batch
    ]
 
    prediction_batch = predict_batch(text_batch)
 
    for item, entities in zip(
        item_batch,
        prediction_batch
    ):
 
        for entity in entities:
 
            extracted = clean_entity(
                entity.get("text", "")
            )
 
            if not extracted:
                continue
 
            entity_start = entity.get("start", 0)
            entity_end = entity.get(
                "end",
                entity_start
            )
 
            records.append({
                "review_id": item["review_id"],
                "book": item["book"],
                "chunk_number": item["chunk_number"],
                "extracted_entity": extracted,
                "normalized_entity": extracted.casefold(),
                "entity_label": entity.get("label", ""),
                "score": round(
                    float(entity.get("score", 0)),
                    3
                ),
                "context": create_context(
                    item["text"],
                    entity_start,
                    entity_end
                )
            })
 
 
entities_df = pd.DataFrame(records)
 
entities_df.to_csv(
    OUTPUT_RAW,
    index=False,
    encoding="utf-8-sig"
)
 
print("Extracted mentions:", len(entities_df))
print("Saved:", OUTPUT_RAW)
 
 
if not entities_df.empty:

    AUTHOR_ALIASES = {
        "kafka": "Franz Kafka",
        "franz kafka": "Franz Kafka",
        "kafkas": "Franz Kafka",
        "franz kafkas": "Franz Kafka",
        "mr kafka": "Franz Kafka",
        "mr. kafka": "Franz Kafka",
        "sir franz kafka": "Franz Kafka",
        "franz kakfa": "Franz Kafka",
        "franza kafka": "Franz Kafka",
        "frank kafka": "Franz Kafka",

        "camus": "Albert Camus",
        "albert camus": "Albert Camus",

        "nabokov": "Vladimir Nabokov",
        "vladimir nabokov": "Vladimir Nabokov",
        "vladamir nabokov": "Vladimir Nabokov",

        "murakami": "Haruki Murakami",
        "haruki murakami": "Haruki Murakami",

        "dostoevsky": "Fyodor Dostoevsky",
        "dostoyevsky": "Fyodor Dostoevsky",
        "fyodor dostoevsky": "Fyodor Dostoevsky",
        "fyodor dostoyevsky": "Fyodor Dostoevsky",

        "orwell": "George Orwell",
        "george orwell": "George Orwell",

        "gogol": "Nikolai Gogol",
        "nikolai gogol": "Nikolai Gogol",

        "ovid": "Ovid",

        "sartre": "Jean-Paul Sartre",
        "jean-paul sartre": "Jean-Paul Sartre",
        "gean paul sartre": "Jean-Paul Sartre",

        "gabriel garcía márquez": "Gabriel García Márquez",
        "gabriel garcia marquez": "Gabriel García Márquez",
        "garcía márquez": "Gabriel García Márquez",
        "garcia marquez": "Gabriel García Márquez",

        "marx": "Karl Marx",
        "karl marx": "Karl Marx",

        "nietzsche": "Friedrich Nietzsche",
        "friedrich nietzsche": "Friedrich Nietzsche",

        "gregor": "Gregor Samsa",
        "gregor samsa": "Gregor Samsa",
        "gegor": "Gregor Samsa",
        "geogor": "Gregor Samsa"
    }
    entities_df["canonical_entity"] = (
    entities_df["normalized_entity"]
    .map(AUTHOR_ALIASES)
    .fillna(entities_df["extracted_entity"])
)

    canonical_df = entities_df.copy()

    canonical_counts = (
        canonical_df
        .groupby("canonical_entity")
        .agg(
            mentions=(
                "canonical_entity",
                "size"
            ),
            reviews=(
                "review_id",
                "nunique"
            ),
            average_score=(
                "score",
                "mean"
            ),
            example_context=(
                "context",
                "first"
            )
        )
        .reset_index()
        .sort_values(
            ["mentions", "reviews"],
            ascending=False
        )
    )

    canonical_counts["average_score"] = (
        canonical_counts["average_score"]
        .round(3)
    )

    canonical_counts.to_csv(
        OUTPUT_CANONICAL,
        index=False,
        encoding="utf-8-sig"
    )

    print("Saved:", OUTPUT_CANONICAL)

    print(
        canonical_counts
        .to_string(index=False)
    )
 
else:
    print("No entities were extracted.")