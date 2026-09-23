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

To run the corpus preproccessing code, run this in the terminal: ".\run_corpus.bat" 
To run the sub studies, run this in the terminal: ".\run_sub_studies.bat"

the automatition script requires that the project runs on a virtual enviroment, this can be done by running "python -m venv .venv", be sure to install all the required packages to the virtual enviroment and not to the global enviroment as that can lead to conflicts with local installs please refer to the versions below in case of version clash

|Package              | Version |
|---------------------| -------| 
|annotated-doc        | 0.0.5|
|anyio                | 4.15.1|
|bertopic             | 0.17.4|
|certifi              | 2026.7.22|
|click                | 8.5.0|
|cloudpickle          | 3.1.2|
|colorama             | 0.4.6|
|contourpy            | 1.4.0|
|cycler               | 0.12.1|
|filelock             | 4.0.1|
|fonttools            | 4.65.0|
|fsspec               | 2026.9.0|
|gliner               | 0.2.29|
|h11                  | 0.16.0|
|hdbscan              | 0.8.44|
|hf-xet               | 1.6.0|
|httpcore             | 1.0.9|
|httpx                | 0.28.1|
|huggingface_hub      | 1.32.0|
|idna                 | 3.20|
|Jinja2               | 3.1.6|
|joblib               | 1.6.0|
|kiwisolver           | 1.5.1|
|langdetect           | 1.0.9|
|llvmlite             | 0.49.0|
|markdown-it-py       | 4.2.0|
|MarkupSafe           | 3.0.3|
|matplotlib           | 3.11.2|
|mdurl                | 0.1.2|
|mpmath               | 1.3.0|
|narwhals             | 2.26.0|
|networkx             | 3.7|
|numba                | 0.67.0|
|numpy                | 2.5.3|
|packaging            | 26.3|
|pandas               | 3.0.6|
|pillow               | 12.3.0|
|pip                  | 25.1.1|
|plotly               | 7.1.0|
|Pygments             | 2.21.0|
|pynndescent          | 0.6.0|
|pyparsing            | 3.3.3|
|python-dateutil      | 2.9.0.post0|
|PyYAML               | 6.0.3|
|regex                | 2026.9.10|
|rich                 | 15.0.0|
|safetensors          | 0.8.0|
|scikit-learn         | 1.9.1|
|scipy                | 1.18.1|
|seaborn              | 0.13.2|
|sentence-transformers| 6.1.0|
|sentencepiece       |  0.2.2|
|setuptools          |  84.0.0|
|shellingham         |  1.5.4|
|six                 |  1.17.0|
|sympy               |  1.14.0|
|threadpoolctl       |  3.7.0|
|tokenizers          |  0.23.2|
|torch               |  2.14.0|
|tqdm                |  4.70.1|
|transformers        |  5.16.1|
|typer               |  0.27.2|
|typing_extensions   |  4.16.0|
|tzdata              |  2026.4|
|umap-learn          |  0.5.12|
|
