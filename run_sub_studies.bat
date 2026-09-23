@echo off
setlocal

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "CORPUS=%ROOT%annotated\Corpus_Construction"
set "SUB1=%ROOT%annotated\Sub_Study_1"
set "SUB3=%ROOT%annotated\Sub_Study_3"

if not exist "%PYTHON%" (
    echo ERROR: Could not find the virtual environment at "%PYTHON%".
    echo Create it with: python -m venv .venv
    exit /b 1
)

if not exist "%CORPUS%\keyword_and_length_analysis\output\kafkaesque_main_comparable_corpus.csv" (
    echo The corpus output is missing. Running corpus construction first...
    call "%ROOT%run_corpus.bat"
    if errorlevel 1 exit /b 1
)

if not exist "%SUB1%\input" mkdir "%SUB1%\input"
if not exist "%SUB1%\input\kafkaesque_main_comparable_corpus.csv" (
    copy /y "%CORPUS%\keyword_and_length_analysis\output\kafkaesque_main_comparable_corpus.csv" "%SUB1%\input\kafkaesque_main_comparable_corpus.csv" >nul
)

if not exist "%SUB1%\output\kafkaesque_local_contexts_all_six_books.csv" (
    echo Extracting local contexts...
    "%PYTHON%" "%SUB1%\local_context_extraction.py"
    if errorlevel 1 exit /b 1
) else (
    echo Skipping local-context extraction: output already exists.
)

set "NEED_COLLOCATION="
for %%F in (
    all_six_books_collocations_pmi.csv
    all_six_books_collocations_pmi_top40.png
) do if not exist "%SUB1%\output\%%F" set "NEED_COLLOCATION=1"

if defined NEED_COLLOCATION (
    echo Running collocation analysis...
    "%PYTHON%" "%SUB1%\collocation_analysis.py"
    if errorlevel 1 exit /b 1
) else (
    echo Skipping collocation analysis: all outputs already exist.
)

if not exist "%SUB1%\output\bertopic_barchart.html" (
    echo Running BERTopic analysis...
    "%PYTHON%" "%SUB1%\bertopic_analysis.py"
    if errorlevel 1 exit /b 1
) else (
    echo Skipping BERTopic analysis: output already exists.
)

if not exist "%CORPUS%\tokenize_english_corpus\output\kafka_english_corpus_tokenized.csv" (
    echo ERROR: The tokenized corpus is missing.
    exit /b 1
)

if not exist "%SUB3%\input" mkdir "%SUB3%\input"
if not exist "%SUB3%\input\kafka_english_corpus_tokenized.csv" (
    copy /y "%CORPUS%\tokenize_english_corpus\output\kafka_english_corpus_tokenized.csv" "%SUB3%\input\kafka_english_corpus_tokenized.csv" >nul
)

set "NEED_AUTHORS="
for %%F in (
    metamorphosis_gliner_entities_raw.csv
    metamorphosis_canonical_entity_counts.csv
) do if not exist "%SUB3%\output\%%F" set "NEED_AUTHORS=1"

if defined NEED_AUTHORS (
    echo Running author mention extraction...
    "%PYTHON%" "%SUB3%\author_analysis.py"
    if errorlevel 1 exit /b 1
) else (
    echo Skipping author mention extraction: all outputs already exist.
)

echo Sub-studies complete. Sub-Study 2 has no executable script in this repository.
exit /b 0