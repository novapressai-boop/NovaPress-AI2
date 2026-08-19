import json
import re
from pathlib import Path
from collections import Counter


# =========================================
# NovaPress AI - Analyzer
# =========================================

print("\n========== NovaPress AI Analyzer ==========\n")


# =========================================
# Project Paths
# =========================================

# analyzer.py is inside:
# NovaPress-AI2/agents/analyzer.py

AGENT_DIR = Path(__file__).resolve().parent
BASE_DIR = AGENT_DIR.parent

DATA_DIR = BASE_DIR / "data"

OUTPUT_DIR = DATA_DIR / "output"

INPUT_FILE = OUTPUT_DIR / "news_output.json"

OUTPUT_FILE = OUTPUT_DIR / "analyzed_news.json"


# Support both possible keyword folder names
KEYWORDS_DIR = DATA_DIR / "keywords"

if not KEYWORDS_DIR.exists():

    ALT_KEYWORDS_DIR = DATA_DIR / "keyword"

    if ALT_KEYWORDS_DIR.exists():
        KEYWORDS_DIR = ALT_KEYWORDS_DIR


print("Project Directory:")
print(BASE_DIR)

print("\nInput File:")
print(INPUT_FILE)

print("\nKeyword Directory:")
print(KEYWORDS_DIR)


# =========================================
# Load Keywords
# =========================================

def load_keywords():

    keyword_db = {}

    if not KEYWORDS_DIR.exists():

        print(
            "\nWARNING: Keyword folder not found!"
        )

        return keyword_db

    files = list(
        KEYWORDS_DIR.glob("*.json")
    )

    if not files:

        print(
            "\nWARNING: No keyword JSON files found!"
        )

        return keyword_db

    for file in files:

        try:

            with open(
                file,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            # Accept a simple list:
            # ["cricket", "football"]

            if isinstance(data, list):

                raw_keywords = data

            # Also accept:
            # {"keywords": ["cricket", "football"]}

            elif isinstance(data, dict):

                raw_keywords = data.get(
                    "keywords",
                    []
                )

            else:

                print(
                    f"Invalid keyword file: {file.name}"
                )

                continue

            keywords = []

            for item in raw_keywords:

                if isinstance(
                    item,
                    str
                ):

                    keyword = item.strip().lower()

                    if keyword:

                        keywords.append(
                            keyword
                        )

            keywords = list(
                dict.fromkeys(
                    keywords
                )
            )

            category = file.stem.lower()

            keyword_db[category] = keywords

            print(
                f"Loaded {category}: "
                f"{len(keywords)} keywords"
            )

        except Exception as e:

            print(
                f"Error loading "
                f"{file.name}: {e}"
            )

    return keyword_db


# =========================================
# Clean Text
# =========================================

def clean_text(text):

    if not text:

        return ""

    text = str(text).lower()

    # Remove HTML
    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # Remove URLs
    text = re.sub(
        r"https?://\S+|www\.\S+",
        " ",
        text
    )

    # Keep Unicode letters and numbers
    text = re.sub(
        r"[^\w\s]",
        " ",
        text,
        flags=re.UNICODE
    )

    # Remove extra spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================
# Keyword Matching
# =========================================

def keyword_matches(
    text,
    keywords
):

    found = []

    if not text:

        return found

    for keyword in keywords:

        keyword = keyword.strip().lower()

        if not keyword:

            continue

        # English / number keywords
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

                found.append(
                    keyword
                )

        else:

            # Bangla / multilingual keywords
            if keyword in text:

                found.append(
                    keyword
                )

    return list(
        dict.fromkeys(
            found
        )
    )


# =========================================
# Calculate Category Score
# =========================================

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

    # Weighted scoring
    title_score = (
        len(title_matches) * 3
    )

    summary_score = (
        len(summary_matches) * 2
    )

    content_score = (
        len(content_matches)
    )

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

        "title_matches":
            title_matches,

        "summary_matches":
            summary_matches,

        "content_matches":
            content_matches,

        "all_matches":
            all_matches
    }


# =========================================
# Analyze One News Item
# =========================================

def analyze_news(
    news,
    keyword_db
):

    title = clean_text(
        news.get(
            "title",
            ""
        )
    )

    summary = clean_text(
        news.get(
            "summary",
            ""
        )
    )

    content = clean_text(
        news.get(
            "content",
            ""
        )
    )

    category_scores = {}

    category_results = {}

    # Check every category
    for category, keywords in (
        keyword_db.items()
    ):

        result = calculate_category_score(
            title,
            summary,
            content,
            keywords
        )

        category_scores[category] = (
            result["score"]
        )

        category_results[category] = (
            result
        )

    # =====================================
    # Find Best Category
    # =====================================

    if category_scores:

        best_category = max(
            category_scores,
            key=category_scores.get
        )

        best_result = category_results[
            best_category
        ]

        best_score = best_result[
            "score"
        ]

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

    # =====================================
    # Approval Logic
    # =====================================

    match_count = len(
        best_result[
            "all_matches"
        ]
    )

    strong_title_match = (
        len(
            best_result[
                "title_matches"
            ]
        ) >= 1
    )

    approved = (
        match_count >= 2
        or strong_title_match
    )

    # =====================================
    # Priority
    # =====================================

    if best_score >= 12:

        priority = "HIGH"

    elif best_score >= 6:

        priority = "MEDIUM"

    else:

        priority = "LOW"

    # =====================================
    # Final Analyzed News
    # =====================================

    return {

        "title":
            news.get(
                "title",
                ""
            ),

        "link":
            news.get(
                "link",
                ""
            ),

        "published":
            news.get(
                "published",
                ""
            ),

        "source":
            news.get(
                "source",
                ""
            ),

        "summary":
            news.get(
                "summary",
                ""
            ),

        "content":
            news.get(
                "content",
                ""
            ),

        "category":
            best_category,

        "category_score":
            best_score,

        "total_score":
            best_score,

        "priority":
            priority,

        "approved":
            approved,

        "matched_keywords":
            best_result[
                "all_matches"
            ],

        "title_matches":
            best_result[
                "title_matches"
            ],

        "summary_matches":
            best_result[
                "summary_matches"
            ],

        "content_matches":
            best_result[
                "content_matches"
            ]
    }


# =========================================
# Main Analyzer
# =========================================

def analyze_all_news():

    # =====================================
    # Check Input
    # =====================================

    if not INPUT_FILE.exists():

        print(
            "\nERROR: Input file not found!"
        )

        print(
            INPUT_FILE
        )

        return

    # =====================================
    # Load News
    # =====================================

    try:

        with open(
            INPUT_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            news_list = json.load(f)

    except Exception as e:

        print(
            f"\nERROR reading news file: {e}"
        )

        return

    # =====================================
    # Validate News
    # =====================================

    if not isinstance(
        news_list,
        list
    ):

        print(
            "\nERROR: news_output.json "
            "must contain a JSON list."
        )

        return

    print(
        f"\nCollected News : "
        f"{len(news_list)}"
    )

    # =====================================
    # Load Keywords
    # =====================================

    keyword_db = load_keywords()

    print(
        f"\nCategories Loaded : "
        f"{len(keyword_db)}"
    )

    # =====================================
    # Analyze
    # =====================================

    analyzed_news = []

    approved_count = 0

    rejected_count = 0

    category_counter = Counter()

    print(
        "\nAnalyzing news...\n"
    )

    for index, news in enumerate(
        news_list,
        start=1
    ):

        if not isinstance(
            news,
            dict
        ):

            continue

        result = analyze_news(
            news,
            keyword_db
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

        print(
            f"[{index}/{len(news_list)}] "
            f"{result['category']} | "
            f"Score: {result['total_score']} | "
            f"Approved: {result['approved']}"
        )

    # =====================================
    # Save Output
    # =====================================

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

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
            f"\nERROR saving output: {e}"
        )

        return

    # =====================================
    # Report
    # =====================================

    print(
        "\n========== Analyzer Report =========="
    )

    print(
        f"Total News      : "
        f"{len(analyzed_news)}"
    )

    print(
        f"Approved News   : "
        f"{approved_count}"
    )

    print(
        f"Rejected News   : "
        f"{rejected_count}"
    )

    print(
        "\nCategory Summary:"
    )

    for category, count in (
        category_counter.most_common()
    ):

        print(
            f"- {category}: {count}"
        )

    if analyzed_news:

        approval_rate = (
            approved_count
            / len(analyzed_news)
        ) * 100

        print(
            f"\nApproval Rate   : "
            f"{approval_rate:.1f}%"
        )

    print(
        "\nSaved File:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "\nAnalyzer finished successfully."
    )


# =========================================
# Run
# =========================================

if __name__ == "__main__":

    try:

        analyze_all_news()

    except KeyboardInterrupt:

        print(
            "\nAnalyzer stopped by user."
        )

    except Exception as e:

        print(
            f"\nUnexpected Error: {e}"
        )