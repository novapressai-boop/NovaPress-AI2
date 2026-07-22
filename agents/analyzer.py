import json
import re
from pathlib import Path
from collections import Counter


# -----------------------------
# Project Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

KEYWORDS_DIR = BASE_DIR / "data" / "keywords"
OUTPUT_DIR = BASE_DIR / "data" / "output"

INPUT_FILE = OUTPUT_DIR / "news_output.json"
OUTPUT_FILE = OUTPUT_DIR / "analyzed_news.json"


# -----------------------------
# Load Keyword Files
# -----------------------------
def load_keywords():
    keyword_db = {}

    if not KEYWORDS_DIR.exists():
        print("Keyword folder not found!")
        return keyword_db

    for file in KEYWORDS_DIR.glob("*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            category = file.stem.lower()

            keyword_db[category] = [
                str(k).strip().lower()
                for k in data
                if isinstance(k, str)
            ]

            print(f"Loaded {category}: {len(keyword_db[category])} keywords")

        except Exception as e:
            print(f"Error loading {file.name}: {e}")

    return keyword_db


# -----------------------------
# Clean Text
# -----------------------------
def clean_text(text):

    if not text:
        return ""

    text = text.lower()

    text = re.sub(r"<.*?>", " ", text)

    text = re.sub(r"http\\S+", " ", text)

    text = re.sub(r"[^\\w\\s]", " ", text)

    text = re.sub(r"\\s+", " ", text)

    return text.strip()


# -----------------------------
# Count Keyword Matches
# -----------------------------
def match_keywords(text, keywords):

    score = 0

    found = []

    for keyword in keywords:

        if keyword in text:

            score += 1

            found.append(keyword)

    return score, found


KEYWORDS = load_keywords()
# -----------------------------
# Analyze Single News
# -----------------------------
def analyze_news(news):

    title = clean_text(news.get("title", ""))

    summary = clean_text(news.get("summary", ""))

    content = clean_text(news.get("content", ""))

    full_text = f"{title} {summary} {content}"

    category_scores = {}

    matched_keywords = {}

    total_score = 0

    for category, keywords in KEYWORDS.items():

        score, found = match_keywords(full_text, keywords)

        category_scores[category] = score

        matched_keywords[category] = found

        total_score += score

    if category_scores:

        best_category = max(category_scores, key=category_scores.get)

        best_score = category_scores[best_category]

    else:

        best_category = "unknown"

        best_score = 0


    # -----------------------------
    # Priority
    # -----------------------------
    if total_score >= 40:

        priority = "HIGH"

    elif total_score >= 20:

        priority = "MEDIUM"

    else:

        priority = "LOW"


    # -----------------------------
    # Approval
    # -----------------------------
    approved = total_score >= 20


    analyzed = {

        "title": news.get("title", ""),

        "link": news.get("link", ""),

        "published": news.get("published", ""),

        "source": news.get("source", ""),

        "summary": news.get("summary", ""),

        "content": news.get("content", ""),

        "category": best_category,

        "category_score": best_score,

        "total_score": total_score,

        "priority": priority,

        "approved": approved,

        "matched_keywords": matched_keywords[best_category]

    }

    return analyzed
# -----------------------------
# Analyze All News
# -----------------------------
def analyze_all_news():

    if not INPUT_FILE.exists():
        print("Input file not found:", INPUT_FILE)
        return

    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            news_list = json.load(f)

    except Exception as e:
        print("Error reading input:", e)
        return

    if not isinstance(news_list, list):
        print("Invalid news format.")
        return

    analyzed_news = []

    approved_count = 0

    rejected_count = 0

    category_counter = Counter()

    for news in news_list:

        result = analyze_news(news)

        analyzed_news.append(result)

        category_counter[result["category"]] += 1

        if result["approved"]:
            approved_count += 1
        else:
            rejected_count += 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            analyzed_news,
            f,
            ensure_ascii=False,
            indent=4
        )

    print("\n========== Analyzer Report ==========")
    print(f"Total News      : {len(analyzed_news)}")
    print(f"Approved News   : {approved_count}")
    print(f"Rejected News   : {rejected_count}")

    print("\nCategory Summary")
    for category, count in category_counter.items():
        print(f"- {category}: {count}")

    print(f"\nSaved File: {OUTPUT_FILE}")


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    analyze_all_news()