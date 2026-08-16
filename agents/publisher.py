"""
NovaPress AI
Publisher Agent
Version: 2.0
"""

import json
import os
from datetime import datetime


class Publisher:
    def __init__(self):
        self.base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        self.output_dir = os.path.join(
            self.base_dir,
            "data",
            "output"
        )

        os.makedirs(self.output_dir, exist_ok=True)

        self.published_file = os.path.join(
            self.output_dir,
            "published_news.json"
        )

    def load_published(self):
        if not os.path.exists(self.published_file):
            return []

        try:
            with open(
                self.published_file,
                "r",
                encoding="utf-8"
            ) as f:
                data = json.load(f)

            return data if isinstance(data, list) else []

        except (json.JSONDecodeError, OSError):
            return []

    def save_published(self, news):
        with open(
            self.published_file,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                news,
                f,
                ensure_ascii=False,
                indent=4
            )

    def publish(self, article):
        if not isinstance(article, dict):
            return False

        title = article.get("title", "").strip()

        if not title:
            print("Publisher: Missing article title.")
            return False

        published = self.load_published()

        article_id = article.get("id")

        if article_id:
            for item in published:
                if item.get("id") == article_id:
                    print("Publisher: Article already published.")
                    return False

        article["published_by"] = "NovaPress AI"
        article["published_at"] = datetime.now().isoformat()
        article["status"] = "published"

        published.append(article)

        self.save_published(published)

        print(f"Publisher: Published -> {title}")

        return True


def publish(article):
    publisher = Publisher()
    return publisher.publish(article)


if __name__ == "__main__":
    print("NovaPress AI Publisher Agent")