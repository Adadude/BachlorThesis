# GLiNER author mention extraction 

(Using the English Goodreads reviews corpus of The Metamorphosis)

Model: GLiNER Small v2.1 (`urchade/gliner_small-v2.1`)

Input: English Goodreads reviews of The Metamorphosis from the csv file "kafka_english_corpus_tokenized.csv" which is found within the "input" folder located in sub-study 3 

This script identifies and counts "author" mentions in Goodreads reviews of The Metamorphosis using the zero-shot Named Entity Recognition model GLiNER Small v2.1. The corpus is first restricted to reviews of The Metamorphosis, empty and duplicate review texts are removed, and the remaining reviews are split into chunks of up to 250 words for better processing due to the long length of some reviews.

GLiNER is applied using the zero-shot label "author" and a confidence threshold of 0.50. The label instructs the model to identify textual entities that it considers represents authors based on their surrounding context. Only detections with a confidence score of at least 0.50 are retained.

Each detected entity also includes a short slice of surrounding text of up to 120 characters, which allows for the identified entities to be inspected closely.

Since GLiNER tended to identify different forms of the same name as separate entities, frequently occurring name variants were manually grouped under a single name. For example, "Albert" and "Camus" were grouped under "Albert Camus". Other entities that weren't given a grouping name were still retained.


Outputs:

1. metamorphosis_gliner_entities_raw.csv –> contains every individual entity detection that met the confidence treshold, including its review ID, book title, chunk number, extracted and normal name form, entity label, confidence score, and surrounding context. It was mainly used for the manual inspection of false positives and other ambiguous detections.

2. metamorphosis_canonical_entity_counts.csv –> contains the final entity counts after grouping together the different variations of the same entity and other detected entities,
together with their total number of mentions, total number of distinct reviews in which they occurred, the average confidence score, and one example context. This file constituted the main aggregated output for sub study 3.


