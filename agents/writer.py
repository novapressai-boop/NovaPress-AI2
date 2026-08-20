import os
import json
from pathlib import Path

from google import genai
from google.genai import types


# =================================
# NovaPress AI Writer
# =================================

print("\n========== NovaPress AI Writer ==========\n")


# =================================
# Find Project Directory
# =================================

CURRENT_DIR = Path(__file__).resolve().parent

PROJECT_DIR = None

for folder in [CURRENT_DIR] + list(CURRENT_DIR.parents):

    if (folder / "data" / "output").exists():
        PROJECT_DIR = folder
        break

if PROJECT_DIR is None:
    raise RuntimeError(
        "NovaPress AI project folder could not be found."
    )


OUTPUT_DIR = PROJECT_DIR / "data" / "output"

INPUT_FILE = OUTPUT_DIR / "news_output.json"

OUTPUT_FILE = OUTPUT_DIR / "articles.json"


print("Project Directory:")
print(PROJECT_DIR)

print("\nInput File:")
print(INPUT_FILE)


# =================================
# Gemini API
# =================================

# Put your Gemini API key here for Pydroid testing.
# DO NOT upload this real key to GitHub.

API_KEY = "YOUR_GEMINI_API_KEY"


if not API_KEY or API_KEY == "YOUR_GEMINI_API_KEY":

    raise RuntimeError(
        "Gemini API key is not set."
    )


client = genai.Client(
    api_key=API_KEY
)


MODEL = "gemini-3.6-flash"


# =================================
# Load Approved News
# =================================

def load_news():

    if not INPUT_FILE.exists():

        print(
            "\nInput file not found:"
        )

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

        print(
            f"\nError loading news: {e}"
        )

        return []

    if not isinstance(news, list):

        print(
            "\nInvalid analyzed_news.json format."
        )

        return []

    approved = [

        item

        for item in news

        if item.get("approved") is True

    ]

    print(
        f"\nApproved News : {len(approved)}"
    )

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

    print(
        "\nArticles saved successfully."
    )

    print(
        f"Output File : {OUTPUT_FILE}"
    )


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
You are the professional AI news writer
for NovaPress AI.

Write a unique, factual and SEO-friendly
news article based ONLY on the supplied
news information.

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

2. Create a clear SEO optimized title.

3. Write a meta description of approximately
150-160 characters.

4. Write a complete news article.

5. Article structure should include:

Introduction
Main Details
Background when relevant
Conclusion

6. Article length:
700-1000 words.

7. Generate exactly 10 SEO tags.

8. Generate one realistic AI image prompt.

9. Do not invent facts that are not supported
by the supplied information.

10. Return JSON only.

Do not use Markdown.
Do not add explanations.
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

            contents=prompt,

            config=types.GenerateContentConfig(

                response_mime_type="application/json",

                response_schema={

                    "type": "OBJECT",

                    "properties": {

                        "title": {
                            "type": "STRING"
                        },

                        "meta_description": {
                            "type": "STRING"
                        },

                        "article": {
                            "type": "STRING"
                        },

                        "tags": {

                            "type": "ARRAY",

                            "items": {
                                "type": "STRING"
                            }

                        },

                        "image_prompt": {
                            "type": "STRING"
                        }

                    },

                    "required": [

                        "title",

                        "meta_description",

                        "article",

                        "tags",

                        "image_prompt"

                    ]

                }

            )

        )

        text = response.text.strip()

        article = json.loads(text)

        return article

    except Exception as e:

        print(
            f"\nGeneration Error: {e}"
        )

        return None


# =================================
# Validate Article
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

            print(
                f"Missing field: {field}"
            )

            return False

    if not isinstance(
        article["tags"],
        list
    ):

        print(
            "Tags must be a list."
        )

        return False

    if len(article["tags"]) != 10:

        print(
            "Article must contain exactly 10 tags."
        )

        return False

    return True


# =================================
# Build Final Article
# =================================

def build_article(news):

    generated = generate_article(
        news
    )

    if not validate_article(
        generated
    ):

        return None

    return {

        "title":
            generated["title"],

        "meta_description":
            generated["meta_description"],

        "article":
            generated["article"],

        "tags":
            generated["tags"],

        "image_prompt":
            generated["image_prompt"],

        "category":
            news.get(
                "category",
                ""
            ),

        "priority":
            news.get(
                "priority",
                ""
            ),

        "score":
            news.get(
                "total_score",
                0
            ),

        "source":
            news.get(
                "source",
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

        "created_by":
            "NovaPress AI",

        "status":
            "ready_for_publish"

    }


# =================================
# Process Articles
# =================================

def process_articles():

    news_list = load_news()

    if not news_list:

        print(
            "\nNo approved news found."
        )

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

        article = build_article(
            news
        )

        if article:

            articles.append(
                article
            )

            success += 1

            print(
                "✓ Success"
            )

        else:

            failed += 1

            print(
                "✗ Failed"
            )

    print(
        "\n========== Writer Report =========="
    )

    print(
        f"Total News       : {total}"
    )

    print(
        f"Articles Created : {success}"
    )

    print(
        f"Failed           : {failed}"
    )

    return articles


# =================================
# Main
# =================================

def main():

    articles = process_articles()

    if not articles:

        print(
            "\nNo articles generated."
        )

        return

    save_articles(
        articles
    )

    print(
        "\n========== Completed =========="
    )

    print(
        f"Articles Saved : {len(articles)}"
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