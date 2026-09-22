import os
import zipfile
import pandas as pd
from collections import Counter
from langdetect import detect_langs, DetectorFactory, LangDetectException

# Makes language detection reproducible, as langdetect can otherwise return slightly different results between runs.
DetectorFactory.seed = 0

# Folder where this Python script is located
DATA_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)

ZIP_FILE = os.path.abspath(
    os.path.join(
        DATA_FOLDER,
        "..",
        "..",
        "..",
        "KafkaCSV.zip"
    )
)

OUTPUT_FOLDER = os.path.join(
    DATA_FOLDER,
    "output"
)

BOOK_FILES = [
    "GoodreadsKafkaAmerikaReviews.csv",
    "GoodreadsKafkaCastleReviews.csv",
    "GoodreadsKafkaHungerArtistReviews.csv",
    "GoodreadsKafkaMetamorphosisReviews.csv",
    "GoodreadsKafkaPenalColonyReviews.csv",
    "GoodreadsKafkaTrialReviews.csv"
]

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
all_language_counts = Counter()


def detect_language(text):
    #  Checks whether the review text contains a missing value such as NaN
    if pd.isna(text):
        return "unknown", 0.0, "empty"

    text = str(text).strip()

    # Checks whether the review is empty or consists only of whitespace.
    if not text:
        return "unknown", 0.0, "empty"

    # Checks whether the text contains at least one alphabetic character.
    if not any(character.isalpha() for character in text):
        return "unknown", 0.0, "no_letters"

    try:
        result = detect_langs(text)[0]

        note = "ok" if result.prob >= 0.80 else "uncertain"

        return result.lang, float(result.prob), note

    except LangDetectException:
        return "unknown", 0.0, "error"


with zipfile.ZipFile(ZIP_FILE) as zip_file:

    for file_name in BOOK_FILES:
        internal_path = f"csv/{file_name}"

        print(f"Reading: {file_name}")

        with zip_file.open(internal_path) as file:
            df = pd.read_csv(file, encoding="utf-8")

        df[
            ["language", "language_confidence", "language_note"]
        ] = df["text"].apply(
            lambda text: pd.Series(detect_language(text))
        )

        output_path = os.path.join(
            OUTPUT_FOLDER,
            file_name.replace(
                ".csv",
                "_annotated_confidence.csv"
            )
        )

        df.to_csv(
            output_path,
            index=False,
            encoding="utf-8-sig"
        )

        counts = df["language"].value_counts()
        all_language_counts.update(counts.to_dict())

        print(f"Saved: {output_path}")
        print(counts)
        print("-" * 50)


print("\nOverall language counts:")

for language, count in all_language_counts.most_common():
    print(f"{language}: {count}")