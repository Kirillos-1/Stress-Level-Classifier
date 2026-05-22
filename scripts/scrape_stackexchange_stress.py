import argparse
import csv
import html
import random
import re
import time
from datetime import date
from urllib.parse import urlencode
from urllib.request import Request, urlopen

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

QUERY_GROUPS = {
    "High": [
        "overwhelmed anxiety panic cannot cope",
        "burnout exhausted pressure",
        "extreme stress deadline",
        "mental breakdown workload",
    ],
    "Medium": [
        "worried exam deadline",
        "nervous presentation pressure",
        "stress workload manage",
        "concerned about grades",
    ],
    "Low": [
        "calm productive routine",
        "relaxed study schedule",
        "balanced workload",
        "good time management",
    ],
}

"""
    academia     -> Students, researchers, deadlines, workload
    workplace    -> Job pressure, burnout, work stree
    interperonal -> Social pressure, communication issues, emotional tension
"""

SITES = ["academia", "workplace", "interpersonal"]

def strip_html(value: str) -> str:
    """Stack Exchange API returns question bodies with HTML tags"""
    value = html.unescape(value or "")
    value = re.sub(r"<script.*?</script>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<style.*?</style>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value

def stackexchange_search(site: str, query: str, page: int, pagesize: int):
    params = {
        "order": "desc",
        "sort": "activity",
        "q": query,
        "site": site,
        "filter": "withbody",
        "page": page,
        "pagesize": pagesize,
    }
    url = "https://api.stackexchange.com/2.3/search/advanced?" + urlencode(params)
    req = Request(url, headers={"User-Agent": "stress-level-classifier-course-project/1.0"})
    with urlopen(req, timeout=30) as resp:
        """
        sends request, reads the response, decodes it as text,
        converts JSON into a Python dictionary
        """
        import json
        return json.loads(resp.read().decode("utf-8"))

def build_text(item: dict) -> str:
    title = strip_html(item.get("title", ""))
    body = strip_html(item.get("body", ""))
    text = f"{title}. {body}".strip()
    text = re.sub(r"\s+", " ", text)
    return text

def collect(n_per_class: int, pages_per_query: int, delay: float):
    rows = []
    seen_texts = set()
    today = date.today().isoformat()

    """
        Searches:
            - Each stress level
            - Each Stack Exchange Site
            - Each query for that stress level
            - Each result page for that query
    """
    
    for stress_level, queries in QUERY_GROUPS.items():
        class_rows = []
        for site in SITES:
            for query in queries:
                for page in range(1, pages_per_query + 1):
                    if len(class_rows) >= n_per_class:
                        break
                    try:
                        data = stackexchange_search(site, query, page=page, pagesize=50)
                    except Exception as exc:
                        print(f"Warning: failed query site={site}, label={stress_level}, q={query!r}, page={page}: {exc}")
                        continue

                    for item in data.get("items", []):
                        if len(class_rows) >= n_per_class:
                            break

                        text = build_text(item)
                        if len(text.split()) < 20:
                            continue

                        key = text.lower()
                        if key in seen_texts:
                            continue
                        seen_texts.add(key)

                        class_rows.append({
                            "id": "",
                            "text": text,
                            "stress_level": stress_level,
                            "source_type": "online_scraping_api",
                            "source_name": "Stack Exchange API",
                            "source_url": item.get("link", ""),
                            "source_record_id": str(item.get("question_id", "")),
                            "original_label": f"{site}:{query}",
                            "label_mapping_rule": "keyword_query_mapping_v1",
                            "language": "English",
                            "date_collected": today,
                            "collector": "project_team",
                            "labeler": "keyword_mapping_needs_manual_review",
                            "review_status": "needs_review",
                            "notes": "Scraped online text; verify label manually before final modeling.",
                        })

                    if not data.get("has_more", False):
                        break
                    time.sleep(delay)

                if len(class_rows) >= n_per_class:
                    break
            if len(class_rows) >= n_per_class:
                break

        print(f"{stress_level}: collected {len(class_rows)} rows")
        rows.extend(class_rows)

    random.seed(42)
    random.shuffle(rows)
    for index, row in enumerate(rows, start=1):
        row["id"] = f"scraped_{index:05d}"
    return rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="scraped_stackexchange_stress.csv")
    parser.add_argument("--n-per-class", type=int, default=200)
    parser.add_argument("--pages-per-query", type=int, default=2)
    parser.add_argument("--delay", type=float, default=0.4)
    args = parser.parse_args()

    rows = collect(args.n_per_class, args.pages_per_query, args.delay)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=STANDARD_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved {len(rows)} rows to {args.output}")
    counts = {}
    for row in rows:
        counts[row["stress_level"]] = counts.get(row["stress_level"], 0) + 1
    print("Class counts:", counts)

if __name__ == "__main__":
    main()
