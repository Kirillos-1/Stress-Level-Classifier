# Stress Level Classifier — Online Dataset Setup

## Decision for Dataset v1

Use the Mendeley Data dataset **MentalDistress: A multi-class social media text dataset for mental health-related emotion detection** as the primary dataset.

Reason: it contains English text samples and class labels, which makes it better for this NLP project than numeric-only survey datasets.

## Main Source

- Source: MentalDistress
- URL: https://data.mendeley.com/datasets/b42wr437hg/2
- DOI: 10.17632/b42wr437hg.2
- License: CC BY 4.0
- Size: 10,100 annotated text samples
- Original columns: `Text`, `Label`
- Original labels: `Suicidal`, `Depressed`, `Anxious`, `Frustrated`, `Others`

## Label Mapping for Dataset v1

| Original Label | Our Stress Label | Use? |
|---|---|---|
| Others | Low | Yes |
| Frustrated | Medium | Yes |
| Anxious | High | Yes |
| Depressed | Exclude from v1 | No |
| Suicidal | Exclude from v1 | No |

We exclude `Depressed` and `Suicidal` in the first version because they are not simply stress labels and may make the project harder to justify ethically and technically.

## How to Build the CSV After Downloading the Source File

1. Download the CSV from Mendeley Data.
2. Place it in the same folder as `build_stress_level_dataset.py`.
3. Run:

```bash
python build_stress_level_dataset.py --source mentaldistress --input MentalDistress.csv --output stress_level_dataset_v1.csv --n-per-class 1500
```

If the downloaded CSV has a different filename, replace `MentalDistress.csv` with the actual filename.

## Optional Secondary Source

Dreaddit can be used later as a secondary source for binary stress detection, but it should not be our primary dataset for this project because it only has stress/non-stress labels, not Low/Medium/High.

Official Dreaddit page:
https://aclanthology.org/D19-6213/
