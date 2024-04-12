# chess_improments_patterns

This repository contains the code for the final project in the course 

The purpose of this project is finding patterns of improvemnt in chess players

## Project Organization

------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── {{data source}}       <- Data from third party sources.
    │              ├── external       <- Data from third party sources.
    │              ├── interim        <- Intermediate data that has been transformed.
    │              ├── processed      <- The final, canonical data sets for modeling.
    │              └── raw            <- The original, immutable data dump.
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │       └── make_dataset.py

--------


## Requirements
`Python 3.8+`

## Installation

Clone the repository and install all the requirments

```
git clone https://github.com/ariel-zilber/chess_improments_patterns.git --recursive
cd chess_improments_patterns
make clean
make requirements
make data
```

## Notebooks
The project is structured around 3 notebooks

[1.exploritary data analysis](notebooks/P1_01_eda.ipynb)  - in this section we explore the dataset

[2. Clustering](notebooks/P1_02_clustering.ipynb) - in this section we perform time series clustering on the chess dataset to create time series patterns

[3. Classification](notebooks/P1_03_classifier.ipynb) - in the section perform classification to predict 

 