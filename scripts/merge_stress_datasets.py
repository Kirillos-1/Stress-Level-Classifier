import argparse
import pandas as pd

STANDARD_COLUMNS = [
    "id",
    "text",
    "stress_level",
    "source_type",
    "source_name",
    "source_url",
    "source_record_id",
    "original_label",
    "label_mapping_rule",
    "language",
    "date_collected",
    "collector",
    "labeler",
    "review_status",
    "notes",
]

def main():
    # python merge_stress_datasets.py --base stress_level_dataset_v1.csv --scraped scraped_stackexchange_stress_clean.csv --output stress_level_dataset_v2_combined.csv
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="stress_level_dataset_v1.csv")
    parser.add_argument("--scraped", default="scraped_stackexchange_stress.csv")
    parser.add_argument("--output", default="stress_level_dataset_v2_combined.csv")
    args = parser.parse_args()

    base = pd.read_csv(args.base)
    scraped = pd.read_csv(args.scraped)

    for col in STANDARD_COLUMNS:
        if col not in base.columns:
            base[col] = ""
        if col not in scraped.columns:
            scraped[col] = ""

    combined = pd.concat([base[STANDARD_COLUMNS], scraped[STANDARD_COLUMNS]], ignore_index=True)
    combined["text_normalized"] = combined["text"].astype(str).str.lower().str.strip()
    combined = combined.drop_duplicates(subset=["text_normalized"]).drop(columns=["text_normalized"])
    combined["id"] = [f"combined_{i:05d}" for i in range(1, len(combined) + 1)]

    combined.to_csv(args.output, index=False, encoding="utf-8")
    print(f"Saved {len(combined)} rows to {args.output}")
    print(combined["stress_level"].value_counts())

if __name__ == "__main__":
    main()
