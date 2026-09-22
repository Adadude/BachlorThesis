# BachelorThesis

## Requirements

Install the Python libraries used by the corpus construction and sub-study scripts:

```bash
pip install pandas matplotlib seaborn langdetect bertopic umap-learn sentence-transformers scikit-learn tqdm gliner torch
```

`torch` can be installed with either CPU support or the CUDA version appropriate for your system. See the official PyTorch installation instructions if you want GPU acceleration for the GLiNER or BERTopic analyses.

DISCLAIMER:
The Kafka Corpus is not included within this repository. To gain acess to it, refer to Prof. Dr. Manuel Burghardt @Uni Leipzig. When downloaded, it should be named
"KafkaCSV.zip" and be located within "..\Kafka_GoodReads\KafkaCSV.zip"

