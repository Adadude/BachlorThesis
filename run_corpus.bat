@echo off
setlocal

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "CORPUS=%ROOT%annotated\Corpus_Construction"

if not exist "%PYTHON%" (
    echo ERROR: Could not find the virtual environment at "%PYTHON%".
    echo Create it with: python -m venv .venv
    exit /b 1
)

if not exist "%ROOT%KafkaCSV.zip" (
    echo ERROR: Could not find "%ROOT%KafkaCSV.zip".
    exit /b 1
)

set "NEED_LANGUAGE="
for %%F in (
    GoodreadsKafkaAmerikaReviews_annotated_confidence.csv
    GoodreadsKafkaCastleReviews_annotated_confidence.csv
    GoodreadsKafkaHungerArtistReviews_annotated_confidence.csv
    GoodreadsKafkaMetamorphosisReviews_annotated_confidence.csv
    GoodreadsKafkaPenalColonyReviews_annotated_confidence.csv
    GoodreadsKafkaTrialReviews_annotated_confidence.csv
) do if not exist "%CORPUS%\language_detection\output\%%F" set "NEED_LANGUAGE=1"

if defined NEED_LANGUAGE (
    echo Running language detection...
    "%PYTHON%" "%CORPUS%\language_detection\language_detection.py"
    if errorlevel 1 exit /b 1
) else (
    echo Skipping language detection: all outputs already exist.
)

if not exist "%CORPUS%\create_english_corpus\output\kafka_english_corpus.csv" (
    echo Creating the English corpus...
    "%PYTHON%" "%CORPUS%\create_english_corpus\create_english_corpus.py"
    if errorlevel 1 exit /b 1
) else (
    echo Skipping English corpus creation: output already exists.
)

if not exist "%CORPUS%\tokenize_english_corpus\output\kafka_english_corpus_tokenized.csv" (
    echo Tokenizing the English corpus...
    "%PYTHON%" "%CORPUS%\tokenize_english_corpus\tokenize_english_corpus.py"
    if errorlevel 1 exit /b 1
) else (
    echo Skipping tokenization: output already exists.
)

set "NEED_ANALYSIS="
for %%F in (
    corpus_descriptive_statistics.csv
    kafkaesque_keyword_reviews_all_books.csv
    kafkaesque_keyword_frequency_by_book.csv
    kafkaesque_main_comparable_corpus.csv
    boxplot_kafkaesque_review_lengths.png
) do if not exist "%CORPUS%\keyword_and_length_analysis\output\%%F" set "NEED_ANALYSIS=1"

if defined NEED_ANALYSIS (
    echo Running keyword and length analysis...
    "%PYTHON%" "%CORPUS%\keyword_and_length_analysis\keyword_and_length_analysis.py"
    if errorlevel 1 exit /b 1
) else (
    echo Skipping keyword and length analysis: all outputs already exist.
)

if not exist "%CORPUS%\boxplot\output\boxplot_review_length_entire_and_books.png" (
    echo Creating the review-length boxplot...
    "%PYTHON%" "%CORPUS%\boxplot\boxplot.py"
    if errorlevel 1 exit /b 1
) else (
    echo Skipping review-length boxplot: output already exists.
)

echo Corpus construction complete.
exit /b 0