# Project Structure Guide

This repository is organized to make the machine-learning workflow easy to understand, reproduce, and present.

```text
Stress-level-classifier/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── docs/
├── metadata/
├── models/
├── notebooks/
├── reports/
└── scripts/
```

## Main folders

### `data/raw/`
Original source files. These files should be kept unchanged so the dataset creation process remains traceable.

### `data/interim/`
Intermediate generated files, such as standardized source datasets before final cleaning and balancing.

### `data/processed/`
Cleaned datasets used for modeling. The main file is:

```text
data/processed/stress_level_dataset_v2_balanced.csv
```

### `notebooks/`
Notebook-based workflow used for explanation and discussion.

- `01_scraping_stackexchange.ipynb`: collects additional text examples.
- `02_data_inspection_cleaning.ipynb`: cleans, merges, checks, and balances the dataset.
- `phase2_modeling.ipynb`: trains, evaluates, compares, and saves the models.

### `scripts/`
Reusable Python scripts for dataset building, scraping, and merging.

### `metadata/`
Dataset source metadata and label-mapping rules. This folder is important because it explains how the target labels were created.

### `models/`
Saved trained model pipeline used by the Streamlit app.

### `reports/`
Evaluation outputs, prediction files, figures, and final reports.

### `docs/`
Extra documentation for GitHub, LinkedIn, project structure, and model limitations.

## Recommended presentation order

1. Explain the problem: classify text into Low, Medium, or High stress.
2. Explain the dataset sources and label mapping.
3. Explain cleaning, duplicate removal, balancing, and TF-IDF.
4. Explain the five trained models.
5. Compare performance using Accuracy, Macro Precision, Macro Recall, and Macro F1.
6. Show the Streamlit app prediction workflow.
