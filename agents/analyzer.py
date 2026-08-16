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

            with open(
                file,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            if not isinstance(data, list):
                print(f"Invalid keyword file: {file.name}")
                continue

            category = file.stem.lower()

            keywords = []

            for item in data:

                if isinstance(item, str):

                    keyword = item.strip().lower()

                    if keyword:
                        keywords.append(keyword)

            keyword_db[category] = keywords

            print(
                f"Loaded {category}: "
                f"{len(keywords)} keywords"
            )

        except Exception as e:

            print(
                f"Error loading {file.name}: {e}"
            )

    return keyword_db


# -----------------------------
# Clean Text
# -----------------------------
def clean_text(text):

    if not text:
        return ""

    text = str(text).lower()

    # Remove HTML
    text = re.sub(
        r"<.*?>",
        " ",
        text
    )

    # Remove URLs
    text = re.sub(
        r"https?://\S+|www\.\S+",
        " ",
        text
    )

    # Remove punctuation
    text = re.sub(
        r"[^\w\s]",
        " ",
        text
    )

    # Remove extra spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# -----------------------------
# Keyword Matching
# -----------------------------
def keyword_matches(text, keywords):

    found = []

    for keyword in keywords:

        keyword = keyword.strip().lower()

        if not keyword:
            continue

        # For very short English keywords,
        # use word boundaries to avoid false matches.
        if re.fullmatch(
            r"[a-z0-9]+",
            keyword
        ):

            pattern = (
                r"(?<![a-z0-9])"
                + re.escape(keyword)
                + r"(?![a-z0-9])"
            )

            if re.search(
                pattern,
                text
            ):

                found.append(keyword)

        else:

            if keyword in text:
                found.append(keyword)

    return found


# -----------------------------
# Calculate Category Score
# -----------------------------
def calculate_category_score(
    title,
    summary,
    content,
    keywords
):

    title_matches = keyword_matches(
        title,
        keywords
    )

    summary_matches = keyword_matches(
        summary,
        keywords
    )

    content_matches = keyword_matches(
        content,
        keywords
    )

    # Remove duplicates
    title_matches = list(dict.fromkeys(title_matches))
    summary_matches = list(dict.fromkeys(summary_matches))
    content_matches = list(dict.fromkeys(content_matches))

    # Weighted scoring
    title_score = len(title_matches) * 3

    summary_score = len(summary_matches) * 2

    content_score = len(content_matches)

    total_score = (
        title_score
        + summary_score
        + content_score
    )

    all_matches = list(
        dict.fromkeys(
            title_matches
            + summary_matches
            + content_matches
        )
    )

    return {
        "score": total_score,
        "title_matches": title_matches,
        "summary_matches": summary_matches,
        "content_matches": content_matches,
        "all_matches": all_matches
    }


# -----------------------------
# Load Keywords
# -----------------------------
KEYWORDS = load_keywords()


# -----------------------------
# Analyze One News
# -----------------------------
def analyze_news(news):

    title = clean_text(
        news.get("title", "")
    )

    summary = clean_text(
        news.get("summary", "")
    )

    content = clean_text(
        news.get("content", "")
    )

    category_scores = {}

    category_matches = {}

    # -----------------------------
    # Check Every Category
    # -----------------------------
    for category, keywords in KEYWORDS.items():

        result = calculate_category_score(
            title,
            summary,
            content,
            keywords
        )

        category_scores[category] = result["score"]

        category_matches[category] = result

    # -----------------------------
    # Find Best Category
    # -----------------------------
    if category_scores:

        best_category = max(
            category_scores,
            key=category_scores.get
        )

        best_result = category_matches[
            best_category
        ]

        best_score = best_result["score"]

    else:

        best_category = "unknown"

        best_score = 0

        best_result = {
            "score": 0,
            "title_matches": [],
            "summary_matches": [],
            "content_matches": [],
            "all_matches": []
        }

    # -----------------------------
    # Approval Logic
    # -----------------------------
    match_count = len(
        best_result["all_matches"]
    )

    # A news item is approved when:
    # 1. At least 2 relevant keywords are found
    # OR
    # 2. One strong title keyword is found
    #
    # This prevents the old problem where
    # almost everything was rejected.

    strong_title_match = (
        len(best_result["title_matches"]) >= 1
    )

    approved = (
        match_count >= 2
        or strong_title_match
    )

    # -----------------------------
    # Priority
    # -----------------------------
    if best_score >= 12:

        priority = "HIGH"

    elif best_score >= 6:

        priority = "MEDIUM"

    else:

        priority = "LOW"

    # -----------------------------
    # Final Result
    # -----------------------------
    analyzed = {

        "title": news.get(
            "title",
            ""
        ),

        "link": news.get(
            "link",
            ""
        ),

        "published": news.get(
            "published",
            ""
        ),

        "source": news.get(
            "source",
            ""
        ),

        "summary": news.get(
            "summary",
            ""
        ),

        "content": news.get(
            "content",
            ""
        ),

        "category": best_category,

        "category_score": best_score,

        "total_score": best_score,

        "priority": priority,

        "approved": approved,

        "matched_keywords": best_result[
            "all_matches"
        ],

        "title_matches": best_result[
            "title_matches"
        ],

        "summary_matches": best_result[
            "summary_matches"
        ],

        "content_matches": best_result[
            "content_matches"
        ]
    }

    return analyzed


# -----------------------------
# Analyze All News
# -----------------------------
def analyze_all_news():

    # -----------------------------
    # Check Input File
    # -----------------------------
    if not INPUT_FILE.exists():

        print(
            "Input file not found:"
        )

        print(
            INPUT_FILE
        )

        return

    # -----------------------------
    # Read News
    # -----------------------------
    try:

        with open(
            INPUT_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            news_list = json.load(f)

    except Exception as e:

        print(
            "Error reading input:",
            e
        )

        return

    # -----------------------------
    # Validate
    # -----------------------------
    if not isinstance(
        news_list,
        list
    ):

        print(
            "Invalid news format."
        )

        return

    # -----------------------------
    # Counters
    # -----------------------------
    analyzed_news = []

    approved_count = 0

    rejected_count = 0

    category_counter = Counter()

    # -----------------------------
    # Analyze News
    # -----------------------------
    for news in news_list:

        if not isinstance(
            news,
            dict
        ):

            continue

        result = analyze_news(
            news
        )

        analyzed_news.append(
            result
        )

        category_counter[
            result["category"]
        ] += 1

        if result["approved"]:

            approved_count += 1

        else:

            rejected_count += 1

    # -----------------------------
    # Create Output Directory
    # -----------------------------
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------
    # Save Result
    # -----------------------------
    try:

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                analyzed_news,
                f,
                ensure_ascii=False,
                indent=4
            )

    except Exception as e:

        print(
            "Error saving output:",
            e
        )

        return

    # -----------------------------
    # Analyzer Report
    # -----------------------------
    print(
        "\n========== Analyzer Report =========="
    )

    print(
        f"Total News      : {len(analyzed_news)}"
    )

    print(
        f"Approved News   : {approved_count}"
    )

    print(
        f"Rejected News   : {rejected_count}"
    )

    print(
        "\nCategory Summary"
    )

    for category, count in (
        category_counter.most_common()
    ):

        print(
            f"- {category}: {count}"
        )

    # -----------------------------
    # Approval Percentage
    # -----------------------------
    if len(analyzed_news) > 0:

        percentage = (
            approved_count
            / len(analyzed_news)
        ) * 100

        print(
            f"\nApproval Rate   : "
            f"{percentage:.1f}%"
        )

    print(
        f"\nSaved File: {OUTPUT_FILE}"
    )


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":

    analyze_all_news()