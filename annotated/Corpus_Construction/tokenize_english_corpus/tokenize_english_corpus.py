import os
import re 
import html 
import pandas as pd 


# Folder where this Python script is located
DATA_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)

INPUT_CSV = os.path.abspath(
    os.path.join(
        DATA_FOLDER,
        "..",
        "create_english_corpus",
        "output",
        "kafka_english_corpus.csv"
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

OUTPUT_CSV = os.path.join(
    OUTPUT_FOLDER,
    "kafka_english_corpus_tokenized.csv"
)

TEXT_COL = "text" 
 
 
df = pd.read_csv(INPUT_CSV) 
 
if "review_id" not in df.columns: 
    df["review_id"] = range(1, len(df) + 1) 
 
# Cleans the original review text before tokenization 
def clean_text(text): 
    text = html.unescape(str(text)) 
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.IGNORECASE) 
    text = re.sub(r"<[^>]+>", " ", text) 
    text = re.sub(r"http\S+|www\.\S+", " ", text) 
    text = re.sub(r"\s+", " ", text).strip() 
    return text 
 
# Tokenizes the cleaned review text 
def tokenize(text): 
    return re.findall(r"\b[a-z]+(?:'[a-z]+)?\b", text.lower()) 
 
 
df["clean_text"] = df[TEXT_COL].apply(clean_text) 
df["tokens"] = df["clean_text"].apply(tokenize) 
df["token_count"] = df["tokens"].apply(len) 
 
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig") 
 
print("Reviews:", len(df)) 
print("Saved:", OUTPUT_CSV)