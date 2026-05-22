# Model Card — Stress Level Classifier

## Model purpose

The model predicts one of three stress levels from a short English text response:

- Low
- Medium
- High

It is intended for educational demonstration of a machine-learning text classification workflow.

## Intended users

- Course instructors and evaluators.
- Students reviewing the machine-learning pipeline.
- Developers learning how to combine TF-IDF, scikit-learn models, and Streamlit.

## Not intended for

- Medical diagnosis.
- Crisis detection.
- Clinical decision making.
- Replacing professional mental-health support.

## Input

A short English text response, such as a journal entry, survey answer, or written reflection.

## Output

A predicted class label:

```text
Low, Medium, or High
```

The Streamlit app may also show prediction confidence scores if the selected model supports probabilities.

## Training data summary

Final balanced dataset:

```text
data/processed/stress_level_dataset_v2_balanced.csv
```

Class distribution:

| Class | Rows |
|---|---:|
| Low | 1,841 |
| Medium | 1,841 |
| High | 1,841 |
| Total | 5,523 |

## Evaluation summary

The best model was selected using Macro F1-score. Macro F1 is useful because it gives equal importance to each class.

| Model | Accuracy | Macro F1 |
|---|---:|---:|
| Logistic Regression | 0.776 | 0.778 |
| Linear SVM | 0.757 | 0.758 |
| Multinomial Naive Bayes | 0.719 | 0.719 |
| K-Nearest Neighbors | 0.706 | 0.707 |
| Decision Tree | 0.707 | 0.706 |

## Limitations

- The dataset labels come from mapped source labels and keyword-guided scraping, so labels can be noisy.
- The model may misunderstand sarcasm, long context, slang, or rare wording.
- The model is trained on English text only.
- The app should not be used for mental-health decisions.

## Ethical note

Stress-related predictions can be sensitive. The model should be presented as an educational classifier, not as a tool for judging or diagnosing a person’s mental state.
