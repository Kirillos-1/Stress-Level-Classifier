import pandas as pd
import argparse
import re
import zipfile
from datetime import date
from pathlib import Path
from typing import Optional


STANDARD_COLUMNS = [
    "id", "text", "stress_level", "source_type", "source_name", "source_url",
    "source_record_id", "original_label", "label_mapping_rule", "language",
    "date_collected", "collector", "labeler", "review_status", "notes"
]

MENTALDISTRESS_MAPPING = {
    "Others": ("Low", "Others -> Low: general/non-distress text"),
    "Frustrated": ("Medium", "Frustrated -> Medium: pressure/irritation but not necessarily severe distress"),
    "Anxious": ("High", "Anxious -> High: strong stress/anxiety expression"),
}

DREADDIT_MAPPING = {
    0: ("Low", "Dreaddit binary label 0 -> Low/non-stress"),
    1: ("High", "Dreaddit binary label 1 -> High/stress; no Medium class in source"),
    "0": ("Low", "Dreaddit binary label 0 -> Low/non-stress"),
    "1": ("High", "Dreaddit binary label 1 -> High/stress; no Medium class in source"),
}

def clean_text(value):
    text = "" if pd.isna(value) else str(value)
    return re.sub(r"\s+", " ", text).strip()

def balanced_sample(df, label_col, n_per_class: Optional[int]):
    if not n_per_class:
        return df.sample(frac=1, random_state=42).reset_index(drop=True)
    parts = []
    for _, group in df.groupby(label_col):
        parts.append(group.sample(n=min(n_per_class, len(group)), random_state=42))
    return pd.concat(parts, ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)

def standardize_mentaldistress(input_csv: Path, output_csv: Path, n_per_class: Optional[int]):
    df = pd.read_csv(input_csv)
    required = {"Text", "Label"}
    if not required.issubset(df.columns):
        raise ValueError(f"Expected columns {required}, found {set(df.columns)}")
    df = df[df["Label"].isin(MENTALDISTRESS_MAPPING)].copy()
    df["text"] = df["Text"].map(clean_text)
    df = df[df["text"].str.len() > 0]
    df["stress_level"] = df["Label"].map(lambda x: MENTALDISTRESS_MAPPING[x][0])
    df = balanced_sample(df, "stress_level", n_per_class)
    rows = []
    today = date.today().isoformat()
    for i, row in df.reset_index(drop=True).iterrows():
        original_label = row["Label"]
        stress_level, mapping_rule = MENTALDISTRESS_MAPPING[original_label]
        rows.append({
            "id": i + 1,
            "text": row["text"],
            "stress_level": stress_level,
            "source_type": "Mendeley Data public dataset",
            "source_name": "MentalDistress",
            "source_url": "https://data.mendeley.com/datasets/b42wr437hg/2",
            "source_record_id": str(row.name),
            "original_label": original_label,
            "label_mapping_rule": mapping_rule,
            "language": "English",
            "date_collected": today,
            "collector": "project_team",
            "labeler": "source_label_mapping",
            "review_status": "needs_review",
            "notes": "Depressed and Suicidal source classes excluded from v1"
        })
    pd.DataFrame(rows, columns=STANDARD_COLUMNS).to_csv(output_csv, index=False)
    print(f"Saved {len(rows)} rows to {output_csv}")
    print(pd.Series([r["stress_level"] for r in rows]).value_counts())

# def read_dreaddit_file(path: Path):
#     if path.suffix.lower() == ".zip":
#         frames = []
#         with zipfile.ZipFile(path) as z:
#             for name in z.namelist():
#                 if name.lower().endswith(".csv"):
#                     with z.open(name) as f:
#                         part = pd.read_csv(f)
#                         part["_source_file"] = name
#                         frames.append(part)
#         if not frames:
#             raise ValueError("No CSV files found inside the Dreaddit zip.")
#         return pd.concat(frames, ignore_index=True)
#     return pd.read_csv(path)

# def standardize_dreaddit(input_file: Path, output_csv: Path, n_per_class: Optional[int]):
#     df = read_dreaddit_file(input_file)
#     if "text" not in df.columns or "label" not in df.columns:
#         raise ValueError(f"Expected columns 'text' and 'label', found {list(df.columns)}")
#     df = df[df["label"].isin([0, 1, "0", "1"])].copy()
#     df["text"] = df["text"].map(clean_text)
#     df = df[df["text"].str.len() > 0]
#     df["stress_level"] = df["label"].map(lambda x: DREADDIT_MAPPING[x][0])
#     df = balanced_sample(df, "stress_level", n_per_class)
#     today = date.today().isoformat()
#     rows = []
#     for i, row in df.reset_index(drop=True).iterrows():
#         label = row["label"]
#         stress_level, mapping_rule = DREADDIT_MAPPING[label]
#         rows.append({
#             "id": i + 1,
#             "text": row["text"],
#             "stress_level": stress_level,
#             "source_type": "ACL Anthology official attachment",
#             "source_name": "Dreaddit",
#             "source_url": "https://aclanthology.org/D19-6213/",
#             "source_record_id": str(row.get("id", row.name)),
#             "original_label": str(label),
#             "label_mapping_rule": mapping_rule,
#             "language": "English",
#             "date_collected": today,
#             "collector": "project_team",
#             "labeler": "source_label_mapping",
#             "review_status": "needs_review",
#             "notes": "Dreaddit is binary; use only as optional Low/High supplement"
#         })
#     pd.DataFrame(rows, columns=STANDARD_COLUMNS).to_csv(output_csv, index=False)
#     print(f"Saved {len(rows)} rows to {output_csv}")
#     print(pd.Series([r["stress_level"] for r in rows]).value_counts())

def main():
    # python build_stress_level_dataset.py --source mentaldistress --input MentalDistress.csv --output stress_level_dataset_v1.csv --n-per-class 1500
    
    parser = argparse.ArgumentParser(description="Standardize online stress/mental-health text datasets into our Stress Level Classifier CSV format.")
    parser.add_argument("--source", choices=["mentaldistress", "dreaddit"], required=True)
    parser.add_argument("--input", required=True, help="Path to downloaded CSV or zip file")
    parser.add_argument("--output", default="stress_level_dataset_v1.csv")
    parser.add_argument("--n-per-class", type=int, default=None, help="Optional balanced sample size per target class")
    args = parser.parse_args()
    if args.source == "mentaldistress":
        standardize_mentaldistress(Path(args.input), Path(args.output), args.n_per_class)
    else:
        pass
        # standardize_dreaddit(Path(args.input), Path(args.output), args.n_per_class)

if __name__ == "__main__":
    main()
