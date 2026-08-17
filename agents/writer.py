import os
import json
from pathlib import Path

from google import genai


# =================================
# Project Paths
# =================================

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "data" / "output"

INPUT_FILE = OUTPUT_DIR / "analyzed_news.json"

OUTPUT_FILE = OUTPUT_DIR / "articles.json"


# =================================
# Gemini API
# =================================

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. "
        "Please set the API key in Pydroid Terminal."
    )

client = genai.Client(api_key=API_KEY)

MODEL = "gemini-2.5-flash"


# =================================
# Load Approved News
# =================================

def load_news():

    if not INPUT_FILE.exists():

        print("Input file not found:")
        print(INPUT_FILE)

        return []

    try:

        with open(
            INPUT_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            news = json.load(f)

    except Exception as e:

        print(f"Error loading news: {e}")

        return []

    approved = [
        item
        for item in news
        if item.get("approved") is True
    ]

    print(f"Approved News : {len(approved)}")

    return approved


# =================================
# Save Articles
# =================================

def save_articles(articles):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            articles,
            f,
            ensure_ascii=False,
            indent=4
        )

    print("Articles saved.")


# =================================
# Build SEO Prompt
# =================================

def build_prompt(news):

    category = news.get(
        "category",
        "General"
    )

    title = news.get(
        "title",
        ""
    )

    summary = news.get(
        "summary",
        ""
    )

    content = news.get(
        "content",
        ""
    )

    source = news.get(
        "source",
        ""
    )

    prompt = f"""
You are an expert SEO news writer.

Write a professional, unique and factual news article.

Category:
{category}

Source:
{source}

Original Title:
{title}

Summary:
{summary}

Content:
{content}

Requirements:

1. Write in fluent English.

2. Create an SEO optimized title.

3. Write a meta description between 150 and 160 characters.

4. Write a complete article with:

- Introduction
- Main Details
- Background if relevant
- Conclusion

5. Article length:
700-1000 words.

6. Generate exactly 10 SEO tags.

7. Create one realistic AI image prompt.

8. Return ONLY valid JSON.

JSON format:

{{
    "title": "",
    "meta_description": "",
    "article": "",
    "tags": [
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        ""
    ],
    "image_prompt": ""
}}

Do not add markdown.

Do not add explanations.

Return JSON only.
"""

    return prompt


# =================================
# Generate Article
# =================================

def generate_article(news):

    prompt = build_prompt(news)

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        text = response.text.strip()

        # Remove accidental markdown code fences
        if text.startswith("```json"):

            text = text[7:]

        elif text.startswith("```"):

            text = text[3:]

        if text.endswith("```"):

            text = text[:-3]

        text = text.strip()

        return json.loads(text)

    except Exception as e:

        print(f"Generation Error: {e}")

        return None


# =================================
# Validate Generated Article
# =================================

def validate_article(article):

    if not article:

        return False

    required_fields = [
        "title",
        "meta_description",
        "article",
        "tags",
        "image_prompt"
    ]

    for field in required_fields:

        if field not in article:

            print(f"Missing field: {field}")

            return False

    if not isinstance(
        article["tags"],
        list
    ):

        print("Tags must be a list.")

        return False

    return True


# =================================
# Build Final Article
# =================================

def build_article(news):

    generated = generate_article(news)

    if not validate_article(generated):

        return None

    return {

        "title": generated["title"],

        "meta_description":
            generated["meta_description"],

        "article":
            generated["article"],

        "tags":
            generated["tags"],

        "image_prompt":
            generated["image_prompt"],

        "category":
            news.get("category", ""),

        "priority":
            news.get("priority", ""),

        "score":
            news.get("total_score", 0),

        "source":
            news.get("source", ""),

        "link":
            news.get("link", ""),

        "published":
            news.get("published", ""),

        "created_by":
            "NovaPress AI",

        "status":
            "ready_for_publish"
    }


# =================================
# Process All Approved News
# =================================

def process_articles():

    news_list = load_news()

    if not news_list:

        print("No approved news found.")

        return []

    articles = []

    success = 0

    failed = 0

    total = len(news_list)

    print(
        f"\nProcessing {total} approved news...\n"
    )

    for index, news in enumerate(
        news_list,
        start=1
    ):

        print(
            f"[{index}/{total}] "
            f"{news.get('title', '')}"
        )

        article = build_article(news)

        if article:

            articles.append(article)

            success += 1

            print("✓ Success")

        else:

            failed += 1

            print("✗ Failed")

    print(
        "\n========== Writer Report =========="
    )

    print(
        f"Total News      : {total}"
    )

    print(
        f"Articles Created: {success}"
    )

    print(
        f"Failed          : {failed}"
    )

    return articles


# =================================
# Main
# =================================

def main():

    print(
        "\n========== NovaPress AI Writer ==========\n"
    )

    articles = process_articles()

    if not articles:

        print("No articles generated.")

        return

    save_articles(articles)

    print(
        "\n========== Completed =========="
    )

    print(
        f"Articles Saved : {len(articles)}"
    )

    print(
        f"Output File    : {OUTPUT_FILE}"
    )

    print(
        "\nWriter finished successfully."
    )


# =================================
# Run
# =================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print(
            "\nWriter stopped by user."
        )

    except Exception as e:

        print(
            f"\nUnexpected Error: {e}"
        )