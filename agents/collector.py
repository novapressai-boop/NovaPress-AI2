import os
import json
import hashlib
from datetime import datetime

import feedparser
from bs4 import BeautifulSoup


class NewsCollector:
    def __init__(self):
        self.base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        self.sources_dir = os.path.join(
            self.base_dir,
            "data",
            "sources"
        )

        self.output_dir = os.path.join(
            self.base_dir,
            "data",
            "output"
        )

        os.makedirs(self.output_dir, exist_ok=True)

        self.output_file = os.path.join(
            self.output_dir,
            "news_output.json"
        )

        self.news = []
        self.ids = set()

    def make_id(self, text):
        return hashlib.md5(
            text.encode("utf-8")
        ).hexdigest()

    def load_sources(self):
        sources = []

        if not os.path.exists(self.sources_dir):
            raise FileNotFoundError(
                f"Sources folder not found: {self.sources_dir}"
            )

        for file in os.listdir(self.sources_dir):

            if not file.endswith(".json"):
                continue

            path = os.path.join(
                self.sources_dir,
                file
            )

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

                if isinstance(data, list):
                    sources.extend(data)

        return sources
    def add_news(self, item):
        uid = self.make_id(
            item["title"] + item["link"]
        )

        if uid in self.ids:
            return

        self.ids.add(uid)
        item["id"] = uid
        self.news.append(item)

    def collect_news(self):
        sources = self.load_sources()

        print(f"Loaded {len(sources)} sources.\n")

        for source in sources:

            try:
                print(f"Collecting: {source['name']}")

                feed = feedparser.parse(
                    source["rss"]
                )

                for entry in feed.entries:

                    title = entry.get(
                        "title",
                        ""
                    ).strip()

                    link = entry.get(
                        "link",
                        ""
                    ).strip()

                    summary = BeautifulSoup(
                        entry.get(
                            "summary",
                            ""
                        ),
                        "html.parser"
                    ).get_text(strip=True)

                    news = {
                        "source": source.get("name", "Unknown"),
                        "category": source.get("category", "General"),
                        "language": source.get("language", "en"),
                        "title": title,
                        "link": link,
                        "summary": summary,
                        "published": entry.get("published", ""),
                        "collected_at": datetime.now().isoformat()
                    }

                    if title and link:
                        self.add_news(news)

            except Exception as e:
                print(f"Error collecting {source['name']}: {e}")
    def save_news(self):
        self.news.sort(
            key=lambda x: x.get("published", ""),
            reverse=True
        )

        with open(
            self.output_file,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                self.news,
                f,
                ensure_ascii=False,
                indent=4
            )

        print("\n===================================")
        print(f"Total News : {len(self.news)}")
        print(f"Saved File : {self.output_file}")
        print("===================================\n")


def collect_news():
    collector = NewsCollector()
    collector.collect_news()
    collector.save_news()


if __name__ == "__main__":
    collect_news()